"""Keyboard navigation test — run: xvfb-run -a python3 tests/test_keyboard.py

Drives a real ClipboardWindow with synthetic key events and asserts the
resulting state. Exits non-zero on any failure so it can gate a release.
"""
import os, sys, tempfile
# Modules from the checkout by default; CI sets KLIPR_SRC=/usr/share/klipr.
SRC = os.environ.get("KLIPR_SRC", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
sandbox = tempfile.mkdtemp(prefix="kbtest-")
os.environ["HOME"] = sandbox
os.environ["GDK_BACKEND"] = "x11"
sys.path.insert(0, SRC)
os.chdir(sandbox)

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib

import database
database.init_db()
for i in range(5):
    database.add_item(f"entry-{i}")

from ui.window import ClipboardWindow

class DB:
    def get_history(self, q=None): return database.get_history(q)
    def get_favorites(self, q=None): return database.get_favorites(q)
    def get_counts(self): return database.get_counts()
    def is_favorite(self, c): return database.is_favorite(c)
    def add_to_favorites(self, c): database.add_to_favorites(c)
    def remove_from_favorites(self, c): database.remove_from_favorites(c)
    def delete_history_item(self, i): database.delete_history_item(i)
    def delete_favorite_item(self, i): database.delete_favorite_item(i)
    def update_favorite_name(self, i, n): database.update_favorite_name(i, n)
    def clear_history(self): return database.clear_history()
    def clear_favorites(self): return database.clear_favorites()

copied = []
app = Gtk.Application(application_id="io.test.klipr.kb")
results = []

def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")

def on_activate(a):
    win = ClipboardWindow(a, DB(), lambda c: copied.append(c))
    win.present()

    def run():
        kb = win._on_key_pressed
        CTRL = Gdk.ModifierType.CONTROL_MASK

        # 1. Ctrl+F opens search and focuses the entry
        check("Ctrl+F opens search",
              kb(None, Gdk.KEY_f, 0, CTRL) and win.btn_search.get_active()
              and win.search_revealer.get_reveal_child())

        # 2. Ctrl+F again closes it
        kb(None, Gdk.KEY_f, 0, CTRL)
        check("Ctrl+F toggles closed", not win.btn_search.get_active())

        # 3. Escape with search open closes search, not the window
        win.btn_search.set_active(True)
        kb(None, Gdk.KEY_Escape, 0, 0)
        check("Esc closes search only", not win.btn_search.get_active())

        print("\n" + ("ALL PASS" if all(r[1] for r in results)
                      else "FAILURES: " + ", ".join(n for n, ok, _ in results if not ok)))
        a.quit()
        return False

    GLib.timeout_add(400, run)

app.connect("activate", on_activate)
app.run([])
sys.exit(0 if all(r[1] for r in results) else 1)
