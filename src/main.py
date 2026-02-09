import sys
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio

import settings
from database import init_db, add_item, get_items, delete_item, toggle_pin, clear_unpinned, clear_favorites, get_counts
from clipboard_manager import ClipboardManager
from ui.window import ClipboardWindow
from tray import TrayIcon


class ClipboardApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="dev.klipr.app",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.window = None
        self.clipboard_manager = None
        self.tray_icon = None

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

        self.window = ClipboardWindow(self, self._create_db_interface(), self._on_user_copy)

        # Launch tray icon as a separate subprocess (GTK3 cannot coexist with GTK4)
        self.tray_icon = TrayIcon(self)

        # Check for --hidden flag (for autostart)
        if '--hidden' not in sys.argv:
            self.window.present()

    def do_shutdown(self):
        """Clean up tray subprocess on app shutdown."""
        if self.tray_icon:
            self.tray_icon.shutdown()
        Gtk.Application.do_shutdown(self)

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
