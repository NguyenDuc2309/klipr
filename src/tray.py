"""
Tray icon service launcher.

AppIndicator3 requires GTK3, but our app uses GTK4.
GTK3 and GTK4 CANNOT coexist in the same process.
Solution: launch tray as a separate subprocess (tray_service.py).
"""

import subprocess
import sys
import os
import signal


class TrayIcon:
    """Launches tray icon as a separate subprocess."""

    def __init__(self, app):
        self.app = app
        self._process = None
        self._available = False

        try:
            tray_script = os.path.join(os.path.dirname(__file__), "tray_service.py")
            if not os.path.exists(tray_script):
                return

            env = os.environ.copy()
            env["KLIPR_PID"] = str(os.getpid())
            env["KLIPR_APP_ID"] = app.get_application_id()

            self._process = subprocess.Popen(
                [sys.executable, tray_script],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self._available = True

        except Exception as e:
            print(f"Failed to start tray service: {e}")
            self._process = None

    def is_available(self):
        """Check if tray subprocess is running."""
        if self._process is None:
            return False
        # Check if still alive
        return self._process.poll() is None

    def shutdown(self):
        """Terminate tray subprocess."""
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()
