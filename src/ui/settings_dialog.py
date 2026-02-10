import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk
import os
import settings
from global_shortcut import parse_shortcut_label


class SettingsView(Gtk.Box):
    def __init__(self, on_close_callback, on_theme_changed=None, on_shortcut_changed=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        self.on_close = on_close_callback
        self.on_theme_changed = on_theme_changed
        self.on_shortcut_changed = on_shortcut_changed
        
        self.set_margin_top(0)
        self.set_margin_bottom(0)
        self.set_margin_start(0)
        self.set_margin_end(0)

        self.pending_settings = settings.load().copy()
        self._recording = False

        autostart_path = os.path.expanduser("~/.config/autostart/klipr.desktop")
        self.autostart_initial_state = os.path.exists(autostart_path)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header.add_css_class("header-area")
        header.append(Gtk.Label(label="Settings", css_classes=["title-1"]))
        self.append(header)

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

        about_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        about_box.set_halign(Gtk.Align.CENTER)

        logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "logo.png")
        if os.path.exists(logo_path):
             app_icon = Gtk.Picture.new_for_filename(logo_path)
             app_icon.set_size_request(64, 64)
             app_icon.set_can_shrink(True)
        else:
             app_icon = Gtk.Image.new_from_icon_name("klipr")
             app_icon.set_pixel_size(64)
        about_box.append(app_icon)
        
        self.app_title = Gtk.Label()
        self.app_title.add_css_class("title-1")
        about_box.append(self.app_title)
        
        self.app_desc = Gtk.Label()
        self.app_desc.set_justify(Gtk.Justification.CENTER)
        self.app_desc.add_css_class("dim-label")
        about_box.append(self.app_desc)
        
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

        # DISABLED: Appearance section (feature under development)
        # self._add_section_header(vbox, "Appearance")
        # 
        # appearance_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        # vbox.append(appearance_box)
        # 
        # theme_label = Gtk.Label(label="App Theme")
        # theme_label.set_halign(Gtk.Align.START)
        # appearance_box.append(theme_label)
        # 
        # theme_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        # appearance_box.append(theme_row)
        # 
        # self.theme_dark = Gtk.CheckButton(label="Dark")
        # self.theme_light = Gtk.CheckButton(label="Light")
        # self.theme_light.set_group(self.theme_dark)
        # self.theme_system = Gtk.CheckButton(label="System")
        # self.theme_system.set_group(self.theme_dark)
        # 
        # theme_row.append(self.theme_dark)
        # theme_row.append(self.theme_light)
        # theme_row.append(self.theme_system)

        # DISABLED: Shortcuts section (feature under development)
        # self._add_section_header(vbox, "Shortcuts")
        # 
        # shortcut_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        # vbox.append(shortcut_box)
        # 
        # self.shortcut_enable_check = Gtk.CheckButton(label="Enable global shortcut")
        # self.shortcut_enable_check.connect("toggled", self._on_shortcut_enable_toggled)
        # shortcut_box.append(self.shortcut_enable_check)
        # 
        # self.shortcut_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        # self.shortcut_row.set_margin_start(20)
        # shortcut_box.append(self.shortcut_row)
        # 
        # shortcut_label = Gtk.Label(label="Toggle Window:")
        # self.shortcut_row.append(shortcut_label)
        # 
        # self.shortcut_btn = Gtk.Button()
        # self.shortcut_btn.add_css_class("shortcut-btn")
        # self.shortcut_btn.set_tooltip_text("Click to record new shortcut")
        # self.shortcut_btn.connect("clicked", self._on_record_clicked)
        # self.shortcut_row.append(self.shortcut_btn)
        # 
        # key_ctrl = Gtk.EventControllerKey()
        # key_ctrl.connect("key-pressed", self._on_key_pressed)
        # self.shortcut_btn.add_controller(key_ctrl)
        # 
        # reset_btn = Gtk.Button(icon_name="edit-undo-symbolic")
        # reset_btn.add_css_class("flat")
        # reset_btn.set_tooltip_text("Reset to default (Alt+V)")
        # reset_btn.connect("clicked", self._on_reset_shortcut)
        # self.shortcut_row.append(reset_btn)

        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        action_box.set_halign(Gtk.Align.FILL)
        action_box.set_hexpand(True)
        action_box.set_margin_top(10)
        action_box.set_margin_bottom(10)
        action_box.set_margin_end(20)
        action_box.set_margin_start(20)
        
        btn_restore = Gtk.Button(label="Restore Defaults")
        btn_restore.add_css_class("destructive-action")
        btn_restore.connect("clicked", self._on_restore_defaults)
        action_box.append(btn_restore)
        
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

    def _add_section_header(self, vbox, title):
        label = Gtk.Label(label=title)
        label.set_xalign(0)
        label.add_css_class("settings-section-label")
        vbox.append(label)

    def _refresh_ui(self):
        """Update all UI widgets to match self.pending_settings."""
        s = self.pending_settings
        
        name = s.get("name", "Klipr")
        version = s.get("version", "0.2")
        self.app_title.set_label(name)

        desc = s.get("description", "Clipboard Manager")
        self.app_desc.set_label(f"{desc}\nVersion {version}")

        limit_str = str(s.get("historyLimit", 50))
        if limit_str == "100":
            self.limit_dropdown.set_selected(1)
        elif limit_str == "150":
            self.limit_dropdown.set_selected(2)
        else:
            self.limit_dropdown.set_selected(0)
            
        self.autostart_check.set_active(s.get("autostart", False))
        self.close_tray_check.set_active(s.get("closeToTray", True))

        # DISABLED: Theme and shortcut UI refresh (features under development)
        # t = s.get("theme", "dark")
        # if t == "light":
        #     self.theme_light.set_active(True)
        # elif t == "system":
        #     self.theme_system.set_active(True)
        # else:
        #     self.theme_dark.set_active(True)
        #     
        # self.shortcut_enable_check.set_active(s.get("shortcutEnabled", True))
        # self.shortcut_row.set_sensitive(s.get("shortcutEnabled", True))
        # 
        # sc = s.get("shortcut", "<Alt>v")
        # self.shortcut_btn.set_label(parse_shortcut_label(sc))

    def _on_restore_defaults(self, btn):
        """Reset all pending settings to factory defaults."""
        self.pending_settings = settings.DEFAULTS.copy()
        self._refresh_ui()

    def _on_record_clicked(self, btn):
        self._recording = True
        self.shortcut_btn.set_label("Press shortcut…")
        self.shortcut_btn.grab_focus()

    def _on_key_pressed(self, controller, keyval, keycode, state):
        if not self._recording:
            return False

        _MODIFIER_KEYVALS = {
            Gdk.KEY_Shift_L, Gdk.KEY_Shift_R,
            Gdk.KEY_Control_L, Gdk.KEY_Control_R,
            Gdk.KEY_Alt_L, Gdk.KEY_Alt_R,
            Gdk.KEY_Super_L, Gdk.KEY_Super_R,
            Gdk.KEY_Meta_L, Gdk.KEY_Meta_R,
            Gdk.KEY_ISO_Level3_Shift,
        }
        if keyval in _MODIFIER_KEYVALS:
            return True

        if keyval == Gdk.KEY_Escape:
            self._recording = False
            current = self.pending_settings.get("shortcut", "<Alt>v")
            self.shortcut_btn.set_label(parse_shortcut_label(current))
            return True

        mods = state & (
            Gdk.ModifierType.CONTROL_MASK
            | Gdk.ModifierType.SHIFT_MASK
            | Gdk.ModifierType.ALT_MASK
            | Gdk.ModifierType.SUPER_MASK
        )

        shortcut = ""
        if mods & Gdk.ModifierType.CONTROL_MASK:
            shortcut += "<Ctrl>"
        if mods & Gdk.ModifierType.SHIFT_MASK:
            shortcut += "<Shift>"
        if mods & Gdk.ModifierType.ALT_MASK:
            shortcut += "<Alt>"
        if mods & Gdk.ModifierType.SUPER_MASK:
            shortcut += "<Super>"

        key_name = Gdk.keyval_name(keyval)
        if not key_name:
            return True
            
        if len(key_name) == 1:
            key_name = key_name.lower()
            
        shortcut += key_name
        
        self.pending_settings["shortcut"] = shortcut
        self.shortcut_btn.set_label(parse_shortcut_label(shortcut))
        self._recording = False
        return True

    def _on_reset_shortcut(self, btn):
        default = "<Alt>v"
        self.pending_settings["shortcut"] = default
        self.shortcut_btn.set_label(parse_shortcut_label(default))
        self._recording = False

    def _on_shortcut_enable_toggled(self, btn):
        is_enabled = btn.get_active()
        self.pending_settings["shortcutEnabled"] = is_enabled
        self.shortcut_row.set_sensitive(is_enabled)

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

        # DISABLED: Theme and shortcut settings save (features under development)
        # if self.theme_light.get_active():
        #     self.pending_settings["theme"] = "light"
        # elif self.theme_system.get_active():
        #     self.pending_settings["theme"] = "system"
        # else:
        #     self.pending_settings["theme"] = "dark"
            
        self._apply_autostart(new_autostart_state)

        settings.save(self.pending_settings)

        # if self.on_theme_changed:
        #     self.on_theme_changed(self.pending_settings["theme"])
        #     
        # if self.on_shortcut_changed:
        #     self.on_shortcut_changed()
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
