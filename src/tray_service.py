#!/usr/bin/env python3
"""
Tray icon service — runs as a SEPARATE process.
Uses GTK3 + AyatanaAppIndicator3 (cannot coexist with GTK4 in same process).

Communication with main app:
  - "Open Klipr": activates existing GApplication via D-Bus (single-instance)
  - "Quit":       sends SIGTERM to parent process
"""

import os
import signal
import subprocess
import sys

import gi

gi.require_version("Gtk", "3.0")

try:
    gi.require_version("AyatanaAppIndicator3", "0.1")
    from gi.repository import AyatanaAppIndicator3 as AppIndicator3
except (ImportError, ValueError):
    # AppIndicator3 not installed — exit silently
    sys.exit(0)

from gi.repository import Gtk


def activate_app(app_id):
    """Activate the main GApplication via D-Bus to show the window."""
    obj_path = "/" + app_id.replace(".", "/")
    try:
        subprocess.Popen(
            [
                "gdbus", "call", "--session",
                "--dest", app_id,
                "--object-path", obj_path,
                "--method", "org.gtk.Application.Activate",
                "[]",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def quit_app(parent_pid):
    """Send SIGTERM to the main app process."""
    try:
        os.kill(parent_pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    Gtk.main_quit()


def main():
    parent_pid = int(os.environ.get("KLIPR_PID", os.getppid()))
    app_id = os.environ.get("KLIPR_APP_ID", "dev.klipr.app")

    # Watch parent — if it dies, we die too
    def check_parent():
        try:
            os.kill(parent_pid, 0)  # check if alive (signal 0 = no-op)
            return True  # keep calling
        except ProcessLookupError:
            Gtk.main_quit()
            return False

    from gi.repository import GLib
    GLib.timeout_add_seconds(2, check_parent)

    # Create indicator
    indicator = AppIndicator3.Indicator.new(
        "klipr",
        "edit-paste-symbolic",
        AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
    )

    # Menu
    menu = Gtk.Menu()

    open_item = Gtk.MenuItem(label="Open Klipr")
    open_item.connect("activate", lambda _: activate_app(app_id))
    menu.append(open_item)

    separator = Gtk.SeparatorMenuItem()
    menu.append(separator)

    quit_item = Gtk.MenuItem(label="Quit")
    quit_item.connect("activate", lambda _: quit_app(parent_pid))
    menu.append(quit_item)

    menu.show_all()
    indicator.set_menu(menu)
    indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

    Gtk.main()


if __name__ == "__main__":
    main()

