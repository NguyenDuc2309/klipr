import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, Pango, GLib, Gio
import os
import utils
import settings
from ui.settings_dialog import SettingsDialog


class ClipboardWindow(Gtk.ApplicationWindow):
    def __init__(self, app, db_interface, on_copy, on_shortcut_changed=None):
        super().__init__(application=app, title="Klipr")
        self.set_default_size(420, 600)

        self.db = db_interface
        self.on_copy_callback = on_copy
        self.on_shortcut_changed = on_shortcut_changed
        self._toast_timeout_id = None

        # CSS
        self.css_provider = Gtk.CssProvider()
        self._load_css()
        self._setup_css_monitor()

        # Main overlay (allows toast to float on top of content)
        overlay = Gtk.Overlay()
        self.set_child(overlay)

        # Main content
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        overlay.set_child(vbox)

        # ── Header ──────────────────────────────────────────────────
        header_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        header_area.add_css_class("header-area")
        vbox.append(header_area)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_property("placeholder-text", "Search clipboard history...")
        self.search_entry.connect('search-changed', self._on_search_changed)
        header_area.append(self.search_entry)

        header_right = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        header_right.add_css_class("header-right")
        header_area.append(header_right)

        self.active_filter = "all"

        self.btn_all = Gtk.ToggleButton(label="All")
        self.btn_all.set_active(True)
        self.btn_all.add_css_class("tab")
        self.btn_all.connect('toggled', lambda b: self._on_filter_toggled("all"))
        header_right.append(self.btn_all)

        self.btn_fav = Gtk.ToggleButton(label="Favorites")
        self.btn_fav.add_css_class("tab")
        self.btn_fav.set_group(self.btn_all)
        self.btn_fav.connect('toggled', lambda b: self._on_filter_toggled("favorites"))
        header_right.append(self.btn_fav)

        spacer = Gtk.Label()
        spacer.set_hexpand(True)
        header_right.append(spacer)

        btn_delete_all = Gtk.Button(icon_name="user-trash-symbolic")
        btn_delete_all.set_tooltip_text("Delete all history")
        btn_delete_all.add_css_class("header-btn")
        btn_delete_all.connect('clicked', self._on_clear_clicked)
        header_right.append(btn_delete_all)

        btn_settings = Gtk.Button(icon_name="open-menu-symbolic")
        btn_settings.set_tooltip_text("Settings")
        btn_settings.add_css_class("header-btn")
        btn_settings.connect('clicked', self._on_settings_clicked)
        header_right.append(btn_settings)

        # ── Scrolled list ───────────────────────────────────────────
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        vbox.append(scrolled)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.listbox.set_margin_top(6)
        self.listbox.set_margin_bottom(6)
        self.listbox.connect("row-activated", self._on_row_activated)
        scrolled.set_child(self.listbox)

        # ── Toast notification (floating overlay) ───────────────────
        self.toast_revealer = Gtk.Revealer()
        self.toast_revealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
        self.toast_revealer.set_transition_duration(200)
        self.toast_revealer.set_halign(Gtk.Align.CENTER)
        self.toast_revealer.set_valign(Gtk.Align.END)
        self.toast_revealer.set_margin_bottom(16)

        self.toast_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.toast_box.add_css_class("toast")

        self.toast_icon = Gtk.Image()
        self.toast_icon.set_pixel_size(16)
        self.toast_box.append(self.toast_icon)

        self.toast_label = Gtk.Label()
        self.toast_box.append(self.toast_label)

        self.toast_revealer.set_child(self.toast_box)
        overlay.add_overlay(self.toast_revealer)

        # Load initial data
        self.refresh_list()

        # Close-to-background: hide window instead of destroying
        self.connect('close-request', self._on_close_request)

    # ── CSS ─────────────────────────────────────────────────────────

    def _load_css(self):
        """Load CSS based on current theme setting."""
        self._apply_theme()

    def _setup_css_monitor(self):
        css_path = os.path.join(os.path.dirname(__file__), "..", "style.css")
        file = Gio.File.new_for_path(css_path)
        self._css_monitor = file.monitor_file(Gio.FileMonitorFlags.NONE, None)
        self._css_monitor.connect("changed", self._on_css_changed)

    def _on_css_changed(self, monitor, file, other_file, event_type):
        if event_type == Gio.FileMonitorEvent.CHANGES_DONE_HINT:
            GLib.idle_add(self._load_css)

    # ── Toast ───────────────────────────────────────────────────────

    def show_toast(self, message, toast_type="success"):
        """Show a brief notification at the bottom of the window.

        toast_type: "success" (green), "info" (blue), "warning" (amber)
        """
        if self._toast_timeout_id:
            GLib.source_remove(self._toast_timeout_id)
            self._toast_timeout_id = None

        # Icon per type
        icons = {
            "success": "object-select-symbolic",
            "info": "dialog-information-symbolic",
            "warning": "dialog-warning-symbolic",
        }
        self.toast_icon.set_from_icon_name(
            icons.get(toast_type, "dialog-information-symbolic")
        )

        # CSS class per type
        for cls in ("toast-success", "toast-info", "toast-warning"):
            self.toast_box.remove_css_class(cls)
        self.toast_box.add_css_class(f"toast-{toast_type}")

        self.toast_label.set_label(message)
        self.toast_revealer.set_reveal_child(True)
        self._toast_timeout_id = GLib.timeout_add(2000, self._hide_toast)

    def _hide_toast(self):
        self.toast_revealer.set_reveal_child(False)
        self._toast_timeout_id = None
        return False  # Don't repeat

    # ── Confirm Dialog ──────────────────────────────────────────────

    def _show_confirm(self, title, message, on_confirm):
        """Show a confirmation dialog before destructive actions."""
        try:
            dialog = Gtk.AlertDialog()
            dialog.set_message(title)
            dialog.set_detail(message)
            dialog.set_buttons(["Cancel", "Delete"])
            dialog.set_cancel_button(0)
            dialog.set_default_button(0)

            def on_response(source, result):
                try:
                    choice = source.choose_finish(result)
                    if choice == 1:  # "Delete" button
                        on_confirm()
                except GLib.Error:
                    pass  # Dialog dismissed / cancelled

            dialog.choose(self, None, on_response)
        except AttributeError:
            # Fallback for GTK < 4.10 — confirm directly
            on_confirm()

    # ── Data & List ─────────────────────────────────────────────────

    def refresh_list(self, search_query=None):
        total, favs = self.db.get_counts()
        self.btn_all.set_label(f"All {total}")
        self.btn_fav.set_label(f"Favorites {favs}")

        child = self.listbox.get_first_child()
        while child:
            self.listbox.remove(child)
            child = self.listbox.get_first_child()

        filter_pinned = True if self.active_filter == "favorites" else None
        items = self.db.get_items(search_query, filter_pinned)
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
        total, favs = self.db.get_counts()

        if self.active_filter == "favorites":
            # Favorites tab → delete all favorites
            if favs == 0:
                self.show_toast("Nothing to delete", "info")
                return
            item_word = "favorite" if favs == 1 else "favorites"
            self._show_confirm(
                "Delete all favorites?",
                f"{favs} {item_word} will be permanently deleted.",
                self._do_clear_favorites,
            )
        else:
            # All tab → delete unpinned only, keep favorites
            unpinned = total - favs
            if unpinned == 0:
                self.show_toast("Nothing to delete", "info")
                return
            item_word = "item" if unpinned == 1 else "items"
            self._show_confirm(
                "Delete all history?",
                f"{unpinned} {item_word} will be permanently deleted. "
                "Favorites will be kept.",
                self._do_clear_unpinned,
            )

    def _do_clear_unpinned(self):
        count = self.db.clear_unpinned()
        item_word = "item" if count == 1 else "items"
        self.show_toast(f"Deleted {count} {item_word}", "success")
        self.refresh_list(self.search_entry.get_text())

    def _do_clear_favorites(self):
        count = self.db.clear_favorites()
        item_word = "favorite" if count == 1 else "favorites"
        self.show_toast(f"Deleted {count} {item_word}", "success")
        self.refresh_list(self.search_entry.get_text())

    def _on_copy_clicked(self, content):
        self.on_copy_callback(content)
        self.show_toast("Copied to clipboard", "success")

    def _on_pin_clicked(self, item_id):
        is_pinned = self.db.toggle_pin(item_id)
        if is_pinned:
            self.show_toast("Added to favorites", "success")
        else:
            self.show_toast("Removed from favorites", "info")
        self.refresh_list(self.search_entry.get_text())

    def _on_delete_clicked(self, item_id):
        self.db.delete_item(item_id)
        self.show_toast("Deleted", "success")
        self.refresh_list(self.search_entry.get_text())

    def _on_row_activated(self, listbox, row):
        if not hasattr(row, 'item_data'):
            return
        _, content, _, _ = row.item_data
        self._on_copy_clicked(content)

    def _on_close_request(self, window):
        """Handle window close based on settings.

        close_to_tray ON + tray available → hide window, app stays alive
        close_to_tray ON + no tray        → still hide (re-open via desktop entry)
        close_to_tray OFF                 → quit the application
        """
        if settings.get("close_to_tray"):
            self.hide()
            return True  # Prevent default destroy
        else:
            self.get_application().quit()
            return False

    def _on_settings_clicked(self, btn):
        """Open settings dialog."""
        dialog = SettingsDialog(
            self,
            on_theme_changed=self._on_theme_changed,
            on_shortcut_changed=self.on_shortcut_changed,
        )
        dialog.connect("response", self._on_settings_response)
        dialog.present()

    def _on_settings_response(self, dialog, response):
        dialog.destroy()

    def _on_theme_changed(self, theme):
        """Handle theme change from settings dialog."""
        self._apply_theme(theme)

    def _apply_theme(self, theme=None):
        """Apply theme by loading appropriate CSS."""
        if theme is None:
            theme = settings.get("theme")

        display = Gdk.Display.get_default()

        # Always remove first to avoid stacking
        try:
            Gtk.StyleContext.remove_provider_for_display(display, self.css_provider)
        except Exception:
            pass

        if theme == "light":
            css_file = "style_light.css"
        elif theme == "system":
            # Detect system dark/light via org.gnome.desktop.interface
            css_file = self._detect_system_theme()
        else:  # dark or default
            css_file = "style.css"

        try:
            css_path = os.path.join(os.path.dirname(__file__), "..", css_file)
            self.css_provider.load_from_path(css_path)
            Gtk.StyleContext.add_provider_for_display(
                display, self.css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_USER,
            )
        except Exception as e:
            print(f"Error loading theme CSS: {e}")

    def _detect_system_theme(self):
        """Detect system color scheme preference. Returns CSS filename."""
        try:
            schema = Gio.Settings.new("org.gnome.desktop.interface")
            color_scheme = schema.get_string("color-scheme")
            # Values: "default", "prefer-dark", "prefer-light"
            if "dark" in color_scheme:
                return "style.css"
            else:
                return "style_light.css"
        except Exception:
            pass

        # Fallback: check GTK theme name
        try:
            gtk_settings = Gtk.Settings.get_default()
            theme_name = gtk_settings.get_property("gtk-theme-name") or ""
            if "dark" in theme_name.lower():
                return "style.css"
            else:
                return "style_light.css"
        except Exception:
            return "style.css"

    # ── Row Builder ─────────────────────────────────────────────────

    def _create_row(self, item):
        item_id, content, is_pinned, timestamp = item

        row = Gtk.ListBoxRow()
        row.item_data = item
        row.set_selectable(False)
        row.set_activatable(True)
        row.set_css_classes([])  # Remove 'activatable' class to kill GTK hover
        # Remove GTK's 'activatable' CSS class to kill its built-in hover effect
        row.set_css_classes([])

        item_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        item_box.add_css_class("clipboard-item")

        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        item_box.append(top_row)

        # Content: image or text
        if content.startswith("IMAGE::"):
            image_path = content.replace("IMAGE::", "")
            if os.path.exists(image_path):
                try:
                    texture = Gdk.Texture.new_from_filename(image_path)
                    picture = Gtk.Picture.new_for_paintable(texture)
                    picture.set_can_shrink(True)
                    picture.add_css_class("content-image")

                    # Scale height proportionally to container width,
                    # cap at 250px — don't force a fixed min-height
                    # so small images stay at their natural size.
                    nat_w = texture.get_width()
                    nat_h = texture.get_height()
                    avail_w = 370  # approx available width after margins
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
                    print(f"Error loading image: {e}")
                    top_row.append(Gtk.Label(label="[Image Error]"))
            else:
                lbl = Gtk.Label(label="[Image Missing]")
                lbl.add_css_class("clipboard-item-text")
                top_row.append(lbl)
        else:
            display_text = content[:300]
            if len(content) > 300:
                display_text += "..."

            lbl_content = Gtk.Label(label=display_text)
            lbl_content.set_xalign(0)
            lbl_content.set_wrap(True)
            lbl_content.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
            lbl_content.set_lines(5)
            lbl_content.add_css_class("clipboard-item-text")
            lbl_content.set_hexpand(True)
            top_row.append(lbl_content)

        # Action buttons
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
        btn_fav.set_tooltip_text("Favorite")
        if is_pinned:
            btn_fav.add_css_class("active")
        btn_fav.connect('clicked', lambda b: self._on_pin_clicked(item_id))
        actions.append(btn_fav)

        btn_del = Gtk.Button(icon_name="user-trash-symbolic")
        btn_del.add_css_class("icon-btn")
        btn_del.add_css_class("delete")
        btn_del.set_tooltip_text("Delete")
        btn_del.connect('clicked', lambda b: self._on_delete_clicked(item_id))
        actions.append(btn_del)

        # Meta row
        meta_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        meta_row.add_css_class("clipboard-item-meta")
        item_box.append(meta_row)

        lbl_time = Gtk.Label(label=utils.format_time(timestamp))
        meta_row.append(lbl_time)

        meta_spacer = Gtk.Label()
        meta_spacer.set_hexpand(True)
        meta_row.append(meta_spacer)

        if not content.startswith("IMAGE::"):
            lbl_len = Gtk.Label(label=f"{len(content)} chars")
            meta_row.append(lbl_len)

        row.set_child(item_box)
        return row
