"""
Global keyboard shortcut registration via X11 (XGrabKey).

Uses python-xlib to grab a key combination on the root window so the
shortcut works system-wide, even when the app window is hidden.
Falls back gracefully when X11 is not available (pure Wayland).

Architecture follows xbindkeys:
  1. XSelectInput(root, KeyPressMask)
  2. XGrabKey(root, keycode, modmask, ...)
  3. Loop: XNextEvent → dispatch
"""

import os
import re
import select
import threading

from gi.repository import GLib

try:
    from Xlib import X, XK, display as xdisplay
    HAS_XLIB = True
except ImportError:
    HAS_XLIB = False


# Modifier name → X11 mask
_MOD_MAP = {
    "ctrl": X.ControlMask if HAS_XLIB else 0,
    "control": X.ControlMask if HAS_XLIB else 0,
    "shift": X.ShiftMask if HAS_XLIB else 0,
    "alt": X.Mod1Mask if HAS_XLIB else 0,
    "super": X.Mod4Mask if HAS_XLIB else 0,
}

# Extra modifier combinations to handle NumLock / CapsLock
_LOCK_COMBOS = (0,)
if HAS_XLIB:
    _LOCK_COMBOS = (
        0,
        X.LockMask,
        X.Mod2Mask,
        X.LockMask | X.Mod2Mask,
    )


def parse_shortcut_label(shortcut_str):
    """Convert '<Super>v' → 'Super + V' for display."""
    parts = re.findall(r"<(\w+)>|(\w+)", shortcut_str)
    tokens = []
    for mod, key in parts:
        if mod:
            tokens.append(mod)
        elif key:
            tokens.append(key.upper() if len(key) == 1 else key)
    return " + ".join(tokens)


class GlobalShortcut:
    """Register / unregister a single global keyboard shortcut via X11."""

    def __init__(self, callback):
        self._callback = callback
        self._display = None
        self._root = None
        self._thread = None
        self._running = False
        self._keycode = None
        self._modmask = 0
        self._stop_r = -1
        self._stop_w = -1

    # ── public API ───────────────────────────────────────────────────

    @staticmethod
    def is_available():
        if not HAS_XLIB:
            return False
        try:
            d = xdisplay.Display()
            d.close()
            return True
        except Exception:
            return False

    def bind(self, shortcut_str):
        """Parse *shortcut_str* and register the global hotkey.
        Returns True on success, False on failure.
        """
        if not HAS_XLIB:
            print("Global shortcut: python-xlib not installed")
            return False

        self.unbind()

        # Open a DEDICATED X connection (separate from GTK's)
        try:
            self._display = xdisplay.Display()
            self._root = self._display.screen().root
        except Exception as e:
            print(f"Global shortcut: cannot open X display – {e}")
            return False

        keycode, modmask = self._parse(shortcut_str)
        if keycode is None:
            print(f"Global shortcut: failed to parse '{shortcut_str}'")
            self._close_display()
            return False

        self._keycode = keycode
        self._modmask = modmask

        # Step 1: Select KeyPress events on root (like xbindkeys)
        self._root.change_attributes(event_mask=X.KeyPressMask)

        # Step 2: Grab key on root window (with NumLock/CapsLock variants)
        # Use custom error handler to detect BadAccess (key already grabbed)
        grab_errors = []

        def _on_error(err, _req):
            grab_errors.append(err)

        self._display.set_error_handler(_on_error)

        for extra in _LOCK_COMBOS:
            self._root.grab_key(
                keycode,
                modmask | extra,
                False,               # owner_events (like xbindkeys)
                X.GrabModeAsync,
                X.GrabModeAsync,
            )

        self._display.sync()

        # Reset to default error handler
        self._display.set_error_handler(None)

        if grab_errors:
            label = parse_shortcut_label(shortcut_str)
            print(f"Global shortcut: {label} is already in use by another app")
            self._close_display()
            return False

        # Self-pipe for clean shutdown
        self._stop_r, self._stop_w = os.pipe()

        # Step 3: Start event listener thread
        self._running = True
        self._thread = threading.Thread(
            target=self._event_loop, daemon=True, name="global-shortcut"
        )
        self._thread.start()

        label = parse_shortcut_label(shortcut_str)
        print(f"Global shortcut: registered {label} (keycode={keycode}, mod=0x{modmask:x})")
        return True

    def unbind(self):
        """Unregister the current shortcut (safe to call multiple times)."""
        self._running = False

        # Wake up the listener thread via self-pipe
        if self._stop_w >= 0:
            try:
                os.write(self._stop_w, b"x")
            except OSError:
                pass

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self._thread = None

        # Ungrab key
        if self._root and self._keycode is not None:
            try:
                for extra in _LOCK_COMBOS:
                    self._root.ungrab_key(self._keycode, self._modmask | extra)
                self._display.sync()
            except Exception:
                pass
            print("Global shortcut: unregistered")

        self._keycode = None
        self._modmask = 0
        self._close_display()
        self._close_pipe()

    # ── internal ─────────────────────────────────────────────────────

    def _close_display(self):
        if self._display:
            try:
                self._display.close()
            except Exception:
                pass
            self._display = None
            self._root = None

    def _close_pipe(self):
        for attr in ("_stop_r", "_stop_w"):
            fd = getattr(self, attr, -1)
            if fd >= 0:
                try:
                    os.close(fd)
                except OSError:
                    pass
                setattr(self, attr, -1)

    def _parse(self, shortcut_str):
        """Parse '<Super>v' → (keycode, modifier_mask) or (None, 0)."""
        parts = re.findall(r"<(\w+)>|(\w+)", shortcut_str)

        modmask = 0
        key_name = None

        for mod, key in parts:
            if mod:
                m = _MOD_MAP.get(mod.lower())
                if m is not None:
                    modmask |= m
            elif key:
                key_name = key

        if key_name is None:
            return None, 0

        # Resolve keysym → keycode
        keysym = XK.string_to_keysym(key_name)
        if keysym == 0:
            keysym = XK.string_to_keysym(key_name.lower())
        if keysym == 0:
            keysym = XK.string_to_keysym(key_name.upper())
        if keysym == 0:
            print(f"Global shortcut: unknown key '{key_name}'")
            return None, 0

        keycode = self._display.keysym_to_keycode(keysym)
        if keycode == 0:
            print(f"Global shortcut: no keycode for keysym 0x{keysym:x}")
            return None, 0

        return keycode, modmask

    def _event_loop(self):
        """Background thread: read X11 events via select + next_event.

        KEY: Use next_event() directly after select() confirms data on fd.
        Do NOT use pending_events() — it only checks the internal buffer
        which is empty until next_event() reads from the socket.
        """
        fd = self._display.fileno()

        while self._running:
            try:
                readable, _, _ = select.select(
                    [fd, self._stop_r], [], [], 2.0
                )
            except (ValueError, OSError):
                break

            if not self._running:
                break

            if self._stop_r in readable:
                break

            if fd in readable:
                try:
                    # next_event() reads from socket — works after select()
                    event = self._display.next_event()

                    if event.type == X.KeyPress:
                        # Verify keycode matches (ignore stray events)
                        if event.detail == self._keycode:
                            GLib.idle_add(self._callback)
                except Exception:
                    if self._running:
                        continue
                    break
