import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib, Gio
import os
import settings


class SettingsDialog(Gtk.Dialog):
    def __init__(self, parent, on_theme_changed=None):
        super().__init__(
            title="Settings",
            transient_for=parent,
            modal=True,
            destroy_with_parent=True,
        )
        self.set_default_size(400, 300)
        self.on_theme_changed = on_theme_changed

        # Content area
        content = self.get_content_area()
        content.set_spacing(16)
        content.set_margin_top(16)
        content.set_margin_bottom(16)
        content.set_margin_start(16)
        content.set_margin_end(16)

        # ── Behavior Section ────────────────────────────────────────────
        behavior_label = Gtk.Label(label="Behavior")
        behavior_label.set_xalign(0)
        behavior_label.add_css_class("settings-section-label")
        content.append(behavior_label)

        behavior_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        behavior_box.set_margin_start(12)
        behavior_box.set_margin_bottom(16)

        # Close to tray
        self.close_to_tray_check = Gtk.CheckButton(label="Close to system tray")
        self.close_to_tray_check.set_active(settings.get("close_to_tray"))
        self.close_to_tray_check.connect("toggled", self._on_close_to_tray_toggled)
        behavior_box.append(self.close_to_tray_check)

        # Autostart
        self.autostart_check = Gtk.CheckButton(label="Start on login")
        autostart_path = os.path.expanduser("~/.config/autostart/klipr.desktop")
        self.autostart_check.set_active(os.path.exists(autostart_path))
        self.autostart_check.connect("toggled", self._on_autostart_toggled)
        behavior_box.append(self.autostart_check)

        content.append(behavior_box)

        # ── Appearance Section ──────────────────────────────────────────
        appearance_label = Gtk.Label(label="Appearance")
        appearance_label.set_xalign(0)
        appearance_label.add_css_class("settings-section-label")
        content.append(appearance_label)

        appearance_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        appearance_box.set_margin_start(12)

        # Theme radio buttons
        theme_label = Gtk.Label(label="Theme:")
        theme_label.set_xalign(0)
        appearance_box.append(theme_label)

        theme_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        theme_box.set_margin_start(12)

        current_theme = settings.get("theme")
        self.theme_dark = Gtk.CheckButton(label="Dark")
        self.theme_dark.set_group(None)
        self.theme_light = Gtk.CheckButton(label="Light")
        self.theme_light.set_group(self.theme_dark)
        self.theme_system = Gtk.CheckButton(label="System")
        self.theme_system.set_group(self.theme_dark)

        if current_theme == "dark":
            self.theme_dark.set_active(True)
        elif current_theme == "light":
            self.theme_light.set_active(True)
        else:
            self.theme_system.set_active(True)

        self.theme_dark.connect("toggled", lambda b: self._on_theme_changed("dark") if b.get_active() else None)
        self.theme_light.connect("toggled", lambda b: self._on_theme_changed("light") if b.get_active() else None)
        self.theme_system.connect("toggled", lambda b: self._on_theme_changed("system") if b.get_active() else None)

        theme_box.append(self.theme_dark)
        theme_box.append(self.theme_light)
        theme_box.append(self.theme_system)
        appearance_box.append(theme_box)

        content.append(appearance_box)

        # ── Close Button ────────────────────────────────────────────────
        self.add_button("Close", Gtk.ResponseType.CLOSE)
        self.set_default_response(Gtk.ResponseType.CLOSE)

    def _on_close_to_tray_toggled(self, btn):
        """Handle close to tray toggle."""
        settings.set("close_to_tray", btn.get_active())

    def _on_autostart_toggled(self, btn):
        """Handle autostart toggle: create or remove autostart desktop file."""
        autostart_dir = os.path.expanduser("~/.config/autostart")
        autostart_path = os.path.join(autostart_dir, "klipr.desktop")

        if btn.get_active():
            # Enable autostart: create desktop file
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
            with open(autostart_path, 'w') as f:
                f.write(desktop_content)
        else:
            # Disable autostart: remove desktop file
            if os.path.exists(autostart_path):
                os.remove(autostart_path)

        settings.set("autostart", btn.get_active())

    def _on_theme_changed(self, theme):
        """Handle theme change."""
        settings.set("theme", theme)
        if self.on_theme_changed:
            self.on_theme_changed(theme)

