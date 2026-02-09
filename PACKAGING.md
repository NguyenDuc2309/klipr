# Klipr — Packaging & Architecture Guide

## Package Information

| Field | Value |
|---|---|
| **Name** | `klipr` |
| **Version** | Semantic versioning (`1.0.0`, `1.1.0`, ...) |
| **Architecture** | `all` (pure Python, platform-independent) |
| **License** | MIT |
| **Format** | `.deb` (Debian/Ubuntu) |

---

## Architecture Overview

```
src/
├── main.py              # Entry point — GtkApplication, lifecycle, tray init
├── clipboard_manager.py # Reads/writes system clipboard (text + images)
├── database.py          # SQLite storage (UPSERT, dedup, pruning)
├── settings.py          # JSON config (~/.config/klipr/settings.json)
├── tray.py              # System tray — pure D-Bus SNI + DBusMenu
├── utils.py             # Helpers (format_time)
├── style.css            # Dark theme
├── style_light.css      # Light theme
└── ui/
    ├── __init__.py
    ├── window.py         # Main window UI
    └── settings_dialog.py # Settings modal
```

### System Tray — Pure D-Bus (no AppIndicator)

The tray icon is implemented using **StatusNotifierItem (SNI)** + **DBusMenu** protocols
directly over `Gio.DBus`. This means:

- **No AppIndicator3** dependency
- **No GTK3** — runs entirely within the GTK4 process
- **No extra GIR typelibs** to install
- Uses only `Gio.DBus` which is already part of `python3-gi`

The tray exports two D-Bus objects:

| Object Path | Interface | Purpose |
|---|---|---|
| `/StatusNotifierItem` | `org.kde.StatusNotifierItem` | Icon, title, click handling |
| `/MenuBar` | `com.canonical.dbusmenu` | Right-click menu (Open / Quit) |

On startup, it registers with `org.kde.StatusNotifierWatcher`. The desktop's tray host
(provided by the DE or an extension) then discovers and displays the icon.

**Desktop compatibility:**
- **KDE Plasma**: Native support (StatusNotifierWatcher built-in)
- **GNOME**: Requires `gnome-shell-extension-appindicator` (pre-installed on Ubuntu 22.04+)
- **XFCE/Cinnamon/MATE**: Generally supported via built-in SNI support

The tray includes `IconPixmap` (embedded ARGB pixel data) so the icon displays even if
`klipr` is not in the system icon theme.

---

## Dependencies

### Runtime (declared in .deb, auto-installed by apt)

| Package | Purpose |
|---|---|
| `python3` | Python 3.8+ runtime |
| `python3-gi` | PyGObject — GI bindings (includes `Gio.DBus` for tray) |
| `python3-gi-cairo` | Cairo rendering for GTK |
| `gir1.2-gtk-4.0` | GTK4 GIR typelib |
| `python3-pil` | Pillow — image hashing for dedup |

**No additional system packages needed.** The tray icon uses only `Gio.DBus`
(part of `python3-gi`), so no AppIndicator/Ayatana libraries are required.

### Build-time

```bash
sudo apt install ruby ruby-dev build-essential
sudo gem install --no-document fpm
```

---

## Building the .deb Package

```bash
cd /path/to/clipboard
./packaging/build.sh [VERSION]
```

Example:
```bash
./packaging/build.sh 1.0.0
```

Default version: `1.0.0` if not specified.

The build script:
1. Cleans previous build artifacts
2. Creates FHS directory structure under `build/root/`
3. Copies source to `/usr/share/klipr/`
4. Installs launcher to `/usr/bin/klipr`
5. Installs `.desktop` entry to `/usr/share/applications/`
6. Installs icon to `/usr/share/icons/hicolor/128x128/apps/`
7. Runs `gtk-update-icon-cache` post-install
8. Produces `klipr_VERSION_all.deb`

---

## Installing

```bash
sudo apt install ./klipr_1.0.0_all.deb
```

This single command installs Klipr and all its dependencies automatically.

## Uninstalling

```bash
sudo apt remove klipr
```

User data (`~/.local/share/klipr/`, `~/.cache/klipr/`, `~/.config/klipr/`) is preserved.

---

## Running Klipr

| Method | Command |
|---|---|
| Command line | `klipr` |
| App launcher | Search "Klipr" in application menu |
| Hidden start (autostart) | `klipr --hidden` |
| Development | `cd /path/to/clipboard && python3 src/main.py` |

---

## Application Behavior

### Close to Tray (default: ON)

When closing the window (X button), Klipr **hides** and continues running in the background.
The clipboard monitor stays active. To bring the window back:

- **Click the tray icon** (left click)
- **Right-click tray icon → "Open Klipr"**
- Run `klipr` again (existing process shows its window)

### Quit Completely

- **Right-click tray icon → "Quit"**
- Or disable "Close to system tray" in Settings, then close normally

### Settings

Click the **menu icon** (hamburger) in the header to open Settings:

| Setting | Default | Description |
|---|---|---|
| Close to system tray | ON | Hide on close instead of quitting |
| Start on login | OFF | Create autostart `.desktop` entry |
| Theme | Dark | Dark / Light / System |

### Autostart

When enabled, creates `~/.config/autostart/klipr.desktop` with `Exec=klipr --hidden`.
Klipr starts hidden on login and monitors clipboard in the background.

---

## Data Storage

| Data | Path | Persists across updates |
|---|---|---|
| Clipboard history DB | `~/.local/share/klipr/clipboard.db` | Yes |
| Image cache | `~/.cache/klipr/images/` | Yes |
| Settings | `~/.config/klipr/settings.json` | Yes |

All directories are created automatically on first run.

---

## Icon

The package includes a 128x128 PNG icon at:
- **Installed**: `/usr/share/icons/hicolor/128x128/apps/klipr.png`
- **Source**: `packaging/klipr.png`

The tray icon embeds pixel data via `IconPixmap` D-Bus property, so it displays
regardless of whether the icon is in the system theme.

To customize: replace `packaging/klipr.png` and rebuild.

---

## Version Management

1. Build: `./packaging/build.sh 1.1.0`
2. Test locally: `sudo apt install ./klipr_1.1.0_all.deb`
3. Tag: `git tag v1.1.0`
4. Upload `.deb` to GitHub Releases or distribution channel

---

## Troubleshooting

### Tray icon not visible

The tray requires a **StatusNotifierWatcher** on the desktop:
- **Ubuntu/GNOME**: Install `gnome-shell-extension-appindicator` if not already present
  (`sudo apt install gnome-shell-extension-appindicator`)
- **KDE**: Works out of the box
- Klipr still functions normally without the tray — close-to-tray will hide the window,
  and running `klipr` again will bring it back

### Import errors after installation

```bash
sudo apt install -f   # Fix missing dependencies
```

### Window doesn't appear

```bash
ps aux | grep klipr   # Check if already running
pkill -f klipr        # Kill existing instance
klipr                 # Start fresh
```

### Autostart not working

- Verify `~/.config/autostart/klipr.desktop` exists
- Check that your DE supports XDG autostart
- Verify `klipr` is in `$PATH` (`which klipr`)
