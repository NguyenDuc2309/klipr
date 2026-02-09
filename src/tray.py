"""
System tray icon — pure D-Bus SNI + DBusMenu implementation.

No AppIndicator3. No GTK3. No extra GIR typelibs.
Uses only Gio.DBus (part of PyGObject/GTK4 already installed).

Implements:
  - org.kde.StatusNotifierItem  on /StatusNotifierItem
  - com.canonical.dbusmenu      on /MenuBar

Registers with org.kde.StatusNotifierWatcher (provided by desktop:
KDE has it natively; GNOME needs gnome-shell-extension-appindicator).
"""

import gi
import os
import struct

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GLib


# ── D-Bus interface XML ──────────────────────────────────────────

SNI_XML = """
<node>
  <interface name="org.kde.StatusNotifierItem">
    <method name="Activate">
      <arg type="i" name="x" direction="in"/>
      <arg type="i" name="y" direction="in"/>
    </method>
    <method name="SecondaryActivate">
      <arg type="i" name="x" direction="in"/>
      <arg type="i" name="y" direction="in"/>
    </method>
    <method name="ContextMenu">
      <arg type="i" name="x" direction="in"/>
      <arg type="i" name="y" direction="in"/>
    </method>
    <property name="Category" type="s" access="read"/>
    <property name="Id" type="s" access="read"/>
    <property name="Title" type="s" access="read"/>
    <property name="Status" type="s" access="read"/>
    <property name="WindowId" type="u" access="read"/>
    <property name="IconName" type="s" access="read"/>
    <property name="IconPixmap" type="a(iiay)" access="read"/>
    <property name="Menu" type="o" access="read"/>
    <signal name="NewIcon"/>
    <signal name="NewStatus">
      <arg type="s" name="status"/>
    </signal>
  </interface>
</node>
"""

DBUSMENU_XML = """
<node>
  <interface name="com.canonical.dbusmenu">
    <method name="GetLayout">
      <arg type="i" name="parentId" direction="in"/>
      <arg type="i" name="recursionDepth" direction="in"/>
      <arg type="as" name="propertyNames" direction="in"/>
      <arg type="u" name="revision" direction="out"/>
      <arg type="(ia{sv}av)" name="layout" direction="out"/>
    </method>
    <method name="GetGroupProperties">
      <arg type="ai" name="ids" direction="in"/>
      <arg type="as" name="propertyNames" direction="in"/>
      <arg type="a(ia{sv})" name="properties" direction="out"/>
    </method>
    <method name="GetProperty">
      <arg type="i" name="id" direction="in"/>
      <arg type="s" name="name" direction="in"/>
      <arg type="v" name="value" direction="out"/>
    </method>
    <method name="Event">
      <arg type="i" name="id" direction="in"/>
      <arg type="s" name="eventId" direction="in"/>
      <arg type="v" name="data" direction="in"/>
      <arg type="u" name="timestamp" direction="in"/>
    </method>
    <method name="EventGroup">
      <arg type="a(isvu)" name="events" direction="in"/>
      <arg type="ai" name="idErrors" direction="out"/>
    </method>
    <method name="AboutToShow">
      <arg type="i" name="id" direction="in"/>
      <arg type="b" name="needUpdate" direction="out"/>
    </method>
    <method name="AboutToShowGroup">
      <arg type="ai" name="ids" direction="in"/>
      <arg type="ai" name="updatesNeeded" direction="out"/>
      <arg type="ai" name="idErrors" direction="out"/>
    </method>
    <property name="Version" type="u" access="read"/>
    <property name="TextDirection" type="s" access="read"/>
    <property name="Status" type="s" access="read"/>
    <property name="IconThemePath" type="as" access="read"/>
    <signal name="LayoutUpdated">
      <arg type="u" name="revision"/>
      <arg type="i" name="parent"/>
    </signal>
    <signal name="ItemsPropertiesUpdated">
      <arg type="a(ia{sv})" name="updatedProps"/>
      <arg type="a(ias)" name="removedProps"/>
    </signal>
  </interface>
</node>
"""


# ── Helper: build a DBusMenu layout node as GLib.Variant ─────────

def _make_menu_item(item_id, props_dict, children_variants=None):
    """
    Build a single (ia{sv}av) Variant for DBusMenu GetLayout.
    props_dict: {str: GLib.Variant}
    children_variants: list of already-built (ia{sv}av) GLib.Variant, or None
    """
    builder = GLib.VariantBuilder(GLib.VariantType.new("(ia{sv}av)"))

    # i — item id
    builder.add_value(GLib.Variant("i", item_id))

    # a{sv} — properties
    props_builder = GLib.VariantBuilder(GLib.VariantType.new("a{sv}"))
    for key, val in props_dict.items():
        entry = GLib.VariantBuilder(GLib.VariantType.new("{sv}"))
        entry.add_value(GLib.Variant("s", key))
        entry.add_value(GLib.Variant("v", val))
        props_builder.add_value(entry.end())
    builder.add_value(props_builder.end())

    # av — children (each wrapped in variant)
    children_builder = GLib.VariantBuilder(GLib.VariantType.new("av"))
    if children_variants:
        for child in children_variants:
            children_builder.add_value(GLib.Variant("v", child))
    builder.add_value(children_builder.end())

    return builder.end()


class TrayIcon:
    """
    Pure D-Bus system tray (SNI + DBusMenu).
    No AppIndicator, no GTK3, no extra system packages.
    """

    # Menu item IDs
    _ID_ROOT = 0
    _ID_OPEN = 1
    _ID_SEP = 2
    _ID_QUIT = 3

    def __init__(self, app, on_open=None, on_quit=None):
        self.app = app
        self.on_open = on_open
        self.on_quit = on_quit

        self._conn = None
        self._sni_reg_id = 0
        self._menu_reg_id = 0
        self._registered = False
        self._revision = 1
        self._icon_pixmap = None  # Cached GLib.Variant for IconPixmap

        self._load_icon_pixmap()
        self._setup()

    # ── Icon pixmap ───────────────────────────────────────────────

    def _load_icon_pixmap(self):
        """Load app icon as ARGB pixel data for IconPixmap D-Bus property.

        SNI spec: IconPixmap = a(iiay) — array of (width, height, ARGB_bytes).
        This ensures the tray icon shows even if the named icon isn't in the theme.
        """
        icon_paths = [
            # Installed location
            "/usr/share/icons/hicolor/128x128/apps/klipr.png",
            # Dev location
            os.path.join(os.path.dirname(__file__), "..", "packaging", "klipr.png"),
        ]

        for path in icon_paths:
            if not os.path.exists(path):
                continue
            try:
                from PIL import Image
                with Image.open(path) as img:
                    # Resize to 22x22 (standard tray icon size)
                    img = img.resize((22, 22), Image.LANCZOS).convert("RGBA")
                    w, h = img.size
                    pixels = img.load()

                    # Convert RGBA → ARGB (network byte order / big-endian)
                    argb_data = bytearray()
                    for y in range(h):
                        for x in range(w):
                            r, g, b, a = pixels[x, y]
                            argb_data.extend(struct.pack(">I", (a << 24) | (r << 16) | (g << 8) | b))

                    self._icon_pixmap = GLib.Variant("a(iiay)", [(w, h, bytes(argb_data))])
                return
            except Exception as e:
                print(f"Tray: failed to load icon pixmap from {path}: {e}")

    # ── Setup ────────────────────────────────────────────────────

    def _setup(self):
        try:
            # Use session bus directly — reliable, doesn't depend on GApplication internals
            self._conn = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            if not self._conn:
                return

            sni_info = Gio.DBusNodeInfo.new_for_xml(SNI_XML).interfaces[0]
            menu_info = Gio.DBusNodeInfo.new_for_xml(DBUSMENU_XML).interfaces[0]

            self._sni_reg_id = self._conn.register_object(
                "/StatusNotifierItem",
                sni_info,
                self._on_sni_method_call,
                self._on_sni_get_property,
                None,
            )

            self._menu_reg_id = self._conn.register_object(
                "/MenuBar",
                menu_info,
                self._on_menu_method_call,
                self._on_menu_get_property,
                None,
            )

            self._register_with_watcher()

        except Exception as e:
            print(f"Tray: init failed ({e})")

    def is_available(self):
        return self._registered

    def shutdown(self):
        try:
            if self._conn and self._sni_reg_id:
                self._conn.unregister_object(self._sni_reg_id)
            if self._conn and self._menu_reg_id:
                self._conn.unregister_object(self._menu_reg_id)
        except Exception:
            pass

    # ── Watcher registration ─────────────────────────────────────

    def _register_with_watcher(self):
        """Register with StatusNotifierWatcher using our unique bus name."""
        try:
            unique_name = self._conn.get_unique_name()
            if not unique_name:
                return

            self._conn.call_sync(
                "org.kde.StatusNotifierWatcher",
                "/StatusNotifierWatcher",
                "org.kde.StatusNotifierWatcher",
                "RegisterStatusNotifierItem",
                GLib.Variant("(s)", (unique_name,)),
                None,
                Gio.DBusCallFlags.NONE,
                1500,
                None,
            )
            self._registered = True
        except GLib.Error:
            # Watcher not running (no tray host extension on this desktop)
            self._registered = False

    # ── SNI property getter ──────────────────────────────────────

    def _on_sni_get_property(self, conn, sender, path, iface, prop, *_rest):
        # IconPixmap is pre-built (large payload), return directly
        if prop == "IconPixmap" and self._icon_pixmap is not None:
            return self._icon_pixmap
        if prop == "IconPixmap":
            return GLib.Variant("a(iiay)", [])

        props = {
            "Category": GLib.Variant("s", "ApplicationStatus"),
            "Id": GLib.Variant("s", "klipr"),
            "Title": GLib.Variant("s", "Klipr"),
            "Status": GLib.Variant("s", "Active"),
            "WindowId": GLib.Variant("u", 0),
            "IconName": GLib.Variant("s", "edit-paste-symbolic"),
            "Menu": GLib.Variant("o", "/MenuBar"),
        }
        return props.get(prop)

    # ── SNI method handler ───────────────────────────────────────

    def _on_sni_method_call(self, conn, sender, path, iface, method, params, invocation):
        if method in ("Activate", "SecondaryActivate"):
            if self.on_open:
                GLib.idle_add(self.on_open)
            invocation.return_value(None)
            return

        if method == "ContextMenu":
            invocation.return_value(None)
            return

        invocation.return_dbus_error(
            "org.freedesktop.DBus.Error.UnknownMethod", f"No method {method}"
        )

    # ── DBusMenu property getter ─────────────────────────────────

    def _on_menu_get_property(self, conn, sender, path, iface, prop, *_rest):
        props = {
            "Version": GLib.Variant("u", 3),
            "TextDirection": GLib.Variant("s", "ltr"),
            "Status": GLib.Variant("s", "normal"),
            "IconThemePath": GLib.Variant("as", []),
        }
        return props.get(prop)

    # ── DBusMenu method handler ──────────────────────────────────

    def _on_menu_method_call(self, conn, sender, path, iface, method, params, invocation):
        if method == "GetLayout":
            self._handle_get_layout(params, invocation)
            return

        if method == "GetGroupProperties":
            ids, prop_names = params.unpack()
            result_builder = GLib.VariantBuilder(GLib.VariantType.new("a(ia{sv})"))
            for item_id in ids:
                p = self._item_props(item_id)
                entry_builder = GLib.VariantBuilder(GLib.VariantType.new("(ia{sv})"))
                entry_builder.add_value(GLib.Variant("i", item_id))
                dict_builder = GLib.VariantBuilder(GLib.VariantType.new("a{sv}"))
                for k, v in p.items():
                    kv = GLib.VariantBuilder(GLib.VariantType.new("{sv}"))
                    kv.add_value(GLib.Variant("s", k))
                    kv.add_value(GLib.Variant("v", v))
                    dict_builder.add_value(kv.end())
                entry_builder.add_value(dict_builder.end())
                result_builder.add_value(entry_builder.end())
            invocation.return_value(GLib.Variant.new_tuple(result_builder.end()))
            return

        if method == "GetProperty":
            item_id, name = params.unpack()
            p = self._item_props(item_id)
            val = p.get(name, GLib.Variant("s", ""))
            invocation.return_value(GLib.Variant.new_tuple(GLib.Variant("v", val)))
            return

        if method == "Event":
            item_id, event_id, _data, _ts = params.unpack()
            # Tray hosts send "clicked" or "activate" depending on implementation
            if event_id in ("clicked", "activate"):
                if item_id == self._ID_OPEN and self.on_open:
                    GLib.idle_add(self.on_open)
                elif item_id == self._ID_QUIT and self.on_quit:
                    GLib.idle_add(self.on_quit)
            invocation.return_value(None)
            return

        if method == "EventGroup":
            invocation.return_value(GLib.Variant.new_tuple(GLib.Variant("ai", [])))
            return

        if method == "AboutToShow":
            invocation.return_value(GLib.Variant.new_tuple(GLib.Variant("b", False)))
            return

        if method == "AboutToShowGroup":
            invocation.return_value(GLib.Variant.new_tuple(
                GLib.Variant("ai", []),
                GLib.Variant("ai", []),
            ))
            return

        invocation.return_dbus_error(
            "org.freedesktop.DBus.Error.UnknownMethod", f"No method {method}"
        )

    # ── Menu layout ──────────────────────────────────────────────

    def _item_props(self, item_id):
        """Return properties dict {str: GLib.Variant} for a menu item."""
        if item_id == self._ID_ROOT:
            return {"children-display": GLib.Variant("s", "submenu")}
        if item_id == self._ID_OPEN:
            return {
                "label": GLib.Variant("s", "Open Klipr"),
                "enabled": GLib.Variant("b", True),
                "visible": GLib.Variant("b", True),
            }
        if item_id == self._ID_SEP:
            return {"type": GLib.Variant("s", "separator")}
        if item_id == self._ID_QUIT:
            return {
                "label": GLib.Variant("s", "Quit"),
                "enabled": GLib.Variant("b", True),
                "visible": GLib.Variant("b", True),
            }
        return {}

    def _handle_get_layout(self, params, invocation):
        """Build and return the full menu layout tree."""
        _parent_id, _depth, _props = params.unpack()

        # Build child nodes
        open_node = _make_menu_item(self._ID_OPEN, self._item_props(self._ID_OPEN))
        sep_node = _make_menu_item(self._ID_SEP, self._item_props(self._ID_SEP))
        quit_node = _make_menu_item(self._ID_QUIT, self._item_props(self._ID_QUIT))

        # Build root with children
        root = _make_menu_item(
            self._ID_ROOT,
            self._item_props(self._ID_ROOT),
            [open_node, sep_node, quit_node],
        )

        # Return (u, (ia{sv}av)) — revision + layout
        result = GLib.Variant.new_tuple(
            GLib.Variant("u", self._revision),
            root,
        )
        invocation.return_value(result)
