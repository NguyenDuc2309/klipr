import sys
import os
os.environ["GDK_BACKEND"] = "x11"
import ast
import subprocess

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio

Gtk.Window.set_default_icon_name("klipr")

import settings
from database import (
    init_db, add_item, get_history, get_favorites, 
    delete_history_item, delete_favorite_item, 
    add_to_favorites, remove_from_favorites, is_favorite,
    update_favorite_name,
    clear_history, clear_favorites, get_counts
)
from clipboard_manager import ClipboardManager
from ui.window import ClipboardWindow
from tray import TrayIcon


SHORTCUT_BASE = "org.gnome.settings-daemon.plugins.media-keys"
SHORTCUT_CUSTOM_BASE = f"{SHORTCUT_BASE}.custom-keybinding"
SHORTCUT_PATH = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/klipr/"


class ClipboardApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="io.github.nguyenduc2309.klipr",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
        )
        self.window = None
        self.clipboard_manager = None
        self.tray_icon = None
        self._start_hidden = False
        self._pending_toggle = False
        self._registered_shortcut = None

        self.add_main_option(
            "hidden",
            0,
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "Start Klipr hidden (do not present the window)",
            None,
        )
        self.add_main_option(
            "toggle",
            ord("t"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "Toggle window visibility",
            None,
        )

    def do_command_line(self, command_line: Gio.ApplicationCommandLine):
        options = command_line.get_options_dict()

        is_toggle = False
        try:
            is_toggle = bool(options.contains("toggle"))
        except Exception:
            argv = command_line.get_arguments() or []
            is_toggle = "--toggle" in argv or "-t" in argv

        if is_toggle:
            if self.window:
                self._toggle_window()
            else:
                self._pending_toggle = True
                self.activate()
            return 0

        try:
            self._start_hidden = bool(options.contains("hidden"))
        except Exception:
            argv = command_line.get_arguments() or []
            self._start_hidden = "--hidden" in argv

        self.activate()
        return 0

    def do_activate(self):
        settings.load()
        self.hold()
        if self.window:
            if self._pending_toggle:
                self._pending_toggle = False
                GLib.idle_add(self._toggle_window)
            elif not self._start_hidden:
                self.window.present()
            return

        try:
            init_db()
        except Exception:
            pass

        self.clipboard_manager = ClipboardManager(self._on_clipboard_update)

        self.window = ClipboardWindow(
            self,
            self._create_db_interface(),
            self._on_user_copy,
        )

        self.tray_icon = TrayIcon(
            self,
            on_open=self._tray_open,
            on_quit=self.quit,
        )


        self._monitor_settings()

        self._setup_shortcut()

        if self._pending_toggle:
            self._pending_toggle = False
            GLib.idle_add(self._show_window)
        elif not self._start_hidden:
            self.window.present()

    def _monitor_settings(self):
        """Watch setting.json for changes and reload."""
        settings_path = settings.get_settings_file()
        if not settings_path.exists():
             return

        f = Gio.File.new_for_path(str(settings_path))
        try:
            self.settings_monitor = f.monitor_file(Gio.FileMonitorFlags.NONE, None)
            self.settings_monitor.connect("changed", self._on_settings_file_changed)
        except Exception:
            pass

    def _on_settings_file_changed(self, monitor, file, other_file, event_type):
        if event_type == Gio.FileMonitorEvent.CHANGES_DONE_HINT:
            GLib.idle_add(self._reload_settings)

    def _reload_settings(self):
        settings.reload()
        
        if self.window:
            self.window.update_from_settings()
        
        self._setup_shortcut()
        return False

    def do_shutdown(self):
        if self.tray_icon:
            self.tray_icon.shutdown()
        if hasattr(self, 'css_monitors'):
            for monitor in self.css_monitors:
                monitor.cancel()
        if hasattr(self, 'settings_monitor'):
            self.settings_monitor.cancel()
            
        Gtk.Application.do_shutdown(self)

    def _tray_open(self):
        if self.window:
            self.window.present()
        return False

    def _toggle_window(self):
        """Toggle window visibility (called by global shortcut)."""
        if not self.window:
            return False

        if self.window.get_visible():
            self.window.hide()
        else:
            self.window.set_visible(True)
            self.window.present()
        return False

    def _show_window(self):
        if self.window:
            self.window.set_visible(True)
            self.window.present()
        return False

    def _setup_shortcut(self):
        """Register global hotkey via GNOME gsettings custom keybindings.
        
        This is the only reliable method that works on both X11 and Wayland.
        It registers 'klipr --toggle' as a GNOME custom keyboard shortcut.
        """
        shortcut_str = settings.get("shortcut")
        if shortcut_str == self._registered_shortcut:
            return

        if not shortcut_str:
            self._disable_shortcut()
            self._registered_shortcut = shortcut_str
            return

        accel = self._shortcut_to_accel(shortcut_str)
        if not accel:
            return

        try:
            self._ensure_shortcut_path()
            self._set_shortcut_property("name", "Klipr Toggle")
            self._set_shortcut_property("command", "klipr --toggle")
            self._set_shortcut_property("binding", accel)
            self._registered_shortcut = shortcut_str
            print(f"Global shortcut registered via GNOME: {shortcut_str} → {accel}")
        except FileNotFoundError:
            print("Shortcut: gsettings not found; shortcut not registered (non-GNOME desktop).")
        except Exception as e:
            print(f"Shortcut setup error: {e}")

    def _shortcut_to_accel(self, shortcut_str):
        raw = shortcut_str.strip()
        parts = [p.strip() for p in raw.replace("-", "+").split("+") if p.strip()]

        accel_parts = []
        key_part = None
        for p in parts:
            pl = p.lower()
            if pl in ("ctrl", "control"):
                accel_parts.append("<Control>")
            elif pl == "shift":
                accel_parts.append("<Shift>")
            elif pl == "alt":
                accel_parts.append("<Alt>")
            elif pl in ("super", "win", "cmd"):
                accel_parts.append("<Super>")
            else:
                key_part = p.lower()

        if not key_part:
            print(f"Shortcut: no key part found in '{shortcut_str}'")
            return None

        return "".join(accel_parts) + key_part

    def _ensure_shortcut_path(self):
        result = subprocess.run(
            ["gsettings", "get", SHORTCUT_BASE, "custom-keybindings"],
            capture_output=True, text=True, timeout=3
        )
        existing_raw = result.stdout.strip()
        if existing_raw.startswith("@as"):
            existing = []
        else:
            try:
                existing = ast.literal_eval(existing_raw)
            except Exception:
                existing = []

        if SHORTCUT_PATH in existing:
            return

        existing.append(SHORTCUT_PATH)
        new_list = "[" + ", ".join(f"'{p}'" for p in existing) + "]"
        subprocess.run(
            ["gsettings", "set", SHORTCUT_BASE, "custom-keybindings", new_list],
            timeout=3
        )

    def _set_shortcut_property(self, key, value):
        subprocess.run(
            ["gsettings", "set", f"{SHORTCUT_CUSTOM_BASE}:{SHORTCUT_PATH}", key, value],
            timeout=3
        )

    def _disable_shortcut(self):
        try:
            self._set_shortcut_property("binding", "")
        except FileNotFoundError:
            print("Shortcut: gsettings not found; shortcut not registered (non-GNOME desktop).")
        except Exception as e:
            print(f"Shortcut disable error: {e}")

    def _create_db_interface(self):
        class DBInterface:
            def get_history(self, query=None):
                return get_history(query)
            def get_favorites(self, query=None):
                return get_favorites(query)
            def get_counts(self):
                return get_counts()
            def delete_history_item(self, item_id):
                delete_history_item(item_id)
            def delete_favorite_item(self, item_id):
                delete_favorite_item(item_id)
            def add_to_favorites(self, content):
                add_to_favorites(content)
            def remove_from_favorites(self, content):
                remove_from_favorites(content)
            def is_favorite(self, content):
                return is_favorite(content)
            def update_favorite_name(self, item_id, name):
                update_favorite_name(item_id, name)
            def clear_history(self):
                return clear_history()
            def clear_favorites(self):
                return clear_favorites()
        return DBInterface()

    def _on_clipboard_update(self, text):
        add_item(text)
        if self.window:
            # Preserve current search query during background refresh
            search_query = self.window.search_entry.get_text()
            GLib.idle_add(self.window.refresh_list, search_query)

    def _on_user_copy(self, content):
        self.clipboard_manager.set_content(content)


if __name__ == "__main__":
    try:
        app = ClipboardApp()
        sys.exit(app.run(sys.argv))
    except BaseException as e:
        import traceback
        with open("/tmp/klipr_crash.log", "w") as f:
            f.write(f"Type: {type(e).__name__}\n")
            f.write(f"Error: {str(e)}\n\n")
            f.write(traceback.format_exc())
            f.flush()
            os.fsync(f.fileno())
        print(f"CRASH: {e}")
        traceback.print_exc()
        sys.exit(1)
#
