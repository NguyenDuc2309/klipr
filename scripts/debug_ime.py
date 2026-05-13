
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib

class IMETestWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="IME Event Debugger")
        self.set_default_size(500, 400)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(20)
        vbox.set_margin_bottom(20)
        vbox.set_margin_start(20)
        vbox.set_margin_end(20)
        self.set_child(vbox)

        # List all signals for debugging
        from gi.repository import GObject
        print("Signals for Gtk.Entry:")
        for s in sorted(GObject.signal_list_names(Gtk.Entry)):
            print(f"  {s}")

        label = Gtk.Label(label="Type with Vietnamese IME and press Enter:")
        vbox.append(label)

        self.entry = Gtk.Entry()
        vbox.append(self.entry)

        # Get the internal IMContext if possible (GTK4 entries use one internally)
        # Note: GtkEntry doesn't expose its IMContext easily in Python without 
        # subclassing or trickery, but we can monitor the 'changed' signal 
        # which is the result of 'commit'.

        # Connect to standard signals
        self.entry.connect("changed", self._on_changed)
        self.entry.connect("activate", self._on_activate)

        # Key Event Controller
        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.connect("key-pressed", self._on_key_pressed)
        key_ctrl.connect("im-update", self._on_im_update)
        self.entry.add_controller(key_ctrl)

        # Log area
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        scrolled.set_child(self.log_view)
        vbox.append(scrolled)

        self._log("Debug session started. Propagation: BUBBLE")

    def _log(self, msg):
        buffer = self.log_view.get_buffer()
        iter = buffer.get_end_iter()
        buffer.insert(iter, msg + "\n")
        # Auto scroll
        adj = self.log_view.get_parent().get_vadjustment()
        adj.set_value(adj.get_upper())

    def _on_im_update(self, ctrl):
        self._log("[Signal] im-update: IME is intercepting keys")

    def _on_changed(self, entry):
        self._log(f"[Signal] changed: '{entry.get_text()}'")

    def _on_activate(self, entry):
        self._log(f"[Signal] activate (Enter pressed): '{entry.get_text()}'")

    def _on_key_pressed(self, ctrl, keyval, keycode, state):
        key_name = Gdk.keyval_name(keyval)
        self._log(f"[Event] key-pressed: {key_name} (val: {keyval})")
        
        # This mirrors the logic in window.py
        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            self._log("  >> Match Enter key - Returning True (Swallowing)")
            return True
        return False

class TestApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="dev.klipr.imetest")
    def do_activate(self):
        self.win = IMETestWindow(self)
        self.win.present()

if __name__ == "__main__":
    app = TestApp()
    app.run(None)
