import ctypes
import datetime

_malloc_trim = None
_malloc_trim_looked_up = False


def trim_memory():
    """Hand glibc's freed-but-retained heap pages back to the OS.

    Decoding thumbnails allocates and frees large buffers in a burst. glibc
    keeps that freed space on its own heap rather than returning it, so RSS
    stays at the peak long after the memory is dead — measured 119MB held
    where only ~104MB was live, and it takes glibc hours to give back on its
    own. Python's gc has nothing to do with this (gc.collect() moved RSS by
    0.0MB); it is entirely below the interpreter, so malloc_trim is the only
    thing that releases it.

    Cheap and safe: it only returns memory already free, never anything in
    use. Not available outside glibc (musl, for instance), hence the guard —
    a system without it just keeps the old behaviour.
    """
    global _malloc_trim, _malloc_trim_looked_up
    if not _malloc_trim_looked_up:
        _malloc_trim_looked_up = True
        try:
            _malloc_trim = ctypes.CDLL("libc.so.6").malloc_trim
        except (OSError, AttributeError):
            _malloc_trim = None
    if _malloc_trim is not None:
        try:
            _malloc_trim(0)
        except Exception:
            pass


def format_time(timestamp_str):
    """Format a UTC timestamp string to a human-readable relative time."""
    try:
        dt_utc = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        dt_utc = dt_utc.replace(tzinfo=datetime.timezone.utc)
        dt_local = dt_utc.astimezone()  # Convert to system local timezone

        now = datetime.datetime.now(datetime.timezone.utc).astimezone()
        diff = now - dt_local
        seconds = diff.total_seconds()

        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            return f"{int(seconds / 60)}m ago"
        elif seconds < 86400:
            return f"{int(seconds / 3600)}h ago"
        elif seconds < 604800:
            return f"{int(seconds / 86400)}d ago"
        else:
            return dt_local.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return timestamp_str


def gnome_interface_settings():
    """Return Gio.Settings for org.gnome.desktop.interface, or None.

    Gio.Settings.new() on a schema (or later get on a key) that is not
    installed aborts the whole process via g_error — try/except cannot catch
    it. Desktops without gsettings-desktop-schemas (or with an old one lacking
    color-scheme) would crash on window creation, so look it up first.
    """
    from gi.repository import Gio
    source = Gio.SettingsSchemaSource.get_default()
    schema = source.lookup("org.gnome.desktop.interface", True) if source else None
    if schema is None or not schema.has_key("color-scheme"):
        return None
    return Gio.Settings.new_full(schema, None, None)
