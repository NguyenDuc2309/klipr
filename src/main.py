import sys
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio

import settings
from database import (
    init_db, add_item, get_history, get_favorites, 
    delete_history_item, delete_favorite_item, 
    add_to_favorites, remove_from_favorites, is_favorite,
    clear_history, clear_favorites, get_counts
)
from clipboard_manager import ClipboardManager
from ui.window import ClipboardWindow
from tray import TrayIcon
from global_shortcut import GlobalShortcut


class ClipboardApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="dev.klipr.app",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
        )
        self.window = None
        self.clipboard_manager = None
        self.tray_icon = None
        self.global_shortcut = None
        self._start_hidden = False

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
            self._toggle_window()
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
            on_shortcut_changed=self.on_shortcut_changed,
        )

        self.tray_icon = TrayIcon(
            self,
            on_open=self._tray_open,
            on_quit=self.quit,
        )

        self._setup_global_shortcut()

        self._monitor_css()
        self._monitor_settings()

        if not self._start_hidden:
            self.window.present()

    def _monitor_css(self):
        """Watch style.css for changes and reload (dev mode only)."""
        import os
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        css_files = ["style.css"]  # Only dark mode for now
        self.css_monitors = []
        
        for css in css_files:
            path = os.path.join(base_path, css)
            f = Gio.File.new_for_path(path)
            try:
                monitor = f.monitor_file(Gio.FileMonitorFlags.NONE, None)
                monitor.connect("changed", self._on_style_changed)
                self.css_monitors.append(monitor)
            except Exception:
                pass

    def _on_style_changed(self, monitor, file, other_file, event_type):
        if event_type == Gio.FileMonitorEvent.CHANGES_DONE_HINT:
            GLib.idle_add(self.window.load_css)

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
        
        self.on_shortcut_changed()
        return False

    def do_shutdown(self):
        """Clean up tray and shortcut resources on app shutdown."""
        if self.global_shortcut:
            self.global_shortcut.unbind()
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

    def _setup_global_shortcut(self):
        """Register global keyboard shortcut from settings."""
        if not settings.get("shortcutEnabled"):
            return

        shortcut = settings.get("shortcut")
        if not shortcut:
            return

        self.global_shortcut = GlobalShortcut(self._toggle_window)

        if GlobalShortcut.is_available():
            if not self.global_shortcut.bind(shortcut):
                print("Global shortcut: failed to bind (key may be in use)")
        else:
            print("Global shortcut: X11 not available")

    def on_shortcut_changed(self):
        """Re-register global shortcut after settings change."""
        if self.global_shortcut:
            self.global_shortcut.unbind()
            self.global_shortcut = None

        self._setup_global_shortcut()

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
            def clear_history(self):
                return clear_history()
            def clear_favorites(self):
                return clear_favorites()
        return DBInterface()

    def _on_clipboard_update(self, text):
        add_item(text)
        if self.window:
            GLib.idle_add(self.window.refresh_list)

    def _on_user_copy(self, content):
        self.clipboard_manager.set_content(content)


if __name__ == "__main__":
    app = ClipboardApp()
    sys.exit(app.run(sys.argv))
