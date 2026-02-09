import re

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib, Gio
import os
import settings
from global_shortcut import parse_shortcut_label


class SettingsDialog(Gtk.Dialog):
    def __init__(self, parent, on_theme_changed=None, on_shortcut_changed=None):
        super().__init__(
            title="Settings",
            transient_for=parent,
            modal=True,
            destroy_with_parent=True,
        )
        self.set_default_size(400, -1)
        self.on_theme_changed = on_theme_changed
        self.on_shortcut_changed = on_shortcut_changed

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

        # ── Keyboard Shortcut Section ──────────────────────────────────
        shortcut_label = Gtk.Label(label="Keyboard Shortcut")
        shortcut_label.set_xalign(0)
        shortcut_label.add_css_class("settings-section-label")
        content.append(shortcut_label)

        shortcut_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        shortcut_box.set_margin_start(12)
        shortcut_box.set_margin_bottom(16)

        # Enable / disable shortcut
        self.shortcut_enabled_check = Gtk.CheckButton(label="Enable global shortcut")
        self.shortcut_enabled_check.set_active(settings.get("shortcut_enabled"))
        self.shortcut_enabled_check.connect("toggled", self._on_shortcut_enabled_toggled)
        shortcut_box.append(self.shortcut_enabled_check)

        # Shortcut recorder row
        shortcut_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        shortcut_row.set_margin_start(12)

        shortcut_hint = Gtk.Label(label="Shortcut:")
        shortcut_hint.set_xalign(0)
        shortcut_row.append(shortcut_hint)

        self._recording = False
        current_shortcut = settings.get("shortcut") or "<Ctrl><Shift>v"
        self.shortcut_button = Gtk.Button(label=parse_shortcut_label(current_shortcut))
        self.shortcut_button.set_tooltip_text("Click to record a new shortcut")
        self.shortcut_button.add_css_class("shortcut-btn")
        self.shortcut_button.connect("clicked", self._on_shortcut_record_clicked)

        # Key event controller for recording shortcut
        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.connect("key-pressed", self._on_shortcut_key_pressed)
        self.shortcut_button.add_controller(key_ctrl)

        shortcut_row.append(self.shortcut_button)

        # Reset button
        btn_reset = Gtk.Button(icon_name="edit-undo-symbolic")
        btn_reset.set_tooltip_text("Reset to default (Ctrl + Shift + V)")
        btn_reset.add_css_class("flat")
        btn_reset.connect("clicked", self._on_shortcut_reset)
        shortcut_row.append(btn_reset)

        shortcut_box.append(shortcut_row)

        # Sensitivity based on enabled state
        shortcut_row.set_sensitive(self.shortcut_enabled_check.get_active())
        self._shortcut_row = shortcut_row

        content.append(shortcut_box)

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

    # ── Shortcut handlers ──────────────────────────────────────────

    def _on_shortcut_enabled_toggled(self, btn):
        """Handle shortcut enable/disable toggle."""
        enabled = btn.get_active()
        settings.set("shortcut_enabled", enabled)
        self._shortcut_row.set_sensitive(enabled)
        if self._recording:
            self._recording = False
            current = settings.get("shortcut") or "<Ctrl><Shift>v"
            self.shortcut_button.set_label(parse_shortcut_label(current))
        if self.on_shortcut_changed:
            self.on_shortcut_changed()

    def _on_shortcut_record_clicked(self, btn):
        """Enter recording mode: next key combo will be captured."""
        self._recording = True
        self.shortcut_button.set_label("Press shortcut…")
        self.shortcut_button.grab_focus()

    def _on_shortcut_key_pressed(self, controller, keyval, keycode, state):
        """Capture key combo while in recording mode."""
        if not self._recording:
            return False

        # Ignore lone modifier keys
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

        # Escape cancels recording
        if keyval == Gdk.KEY_Escape:
            self._recording = False
            current = settings.get("shortcut") or "<Ctrl><Shift>v"
            self.shortcut_button.set_label(parse_shortcut_label(current))
            return True

        # Build shortcut string from modifiers + key
        mods = state & (
            Gdk.ModifierType.CONTROL_MASK
            | Gdk.ModifierType.SHIFT_MASK
            | Gdk.ModifierType.ALT_MASK
            | Gdk.ModifierType.SUPER_MASK
        )

        # Require at least one modifier
        if not mods:
            return True

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

        # Normalize single-char keys to lowercase (Shift is explicit modifier)
        if len(key_name) == 1:
            key_name = key_name.lower()

        shortcut += key_name

        # Save and notify
        self._recording = False
        self.shortcut_button.set_label(parse_shortcut_label(shortcut))
        settings.set("shortcut", shortcut)
        if self.on_shortcut_changed:
            self.on_shortcut_changed()

        return True

    def _on_shortcut_reset(self, btn):
        """Reset shortcut to default."""
        default = "<Ctrl><Shift>v"
        settings.set("shortcut", default)
        self.shortcut_button.set_label(parse_shortcut_label(default))
        if self._recording:
            self._recording = False
        if self.on_shortcut_changed:
            self.on_shortcut_changed()

    # ── Theme handlers ──────────────────────────────────────────────

    def _on_theme_changed(self, theme):
        """Handle theme change."""
        settings.set("theme", theme)
        if self.on_theme_changed:
            self.on_theme_changed(theme)

