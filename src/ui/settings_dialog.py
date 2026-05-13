import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, Gio
import os
import settings



class SettingsView(Gtk.Box):
    def __init__(self, on_close_callback, on_theme_changed=None, on_show_confirm=None, on_show_toast=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        self.on_close = on_close_callback
        self.on_theme_changed = on_theme_changed
        self.on_show_confirm = on_show_confirm
        self.on_show_toast = on_show_toast
        
        self.set_margin_top(0)
        self.set_margin_bottom(0)
        self.set_margin_start(0)
        self.set_margin_end(0)

        self.pending_settings = settings.load().copy()


        autostart_path = os.path.expanduser("~/.config/autostart/klipr.desktop")
        self.autostart_initial_state = os.path.exists(autostart_path)


        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        self.append(scrolled)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox.set_margin_top(20)
        vbox.set_margin_bottom(20)
        vbox.set_margin_start(40)
        vbox.set_margin_end(40)
        scrolled.set_child(vbox)

        about_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        about_box.set_halign(Gtk.Align.FILL)

        logo_path = self._get_logo_path("logo.png")
        if logo_path:
             self.app_icon_widget = Gtk.Picture.new_for_filename(logo_path)
             self.app_icon_widget.set_size_request(48, 48)
             self.app_icon_widget.set_can_shrink(True)
        else:
             self.app_icon_widget = Gtk.Image.new_from_icon_name("klipr")
             self.app_icon_widget.set_pixel_size(48)
        self.app_icon_widget.set_valign(Gtk.Align.CENTER)
        about_box.append(self.app_icon_widget)

        about_text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        about_text_box.set_valign(Gtk.Align.CENTER)

        self.app_title = Gtk.Label()
        self.app_title.add_css_class("title-2")
        self.app_title.set_halign(Gtk.Align.START)
        about_text_box.append(self.app_title)
        
        self.app_desc = Gtk.Label()
        self.app_desc.set_halign(Gtk.Align.START)
        self.app_desc.add_css_class("dim-label")
        about_text_box.append(self.app_desc)
        
        about_box.append(about_text_box)
        vbox.append(about_box)
        vbox.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        self._add_section_header(vbox, "General")
        
        general_grid = Gtk.Grid()
        general_grid.set_column_spacing(12)
        general_grid.set_row_spacing(12)
        vbox.append(general_grid)

        limit_label = Gtk.Label(label="History Limit")
        limit_label.set_halign(Gtk.Align.START)
        general_grid.attach(limit_label, 0, 0, 1, 1)

        limit_model = Gtk.StringList()
        limit_model.append("50")
        limit_model.append("100")
        limit_model.append("150")
        
        self.limit_dropdown = Gtk.DropDown(model=limit_model)
        self.limit_dropdown.set_halign(Gtk.Align.END)
        self.limit_dropdown.set_hexpand(True)
        general_grid.attach(self.limit_dropdown, 1, 0, 1, 1)

        self._add_section_header(vbox, "Shortcuts")
        shortcut_grid = Gtk.Grid()
        shortcut_grid.set_column_spacing(12)
        shortcut_grid.set_row_spacing(12)
        vbox.append(shortcut_grid)

        shortcut_label = Gtk.Label(label="Global Toggle")
        shortcut_label.set_halign(Gtk.Align.START)
        shortcut_grid.attach(shortcut_label, 0, 0, 1, 1)

        self._shortcut_capturing = False
        self._captured_shortcut = None

        shortcut_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        shortcut_btn_box.set_halign(Gtk.Align.END)
        shortcut_btn_box.set_hexpand(True)

        self.shortcut_capture_btn = Gtk.Button()
        self.shortcut_capture_btn.set_halign(Gtk.Align.END)
        self.shortcut_capture_btn.add_css_class("shortcut-capture-btn")
        self.shortcut_capture_btn.connect("clicked", self._on_shortcut_capture_clicked)

        self.shortcut_clear_btn = Gtk.Button(icon_name="edit-clear-symbolic")
        self.shortcut_clear_btn.set_tooltip_text("Clear shortcut")
        self.shortcut_clear_btn.add_css_class("icon-btn")
        self.shortcut_clear_btn.add_css_class("shortcut-clear-btn")
        self.shortcut_clear_btn.connect("clicked", self._on_shortcut_clear_clicked)

        shortcut_btn_box.append(self.shortcut_capture_btn)
        shortcut_btn_box.append(self.shortcut_clear_btn)
        shortcut_grid.attach(shortcut_btn_box, 1, 0, 1, 1)

        shortcut_hint = Gtk.Label()
        shortcut_hint.set_markup('<span size="small" alpha="70%">Click button, then press your desired key combo.</span>')
        shortcut_hint.set_halign(Gtk.Align.START)
        shortcut_hint.set_margin_top(2)
        shortcut_grid.attach(shortcut_hint, 0, 1, 2, 1)
        
        self._add_section_header(vbox, "Behavior")
        
        behavior_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.append(behavior_box)

        self.autostart_check = Gtk.CheckButton(label="Start on login")
        if "autostart" not in self.pending_settings:
            self.pending_settings["autostart"] = self.autostart_initial_state
        behavior_box.append(self.autostart_check)

        self.close_tray_check = Gtk.CheckButton(label="Close to system tray")
        behavior_box.append(self.close_tray_check)

        self._add_section_header(vbox, "Appearance")

        theme_cards_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        theme_cards_box.set_homogeneous(True)
        vbox.append(theme_cards_box)

        self.theme_dark_btn = self._create_theme_card(
            "weather-clear-night-symbolic", "Dark"
        )
        self.theme_light_btn = self._create_theme_card(
            "weather-clear-symbolic", "Light"
        )
        self.theme_system_btn = self._create_theme_card(
            "emblem-system-symbolic", "System"
        )

        self.theme_dark_btn.connect("clicked", self._on_theme_card_clicked, "dark")
        self.theme_light_btn.connect("clicked", self._on_theme_card_clicked, "light")
        self.theme_system_btn.connect("clicked", self._on_theme_card_clicked, "system")

        theme_cards_box.append(self.theme_dark_btn)
        theme_cards_box.append(self.theme_light_btn)
        theme_cards_box.append(self.theme_system_btn)

        btn_restore = Gtk.Button(label="Restore Defaults")
        btn_restore.add_css_class("settings-restore-btn")
        btn_restore.set_halign(Gtk.Align.FILL)
        btn_restore.set_margin_top(8)
        btn_restore.connect("clicked", self._on_restore_defaults)
        vbox.append(btn_restore)

        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        action_box.set_halign(Gtk.Align.FILL)
        action_box.set_hexpand(True)
        action_box.set_margin_top(10)
        action_box.set_margin_bottom(10)
        action_box.set_margin_end(20)
        action_box.set_margin_start(20)
        spacer = Gtk.Label()
        spacer.set_hexpand(True)
        action_box.append(spacer)

        btn_cancel = Gtk.Button(label="Cancel")
        btn_cancel.connect("clicked", self._on_cancel)
        action_box.append(btn_cancel)

        btn_save = Gtk.Button(label="Save")
        btn_save.add_css_class("suggested-action")
        btn_save.connect("clicked", self._on_save)
        action_box.append(btn_save)
        
        self.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        self.append(action_box)

        self._refresh_ui()

    def _get_logo_path(self, filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(base_dir, "..", "..", "assets", filename),
            os.path.join(base_dir, "..", "assets", filename),
            os.path.join(os.getcwd(), "assets", filename),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    def _update_logo(self, theme):
        if not hasattr(self, 'app_icon_widget'):
            return
            
        # Resolve 'system'
        resolved = theme
        if theme == "system":
            resolved = "dark" # Default fallback
            
            # Check GTK prefer-dark property
            gtk_settings = Gtk.Settings.get_default()
            is_dark_gtk = gtk_settings and gtk_settings.get_property("gtk-application-prefer-dark-theme")
            
            # Check Freedesktop/GNOME color-scheme via Gio.Settings (more reliable on modern GNOME)
            is_dark_gnome = False
            try:
                gnome_settings = Gio.Settings.new("org.gnome.desktop.interface")
                color_scheme = gnome_settings.get_string("color-scheme")
                if "dark" in color_scheme.lower():
                    is_dark_gnome = True
            except Exception:
                pass

            if not is_dark_gtk and not is_dark_gnome:
                 resolved = "light"
             
        filename = "light_logo.png" if resolved == "light" else "logo.png"
        path = self._get_logo_path(filename)
        
        # Fallback
        if not path and filename != "logo.png":
            path = self._get_logo_path("logo.png")
            
        if path:
            self.app_icon_widget.set_filename(path)

    def _update_shortcut_btn_label(self, shortcut):
        """Update the shortcut capture button text."""
        if self._shortcut_capturing:
            self.shortcut_capture_btn.set_label("⌨ Press keys...")
        elif shortcut:
            self.shortcut_capture_btn.set_label(shortcut)
        else:
            self.shortcut_capture_btn.set_label("Click to set shortcut")

    def _on_shortcut_capture_clicked(self, btn):
        """Enter capture mode — listen for next key combo on the window level."""
        if self._shortcut_capturing:
            # Second click cancels
            self._shortcut_capturing = False
            if hasattr(self, '_capture_controller') and self._capture_controller:
                try:
                    toplevel = self.get_root()
                    if toplevel:
                        toplevel.remove_controller(self._capture_controller)
                except Exception:
                    pass
                self._capture_controller = None
            self._update_shortcut_btn_label(self._captured_shortcut)
            return

        self._shortcut_capturing = True
        self._update_shortcut_btn_label(None)

        # Attach controller to window (not button): window always receives all key events
        controller = Gtk.EventControllerKey()
        controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self._capture_controller = controller

        def on_key_pressed(ctrl, keyval, keycode, state):
            if not self._shortcut_capturing:
                return False

            # Ignore bare modifier-only presses (wait for actual key)
            modifier_only = {
                Gdk.KEY_Control_L, Gdk.KEY_Control_R,
                Gdk.KEY_Shift_L, Gdk.KEY_Shift_R,
                Gdk.KEY_Alt_L, Gdk.KEY_Alt_R,
                Gdk.KEY_Super_L, Gdk.KEY_Super_R,
                Gdk.KEY_Meta_L, Gdk.KEY_Meta_R,
                Gdk.KEY_Escape,
            }

            # Escape = cancel
            if keyval == Gdk.KEY_Escape:
                self._shortcut_capturing = False
                self._update_shortcut_btn_label(self._captured_shortcut)
                toplevel = self.get_root()
                if toplevel:
                    toplevel.remove_controller(ctrl)
                self._capture_controller = None
                return True

            if keyval in modifier_only:
                return True

            # Build human-readable combo: must have at least one modifier
            parts = []
            if state & Gdk.ModifierType.CONTROL_MASK:
                parts.append("Ctrl")
            if state & Gdk.ModifierType.ALT_MASK:
                parts.append("Alt")
            if state & Gdk.ModifierType.SHIFT_MASK:
                parts.append("Shift")
            if state & Gdk.ModifierType.SUPER_MASK:
                parts.append("Super")

            # If no modifiers are pressed, don't capture this key as a shortcut
            # and DON'T swallow it (let it propagate so user can still type)
            if not parts:
                return False

            key_name = Gdk.keyval_name(keyval)
            if key_name:
                if len(key_name) == 1:
                    key_name = key_name.upper()
                parts.append(key_name)

            combo = "+".join(parts)
            self._captured_shortcut = combo
            self._shortcut_capturing = False
            self._update_shortcut_btn_label(combo)

            # Remove controller from window — done capturing
            toplevel = self.get_root()
            if toplevel:
                toplevel.remove_controller(ctrl)
            self._capture_controller = None
            return True

        controller.connect("key-pressed", on_key_pressed)
        toplevel = self.get_root()
        if toplevel:
            toplevel.add_controller(controller)
        else:
            # Fallback if root not yet available
            self._shortcut_capturing = False
            self._update_shortcut_btn_label(self._captured_shortcut)
            self._capture_controller = None

    def _on_shortcut_clear_clicked(self, btn):
        """Clear the set shortcut."""
        self._captured_shortcut = ""
        self._shortcut_capturing = False
        self._update_shortcut_btn_label("")

    def _add_section_header(self, vbox, title):
        label = Gtk.Label()
        label.set_markup(f'<b>{title}</b>')
        label.set_xalign(0)
        label.set_margin_top(8)
        label.add_css_class("settings-section-label")
        vbox.append(label)

    def _create_theme_card(self, icon_name, label_text):
        card = Gtk.Button()
        card.add_css_class("theme-card")
        
        card_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        card_box.set_halign(Gtk.Align.CENTER)
        card_box.set_valign(Gtk.Align.CENTER)
        
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(24)
        card_box.append(icon)
        
        label = Gtk.Label(label=label_text)
        label.add_css_class("theme-card-label")
        card_box.append(label)
        
        card.set_child(card_box)
        return card

    def _on_theme_card_clicked(self, btn, theme_name):
        self.pending_settings["theme"] = theme_name
        self._update_theme_cards(theme_name)
        self._update_logo(theme_name)
        if self.on_theme_changed:
            self.on_theme_changed(theme_name)

    def _update_theme_cards(self, active_theme):
        for btn, name in [
            (self.theme_dark_btn, "dark"),
            (self.theme_light_btn, "light"),
            (self.theme_system_btn, "system"),
        ]:
            if name == active_theme:
                btn.add_css_class("theme-card-active")
            else:
                btn.remove_css_class("theme-card-active")

    def _refresh_ui(self):
        """Update all UI widgets to match self.pending_settings."""
        s = self.pending_settings
        
        name = s["name"]
        version = s["version"]
        self.app_title.set_label(name)

        desc = s["description"]
        self.app_desc.set_label(f"{desc}\nVersion {version}")

        limit = int(s["historyLimit"])
        limit_map = {50: 0, 100: 1, 150: 2}
        if limit not in limit_map:
            raise ValueError(f"Unsupported historyLimit value: {limit}")
        idx = limit_map[limit]
        self.limit_dropdown.set_selected(idx)
            
        self.autostart_check.set_active(s["autostart"])
        self.close_tray_check.set_active(s["closeToTray"])
        
        current_shortcut = s.get("shortcut", "Ctrl+Alt+M")
        self._captured_shortcut = current_shortcut
        self._shortcut_capturing = False
        self._update_shortcut_btn_label(current_shortcut)

        t = s["theme"]
        self._update_theme_cards(t)
        self._update_logo(t)

    def _on_restore_defaults(self, btn):
        """Reset all pending settings to factory defaults."""
        if self.on_show_confirm:
             self.on_show_confirm(
                 "Restore Defaults?",
                 "Are you sure you want to reset all settings to their default values?",
                 self._do_restore_defaults,
                 confirm_label="Restore"
             )
        else:
             self._do_restore_defaults()

    def _do_restore_defaults(self):
        self.pending_settings = settings.load_base_defaults().copy()
        self._refresh_ui()
        
        # Apply restored theme immediately
        restored_theme = self.pending_settings["theme"]
        if self.on_theme_changed:
            self.on_theme_changed(restored_theme)
            
        if self.on_show_toast:
            self.on_show_toast("Settings restored to defaults", "success")



    def reload_state(self):
        """Reload settings from disk when view is shown again (if cancelled previously)."""
        self.pending_settings = settings.load().copy()
        
        autostart_path = os.path.expanduser("~/.config/autostart/klipr.desktop")
        self.autostart_initial_state = os.path.exists(autostart_path)

        if "autostart" not in self.pending_settings:
            self.pending_settings["autostart"] = self.autostart_initial_state

        self._refresh_ui()

    def _on_cancel(self, btn):
        self.on_close(False)

    def _on_save(self, btn):
        selected_idx = self.limit_dropdown.get_selected()
        if selected_idx == 0:
            limit = 50
        elif selected_idx == 1:
            limit = 100
        else:
            limit = 150
        self.pending_settings["historyLimit"] = limit
        
        new_autostart_state = self.autostart_check.get_active()
        self.pending_settings["autostart"] = new_autostart_state

        self.pending_settings["closeToTray"] = self.close_tray_check.get_active()
        
        self.pending_settings["shortcut"] = self._captured_shortcut or ""

        # theme is already set via card clicks in pending_settings

        self._apply_autostart(new_autostart_state)

        settings.save(self.pending_settings)

        if self.on_theme_changed:
            self.on_theme_changed(self.pending_settings["theme"])


        self.on_close(True)

    def deactivate_capture(self):
        """Force-stop shortcut capture mode and remove controller from window."""
        self._shortcut_capturing = False
        if hasattr(self, '_capture_controller') and self._capture_controller:
            try:
                toplevel = self.get_root()
                if toplevel:
                    toplevel.remove_controller(self._capture_controller)
            except Exception:
                pass
            self._capture_controller = None
        self._update_shortcut_btn_label(self._captured_shortcut)

    def _apply_autostart(self, enable):
        autostart_dir = os.path.expanduser("~/.config/autostart")
        autostart_path = os.path.join(autostart_dir, "klipr.desktop")
        
        if enable and not self.autostart_initial_state:
            os.makedirs(autostart_dir, exist_ok=True)
            desktop_content = """[Desktop Entry]
Type=Application
Name=Klipr
Comment=Clipboard history manager
Exec=klipr --hidden
Icon=klipr
Terminal=false
Categories=Utility;
X-GNOME-Autostart-enabled=true
StartupNotify=true
StartupWMClass=io.github.nguyenduc2309.klipr
"""
            try:
                with open(autostart_path, 'w') as f:
                    f.write(desktop_content)
            except Exception as e:
                print(f"Failed to create autostart: {e}")
                
        elif not enable and self.autostart_initial_state:
            if os.path.exists(autostart_path):
                try:
                    os.remove(autostart_path)
                except Exception as e:
                    print(f"Failed to remove autostart: {e}")
