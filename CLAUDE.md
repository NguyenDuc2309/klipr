# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Klipr is a GTK4 clipboard history manager for Linux (X11 only). It monitors the system clipboard, stores text and images, and provides a searchable UI with favorites, themes, and system tray integration. Written in Python, packaged as `.deb`.

## Commands

```bash
# Run (from project root)
python3 src/main.py                # normal start
python3 src/main.py --hidden        # start minimized to tray
python3 src/main.py --toggle       # show/hide window (used by global shortcut)

# Build .deb package
./packaging/build.sh 1.2.5         # produces klipr_1.2.5_all.deb

# Smoke test
python3 scripts/smoke_test.py
```

No formal test framework (no pytest/unittest). The smoke test instantiates the GTK app with a mock DB interface and verifies widget creation.

## Architecture

**Entry point**: `src/main.py` — `ClipboardApp(Gtk.Application)` with `HANDLES_COMMAND_LINE`. Forces `GDK_BACKEND=x11` (Wayland not supported). CLI flags: `--hidden`, `--toggle`.

**Data flow**: `ClipboardManager` → DB → `ClipboardWindow`

- `clipboard_manager.py`: Listens to `Gdk.Clipboard.changed`, debounces 100ms, reads text/images async. Images saved to `~/.cache/klipr/images/` with MD5 dedup, stored in DB as `IMAGE::<hash>`.
- `database.py`: Two SQLite tables (`clipboard`, `favorites`). Connection-per-call via context manager. Auto-prunes beyond `historyLimit`. `ON CONFLICT DO UPDATE` for dedup.
- `settings.py`: Layered config — base defaults from bundled `setting.json`, user overrides at `~/.config/klipr/settings.json`. In dev mode (local `setting.json` exists), user config ignored. Watches settings file via `Gio.FileMonitor` for live reload.
- `tray.py`: Pure D-Bus SNI implementation (no AppIndicator dependency). Exports `org.kde.StatusNotifierItem` and `com.canonical.dbusmenu`. Icon embedded as ARGB pixel data so it works without theme icons.
- `ui/window.py`: Main window with `Gtk.Stack` for page nav (main/settings). `Gtk.ListBox` for items, tabs for History/Favorites. Search with 180ms debounce (tuned for Vietnamese IME). Toast notifications via `Gtk.Overlay` + `Gtk.Revealer`.
- `ui/settings_dialog.py`: Settings modal with history limit, shortcut capture, autostart, and theme selection.

**Key patterns**:
- `DBInterface` class in `main.py` facades database functions, passed to window to decouple UI from direct DB imports
- Callback pattern: `ClipboardManager(on_update_callback)`, `TrayIcon(on_open, on_quit)`
- `GLib.idle_add` for thread-safe UI updates
- CSS layering: dark theme always loaded as base, light overrides applied at higher provider priority

## Runtime Data Paths

| Data | Path |
|---|---|
| Clipboard DB | `~/.local/share/klipr/clipboard.db` |
| Image cache | `~/.cache/klipr/images/` |
| User settings | `~/.config/klipr/settings.json` |
| Autostart entry | `~/.config/autostart/klipr.desktop` |

## Configuration

`setting.json` (bundled defaults): name, version, closeToTray, autostart, theme (dark/light/system), historyLimit, shortcut (registered via GNOME `gsettings` custom keybindings, not pynput).

## Packaging

Installs to `/usr/share/klipr/` with launcher at `/usr/bin/klipr`. Runtime deps: `python3`, `python3-gi`, `python3-gi-cairo`, `gir1.2-gtk-4.0`, `python3-pil`. Post-install runs `gtk-update-icon-cache` and `update-desktop-database`.