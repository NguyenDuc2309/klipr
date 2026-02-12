import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio
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
        
        btn_cancel = Gtk.Button(label="Cancel")
        btn_cancel.connect("clicked", self._on_cancel)
        action_box.append(btn_cancel)
        
        spacer = Gtk.Label()
        spacer.set_hexpand(True)
        action_box.append(spacer)
        
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

        # theme is already set via card clicks in pending_settings

        self._apply_autostart(new_autostart_state)

        settings.save(self.pending_settings)

        if self.on_theme_changed:
            self.on_theme_changed(self.pending_settings["theme"])


        self.on_close(True)

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
