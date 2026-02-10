import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, Pango, GLib
import os
import utils
import settings



class ClipboardWindow(Gtk.ApplicationWindow):
    def __init__(self, app, db_interface, on_copy, on_shortcut_changed=None):
        super().__init__(application=app, title="Klipr - Clipboard Manager")
        self.set_default_size(420, 600)

        self.db = db_interface
        self.on_copy_callback = on_copy
        self.on_shortcut_changed = on_shortcut_changed
        self._toast_timeout_id = None

        # CSS
        self.css_provider = Gtk.CssProvider()
        self.load_css()
        self._setup_css_monitor()

        # Main overlay (allows toast to float on top of content)
        overlay = Gtk.Overlay()
        self.set_child(overlay)

        # ── Stack (Root Container) ──────────────────────────────────────
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        overlay.set_child(self.stack)

        # ── Page 1: Main View ───────────────────────────────────────────
        self.main_view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.stack.add_named(self.main_view, "main")

        # Header Area
        header_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        header_area.add_css_class("header-area")
        self.main_view.append(header_area)

        # ── Row 1: Title bar ─────────────────────────────────────────
        title_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        title_row.add_css_class("title-row")
        header_area.append(title_row)

        app_name = settings.get("name") or "Klipr"
        self.title_label = Gtk.Label(label=app_name)
        self.title_label.set_xalign(0)
        self.title_label.add_css_class("app-title")
        self.title_label.set_hexpand(True)
        title_row.append(self.title_label)

        # DISABLED: Theme toggle button (feature under development)
        # self.btn_theme = Gtk.Button(icon_name="weather-clear-night-symbolic")
        # self.btn_theme.set_tooltip_text("Toggle theme")
        # self.btn_theme.add_css_class("header-btn")
        # self.btn_theme.connect('clicked', self._on_theme_toggle_clicked)
        # title_row.append(self.btn_theme)

        btn_settings = Gtk.Button(icon_name="emblem-system-symbolic")
        btn_settings.set_tooltip_text("Settings")
        btn_settings.add_css_class("header-btn")
        btn_settings.connect('clicked', self._on_settings_clicked)
        title_row.append(btn_settings)

        # ── Row 2: Tabs + Delete ─────────────────────────────────────
        tab_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        tab_row.add_css_class("tab-row")
        header_area.append(tab_row)

        self.active_filter = "all"

        # Tab group (segmented control)
        tab_group = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        tab_group.add_css_class("tab-group")
        tab_row.append(tab_group)

        self.btn_all = Gtk.ToggleButton(label="History")
        self.btn_all.set_active(True)
        self.btn_all.add_css_class("tab")
        self.btn_all.add_css_class("tab-first")
        self.btn_all.connect('toggled', lambda b: self._on_filter_toggled("all"))
        tab_group.append(self.btn_all)

        self.btn_fav = Gtk.ToggleButton(label="Favourite")
        self.btn_fav.add_css_class("tab")
        self.btn_fav.add_css_class("tab-last")
        self.btn_fav.set_group(self.btn_all)
        self.btn_fav.connect('toggled', lambda b: self._on_filter_toggled("favorites"))
        tab_group.append(self.btn_fav)

        tab_spacer = Gtk.Label()
        tab_spacer.set_hexpand(True)
        tab_row.append(tab_spacer)

        self.btn_delete_all = Gtk.Button(icon_name="user-trash-symbolic")
        self.btn_delete_all.set_tooltip_text("Delete History")
        self.btn_delete_all.add_css_class("header-btn")
        self.btn_delete_all.connect('clicked', self._on_clear_clicked)
        tab_row.append(self.btn_delete_all)

        # ── Row 3: Search ────────────────────────────────────────────
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_property("placeholder-text", "Search clipboard...")
        self.search_entry.connect('search-changed', self._on_search_changed)
        header_area.append(self.search_entry)

        # List
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.main_view.append(scrolled)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.listbox.set_margin_top(6)
        self.listbox.set_margin_bottom(6)
        self.listbox.connect("row-activated", self._on_row_activated)
        scrolled.set_child(self.listbox)

        from ui.settings_dialog import SettingsView
        self.settings_view = SettingsView(
            on_close_callback=self._on_settings_closed,
            on_theme_changed=None,  # DISABLED: Theme feature removed
            on_shortcut_changed=None  # DISABLED: Shortcut feature removed
        )
        self.stack.add_named(self.settings_view, "settings")

        # ── Toast notification (floating overlay) ───────────────────────
        self.toast_revealer = Gtk.Revealer()
        self.toast_revealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
        self.toast_revealer.set_transition_duration(200)
        self.toast_revealer.set_halign(Gtk.Align.CENTER)
        self.toast_revealer.set_valign(Gtk.Align.END)
        self.toast_revealer.set_margin_bottom(16)
        self.toast_revealer.set_can_target(False)

        self.toast_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.toast_box.add_css_class("toast")
        self.toast_box.set_can_target(False)

        self.toast_icon = Gtk.Image()
        self.toast_icon.set_pixel_size(16)
        self.toast_box.append(self.toast_icon)

        self.toast_label = Gtk.Label()
        self.toast_box.append(self.toast_label)

        self.toast_revealer.set_child(self.toast_box)
        overlay.add_overlay(self.toast_revealer)

        # Set correct theme icon on startup
        self._update_theme_icon()

        # Load initial data
        self.refresh_list()

        # Close-to-background: hide window instead of destroying
        self.connect('close-request', self._on_close_request)

    # ── CSS ─────────────────────────────────────────────────────────

    def load_css(self):
        """Load CSS based on current theme setting."""
        self._apply_theme()
        print("CSS Reloaded")
        return False

    def _setup_css_monitor(self):
        pass

    # ── Settings Update ─────────────────────────────────────────────
    
    def update_from_settings(self):
        """Called when settings file changes on disk."""
        # Update Title if name changed
        app_name = settings.get("name") or "Klipr"
        self.set_title(f"{app_name} - Clipboard Manager")
        
        # Reload settings view if open
        if self.settings_view:
             self.settings_view.reload_state()
             
        # Re-apply theme in case it changed
        self.load_css()
        print(f"UI Updated from Settings: {app_name}")

    # ── Toast ───────────────────────────────────────────────────────

    def show_toast(self, message, toast_type="success"):
        """Show a brief notification at the bottom of the window."""
        if self._toast_timeout_id:
            GLib.source_remove(self._toast_timeout_id)
            self._toast_timeout_id = None

        icons = {
            "success": "object-select-symbolic",
            "info": "dialog-information-symbolic",
            "warning": "dialog-warning-symbolic",
        }
        self.toast_icon.set_from_icon_name(
            icons.get(toast_type, "dialog-information-symbolic")
        )

        for cls in ("toast-success", "toast-info", "toast-warning"):
            self.toast_box.remove_css_class(cls)
        self.toast_box.add_css_class(f"toast-{toast_type}")

        self.toast_label.set_label(message)
        self.toast_revealer.set_reveal_child(True)
        self._toast_timeout_id = GLib.timeout_add(2000, self._hide_toast)

    def _hide_toast(self):
        self.toast_revealer.set_reveal_child(False)
        self._toast_timeout_id = None
        return False

    # ── Confirm Dialog ──────────────────────────────────────────────

    def _show_confirm(self, title, message, on_confirm):
        """Show a simple confirmation dialog before destructive actions."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.NONE,
            text=title,
            secondary_text=message,
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Delete", Gtk.ResponseType.OK)

        def on_response(_dialog, response_id):
            _dialog.destroy()
            if response_id == Gtk.ResponseType.OK:
                on_confirm()

        dialog.connect("response", on_response)
        dialog.present()

    # ── Data & List ─────────────────────────────────────────────────

    def refresh_list(self, search_query=None):
        hist_count, fav_count = self.db.get_counts()
        self.btn_all.set_label(f"History ({hist_count})" if hist_count else "History")
        self.btn_fav.set_label(f"Favourite ({fav_count})" if fav_count else "Favourite")
        
        if self.active_filter == "favorites":
             self.btn_delete_all.set_tooltip_text("Delete All Favorites")
             self.btn_delete_all.set_sensitive(fav_count > 0)
        else:
             self.btn_delete_all.set_tooltip_text("Delete All History")
             self.btn_delete_all.set_sensitive(hist_count > 0)

        child = self.listbox.get_first_child()
        while child:
            self.listbox.remove(child)
            child = self.listbox.get_first_child()

        items = []
        if self.active_filter == "favorites":
            items = self.db.get_favorites(search_query)
        else:
            items = self.db.get_history(search_query)

        for item in items:
            self.listbox.append(self._create_row(item))

    # ── Event Handlers ──────────────────────────────────────────────

    def _on_filter_toggled(self, filter_name):
        is_active = (
            (filter_name == "all" and self.btn_all.get_active()) or
            (filter_name == "favorites" and self.btn_fav.get_active())
        )
        if is_active:
            self.active_filter = filter_name
            self.refresh_list(self.search_entry.get_text())

    def _on_search_changed(self, entry):
        self.refresh_list(entry.get_text())

    def _on_clear_clicked(self, btn):
        if self.active_filter == "favorites":
            self._show_confirm(
                "Delete all favorites?",
                "All items in the Favorites list will be permanently deleted.",
                self._do_clear_favorites,
            )
        else:
            self._show_confirm(
                "Delete all history?",
                "All items in the History list will be permanently deleted.\nFavorites will be SAFE.",
                self._do_clear_history,
            )

    def _do_clear_history(self):
        count = self.db.clear_history()
        item_word = "item" if count == 1 else "items"
        self.show_toast(f"Deleted {count} history {item_word}", "success")
        self.refresh_list(self.search_entry.get_text())

    def _do_clear_favorites(self):
        count = self.db.clear_favorites()
        item_word = "favorite" if count == 1 else "favorites"
        self.show_toast(f"Deleted {count} {item_word}", "success")
        self.refresh_list(self.search_entry.get_text())

    def _on_copy_clicked(self, content):
        self.on_copy_callback(content)
        self.show_toast("Copied to clipboard", "success")

    def _on_pin_clicked(self, row, item_id, content):
        """Toggle favorite status."""
        if self.active_filter == "favorites":
            self.db.remove_from_favorites(content)
            self.show_toast("Removed from favorites", "info")
            self.refresh_list(self.search_entry.get_text())
        else:
            if self.db.is_favorite(content):
                self.db.remove_from_favorites(content)
                self.show_toast("Removed from favorites", "info")
                row.set_fav_active(False)
            else:
                self.db.add_to_favorites(content)
                self.show_toast("Added to favorites", "success")
                row.set_fav_active(True)
            self.refresh_list(self.search_entry.get_text())

    def _on_delete_clicked(self, item_id):
        if self.active_filter == "favorites":
            self.db.delete_favorite_item(item_id)
        else:
            self.db.delete_history_item(item_id)
        self.show_toast("Deleted", "success")
        self.refresh_list(self.search_entry.get_text())

    def _on_row_activated(self, listbox, row):
        if not hasattr(row, 'item_data'):
            return
        _, content, _ = row.item_data
        self._on_copy_clicked(content)

    def _on_close_request(self, window):
        if settings.get("closeToTray"):
            self.hide()
            return True
        else:
            self.get_application().quit()
            return False

    # ── Settings Navigation ─────────────────────────────────────────

    def _on_theme_toggle_clicked(self, btn):
        """Quick toggle between dark and light theme."""
        current = settings.get("theme")
        new_theme = "light" if current != "light" else "dark"
        settings.set("theme", new_theme)
        self._apply_theme(new_theme)
        self._update_theme_icon(new_theme)

    def _update_theme_icon(self, theme=None):
        """Update the theme toggle button icon to reflect current theme."""
        if not hasattr(self, 'btn_theme'):
            return  # Button disabled
        if theme is None:
            theme = settings.get("theme")
        if theme == "light":
            self.btn_theme.set_icon_name("weather-clear-symbolic")
            self.btn_theme.set_tooltip_text("Switch to dark mode")
        else:
            self.btn_theme.set_icon_name("weather-clear-night-symbolic")
            self.btn_theme.set_tooltip_text("Switch to light mode")

    def _on_settings_clicked(self, btn):
        self.settings_view.reload_state()
        self.stack.set_visible_child_name("settings")

    def _on_settings_closed(self, saved):
        self.stack.set_visible_child_name("main")
        self._update_theme_icon()
        if saved:
            self.show_toast("Settings saved", "success")

    def _on_theme_changed(self, theme):
        self._apply_theme(theme)

    def _apply_theme(self, theme=None):
        if theme is None:
            theme = settings.get("theme")

        display = Gdk.Display.get_default()
        try:
            Gtk.StyleContext.remove_provider_for_display(display, self.css_provider)
        except Exception:
            pass

        css_file = "style_light.css" if theme == "light" else "style.css"

        try:
            css_path = os.path.join(os.path.dirname(__file__), "..", css_file)
            self.css_provider.load_from_path(css_path)
            Gtk.StyleContext.add_provider_for_display(
                display, self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER,
            )
        except Exception as e:
            print(f"Error loading CSS: {e}")

    # ── Row Builder ─────────────────────────────────────────────────

    def _create_row(self, item):
        item_id, content, timestamp = item
        
        is_pinned = True
        if self.active_filter == "all":
            is_pinned = self.db.is_favorite(content)

        row = Gtk.ListBoxRow()
        row.item_data = item
        row.set_selectable(False)
        row.set_activatable(True)
        row.set_css_classes([])

        item_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        item_box.add_css_class("clipboard-item")

        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        item_box.append(top_row)

        if content.startswith("IMAGE::"):
            image_path = content.replace("IMAGE::", "")
            if os.path.exists(image_path):
                try:
                    texture = Gdk.Texture.new_from_filename(image_path)
                    picture = Gtk.Picture.new_for_paintable(texture)
                    picture.set_can_shrink(True)
                    picture.add_css_class("content-image")
                    
                    nat_w = texture.get_width()
                    nat_h = texture.get_height()
                    avail_w = 370
                    if nat_w > avail_w:
                        display_h = min(int(nat_h * avail_w / nat_w), 250)
                    else:
                        display_h = min(nat_h, 250)
                    picture.set_size_request(-1, display_h)

                    img_box = Gtk.Box()
                    img_box.set_hexpand(True)
                    img_box.append(picture)
                    top_row.append(img_box)
                except Exception as e:
                    top_row.append(Gtk.Label(label="[Image Error]"))
            else:
                top_row.append(Gtk.Label(label="[Image Missing]", css_classes=["clipboard-item-text"]))
        else:
            display_text = content[:300] + ("..." if len(content) > 300 else "")
            lbl = Gtk.Label(label=display_text)
            lbl.set_xalign(0)
            lbl.set_wrap(True)
            lbl.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
            lbl.set_lines(5)
            lbl.add_css_class("clipboard-item-text")
            lbl.set_hexpand(True)
            top_row.append(lbl)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        actions.add_css_class("actions")
        actions.set_valign(Gtk.Align.START)
        top_row.append(actions)

        btn_copy = Gtk.Button(icon_name="edit-copy-symbolic")
        btn_copy.add_css_class("icon-btn")
        btn_copy.add_css_class("copy")
        btn_copy.set_tooltip_text("Copy")
        btn_copy.connect('clicked', lambda b: self._on_copy_clicked(content))
        actions.append(btn_copy)

        btn_fav = Gtk.Button(icon_name="emblem-favorite-symbolic")
        btn_fav.add_css_class("icon-btn")
        btn_fav.add_css_class("fav")
        btn_fav.set_tooltip_text("Add to Favorites")
        if is_pinned:
            btn_fav.add_css_class("active")
            btn_fav.set_tooltip_text("Remove from Favorites")
        
        def set_fav_active(active):
            if active:
                btn_fav.add_css_class("active")
                btn_fav.set_tooltip_text("Remove from Favorites")
            else:
                btn_fav.remove_css_class("active")
                btn_fav.set_tooltip_text("Add to Favorites")
        row.set_fav_active = set_fav_active

        btn_fav.connect('clicked', lambda b: self._on_pin_clicked(row, item_id, content))
        actions.append(btn_fav)

        btn_del = Gtk.Button(icon_name="user-trash-symbolic")
        btn_del.add_css_class("icon-btn")
        btn_del.add_css_class("delete")
        btn_del.set_tooltip_text("Delete")
        btn_del.connect('clicked', lambda b: self._on_delete_clicked(item_id))
        actions.append(btn_del)

        meta_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        meta_row.add_css_class("clipboard-item-meta")
        item_box.append(meta_row)

        meta_row.append(Gtk.Label(label=utils.format_time(timestamp)))
        meta_row.append(Gtk.Label(hexpand=True))
        if not content.startswith("IMAGE::"):
            meta_row.append(Gtk.Label(label=f"{len(content)} chars"))

        row.set_child(item_box)
        return row
