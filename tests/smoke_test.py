import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
import sys
import os

# Modules come from the checkout by default; CI points KLIPR_SRC at the
# installed package (/usr/share/klipr) to test what the .deb actually ships.
sys.path.insert(0, os.environ.get('KLIPR_SRC', os.path.join(os.getcwd(), 'src')))

import settings
from database import init_db

passed = False

def smoke_test():
    print("Starting smoke test...")
    try:
        # 1. Initialize settings and DB
        settings.load()
        init_db()
        print("Settings and DB initialized.")

        # 2. Try to import UI components
        from ui.window import ClipboardWindow
        from ui.settings_dialog import SettingsView
        print("UI components imported.")

        # 3. Create a dummy app to satisfy Gtk.ApplicationWindow
        app = Gtk.Application(application_id="dev.klipr.smoke_test")
        
        def on_activate(app):
            print("Creating main window...")
            try:
                # Mock DB interface
                class MockDB:
                    def get_counts(self): return (0, 0)
                    def get_history(self, q): return []
                    def get_favorites(self, q): return []
                    def clear_history(self): return 0
                    def clear_favorites(self): return 0
                
                win = ClipboardWindow(app, MockDB(), lambda x: None)
                print("Main window created successfully.")
                
                print("Checking for common widgets...")
                if hasattr(win, 'search_entry'):
                    print("✓ search_entry found")
                    # Try a method that failed before
                    if hasattr(win.search_entry, 'set_placeholder_text'):
                        win.search_entry.set_placeholder_text("Test")
                        print("✓ set_placeholder_text works")
                
                global passed
                passed = True
                print("Smoke test PASSED.")
                app.quit()
            except Exception as e:
                print(f"FAILED during window creation: {e}")
                import traceback
                traceback.print_exc()
                app.quit()

        app.connect('activate', on_activate)
        # Run for a short time or just enough to trigger activate
        GLib.timeout_add(100, lambda: app.activate())
        app.run([])
        # Exceptions inside GTK callbacks don't propagate, so check the flag.
        if not passed:
            print("Smoke test FAILED: window was never created successfully.")
            sys.exit(1)

    except Exception as e:
        print(f"Smoke test FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    smoke_test()
