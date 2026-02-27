import gi
gi.require_version('Gdk', '4.0')
from gi.repository import Gdk, GLib
import os
import time
import hashlib

class ClipboardManager:
    def __init__(self, on_update_callback):
        self.callback = on_update_callback
        self.display = Gdk.Display.get_default()
        self.clipboard = self.display.get_clipboard()
        self.clipboard.connect('changed', self.on_changed)
        self.last_content = None
        self._setting_clipboard = False
        self._debounce_id = None
        # Keep references to prevent garbage collection while clipboard is active
        self._current_provider = None
        self._current_bytes = None

    def on_changed(self, clipboard):
        if self._setting_clipboard:
            return

        if self._debounce_id:
            GLib.source_remove(self._debounce_id)
        self._debounce_id = GLib.timeout_add(100, self._do_read_clipboard)

    def _do_read_clipboard(self):
        self._debounce_id = None
        formats = self.clipboard.get_formats()
        if formats.contain_gtype(Gdk.Texture):
            self.clipboard.read_texture_async(None, self.on_read_image_finish, self.clipboard)
        else:
            self.clipboard.read_text_async(None, self.on_read_text_finish, self.clipboard)
        return False  # Don't repeat the timeout

    def on_read_image_finish(self, clipboard, result, user_data):
        try:
            texture = clipboard.read_texture_finish(result)
            if texture:
                cache_dir = os.path.expanduser("~/.cache/klipr/images")
                os.makedirs(cache_dir, exist_ok=True)

                temp_filename = f"temp_{int(time.time()*1000)}.png"
                temp_path = os.path.join(cache_dir, temp_filename)
                texture.save_to_png(temp_path)

                from PIL import Image
                try:
                    with Image.open(temp_path) as img:
                        file_hash = hashlib.md5(img.tobytes()).hexdigest()
                except Exception as e:
                    print(f"Error hashing image: {e}")
                    with open(temp_path, "rb") as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()

                final_filename = f"img_{file_hash}.png"
                final_path = os.path.join(cache_dir, final_filename)

                if os.path.exists(final_path):
                    os.remove(temp_path)
                else:
                    os.rename(temp_path, final_path)

                content_str = f"IMAGE::{final_path}"
                if content_str != self.last_content:
                    self.last_content = content_str
                    GLib.idle_add(self.callback, content_str)
        except Exception as e:
            print(f"Error reading image: {e}")

    def on_read_text_finish(self, clipboard, result, user_data):
        try:
            text = clipboard.read_text_finish(result)
            if text and text != self.last_content:
                self.last_content = text
                self.callback(text)
        except GLib.Error:
            pass

    def set_content(self, content):
        self.last_content = content
        self._setting_clipboard = True
        try:
            if content.startswith("IMAGE::"):
                image_path = content.replace("IMAGE::", "")
                if os.path.exists(image_path):
                    try:
                        with open(image_path, 'rb') as f:
                            image_data = f.read()

                        gbytes = GLib.Bytes.new(image_data)
                        provider = Gdk.ContentProvider.new_for_bytes("image/png", gbytes)

                        self._current_provider = provider
                        self._current_bytes = gbytes

                        self.clipboard.set_content(provider)

                    except Exception as e:
                        print(f"Error setting image content: {e}")
                else:
                    print(f"Image not found: {image_path}")
            else:
                self.clipboard.set(content)
        finally:
            self._setting_clipboard = False
