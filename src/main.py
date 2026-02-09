import sys
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio

import settings
from database import init_db, add_item, get_items, delete_item, toggle_pin, clear_unpinned, clear_favorites, get_counts
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

        # Custom CLI option: --hidden (used by autostart)
        # Without this, GTK rejects unknown options before do_activate() runs.
        self.add_main_option(
            "hidden",
            0,
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "Start Klipr hidden (do not present the window)",
            None,
        )

    def do_command_line(self, command_line: Gio.ApplicationCommandLine):
        options = command_line.get_options_dict()
        try:
            self._start_hidden = bool(options.contains("hidden"))
        except Exception:
            argv = command_line.get_arguments() or []
            self._start_hidden = "--hidden" in argv

        self.activate()
        return 0

    def do_activate(self):
        # Load settings
        settings.load()

        # Hold the application so it stays alive even when window is hidden
        self.hold()

        # If window already exists (from previous activation), just show it
        if self.window:
            self.window.present()
            return

        try:
            init_db()
        except Exception as e:
            print(f"DB Error: {e}")

        self.clipboard_manager = ClipboardManager(self._on_clipboard_update)

        self.window = ClipboardWindow(
            self,
            self._create_db_interface(),
            self._on_user_copy,
            on_shortcut_changed=self._on_shortcut_changed,
        )

        # Tray icon (SNI + DBusMenu via Gio.DBus — no AppIndicator, no GTK3)
        self.tray_icon = TrayIcon(
            self,
            on_open=self._tray_open,
            on_quit=self.quit,
        )
        if self.tray_icon.is_available():
            print("Tray: registered with StatusNotifierWatcher")
        else:
            print("Tray: host not available (no StatusNotifierWatcher on this desktop)")

        # Global keyboard shortcut
        self._setup_global_shortcut()

        # Check for --hidden flag (for autostart)
        if not self._start_hidden:
            self.window.present()

    def do_shutdown(self):
        """Clean up tray and shortcut resources on app shutdown."""
        if self.global_shortcut:
            self.global_shortcut.unbind()
        if self.tray_icon:
            self.tray_icon.shutdown()
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
            # Force the window to pop up immediately
            self.window.set_visible(True)
            self.window.present()
        return False  # for GLib.idle_add

    def _setup_global_shortcut(self):
        """Register global keyboard shortcut from settings."""
        if not settings.get("shortcut_enabled"):
            return

        shortcut = settings.get("shortcut")
        if not shortcut:
            return

        self.global_shortcut = GlobalShortcut(self._toggle_window)

        if GlobalShortcut.is_available():
            if self.global_shortcut.bind(shortcut):
                pass  # success message printed by GlobalShortcut
            else:
                print("Global shortcut: failed to bind (key may be in use)")
        else:
            print("Global shortcut: X11 not available")

    def _on_shortcut_changed(self):
        """Re-register global shortcut after settings change."""
        # Unbind current shortcut
        if self.global_shortcut:
            self.global_shortcut.unbind()
            self.global_shortcut = None

        # Re-setup with new settings
        self._setup_global_shortcut()

    def _create_db_interface(self):
        class DBInterface:
            def get_items(self, query=None, filter_pinned=None):
                return get_items(query, filter_pinned)
            def get_counts(self):
                return get_counts()
            def delete_item(self, item_id):
                delete_item(item_id)
            def toggle_pin(self, item_id):
                return toggle_pin(item_id)
            def clear_unpinned(self):
                return clear_unpinned()
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
