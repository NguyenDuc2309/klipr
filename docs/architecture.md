# Architecture

How Klipr is put together. For setting up a dev environment see [CONTRIBUTING.md](../CONTRIBUTING.md).

## Source layout

```
src/
├── main.py               # Entry point: Gtk.Application, CLI flags, global shortcut, tray, lifecycle
├── clipboard_manager.py  # Watches the system clipboard (text + images), debounced
├── database.py           # SQLite storage: history, favorites, dedup, pruning, image cache
├── settings.py           # Merges bundled defaults (setting.json) with the user's config
├── tray.py               # System tray over raw D-Bus (StatusNotifierItem + DBusMenu)
├── utils.py              # Small helpers (time formatting, malloc_trim, GSettings lookup)
├── style.css             # Dark theme
├── style_light.css       # Light theme
├── ui/
│   ├── window.py         # Main window: list, search, favorites, keyboard navigation
│   └── settings_dialog.py# Settings view
└── ai/                   # Image-to-text (OCR) via an AI provider
    ├── service.py        # Picks the provider from settings
    ├── base.py           # Provider interface
    ├── gemini.py         # Google Gemini
    ├── openai.py         # OpenAI or any OpenAI-compatible endpoint
    └── prompt.py         # Shared extraction prompt
```

`setting.json` at the repo root is the **bundled defaults** (and the app version). It is shipped inside the package
next to the modules. Do not confuse it with the user's copy in `~/.config/klipr/setting.json`.

## Runtime behaviour

- **Single instance.** Klipr is a `Gtk.Application` (`io.github.nguyenduc2309.klipr`). Running `klipr` again while it
  is running just shows the existing window.
- **CLI flags.** `--hidden` starts without showing the window (used by autostart), `--toggle` / `-t` shows or hides it.
- **X11 backend.** `main.py` forces `GDK_BACKEND=x11`, so on a Wayland session Klipr runs through XWayland.
- **Global shortcut.** Registered as a GNOME custom keybinding via `gsettings`. The binding calls the running
  instance's `toggle-window` action over D-Bus (~5 ms), and falls back to `klipr --toggle` if Klipr is not running.
  On desktops without `gsettings` (non-GNOME) nothing is registered: bind `klipr --toggle` in your desktop's
  keyboard settings instead.
- **Close to tray** (default on). Closing the window hides it and the clipboard monitor keeps running.
  Quit from the tray menu.
- **Autostart** creates `~/.config/autostart/klipr.desktop` with `Exec=klipr --hidden`.

### System tray without AppIndicator

The tray talks StatusNotifierItem + DBusMenu directly over `Gio.DBus`: no AppIndicator, no GTK3, no extra typelibs.
It exports `/StatusNotifierItem` (`org.kde.StatusNotifierItem`) and `/MenuBar` (`com.canonical.dbusmenu`), registers
with `org.kde.StatusNotifierWatcher`, and embeds the icon as `IconPixmap` so it shows even when `klipr` is not in the
icon theme.

- KDE Plasma: works out of the box.
- GNOME / Ubuntu: needs the AppIndicator extension (`gnome-shell-extension-appindicator`, preinstalled on Ubuntu).
- No tray host: Klipr still works; run `klipr` or use the shortcut to bring the window back.

### Theme

`system` follows `gtk-application-prefer-dark-theme` and, when the schema is installed, GNOME's
`org.gnome.desktop.interface color-scheme`. The schema is looked up before use (`utils.gnome_interface_settings`)
because `Gio.Settings.new()` on a missing schema aborts the whole process.

### OCR (image → text)

Image items have an extract button. The image is sent to the configured provider (Gemini or an OpenAI-compatible
API) with the prompt in `ai/prompt.py`, and the text is copied back. API keys are stored **in plain text** in
`~/.config/klipr/setting.json`. Nothing is sent anywhere unless you click extract.

## Data storage

| Data | Path | Kept on `apt remove` |
|---|---|---|
| History + favorites (SQLite) | `~/.local/share/klipr/clipboard.db` | yes |
| Image cache | `~/.cache/klipr/images/` | yes |
| User settings | `~/.config/klipr/setting.json` | yes |

Snap remaps these under `~/snap/klipr/current/`.

## Packaging

| Format | Recipe | Built by |
|---|---|---|
| `.deb` (`Architecture: all`) | `packaging/build.sh` | CI on every code change, attached to GitHub Releases |
| APT repo | `scripts/publish_apt.sh` → `landing/apt/` | Maintainer, locally (needs the signing key) |
| Snap | `snap/snapcraft.yaml` | Launchpad auto-build on push |
| Debian archive | `debian/` | Not used by CI; see [debian.md](debian.md) |

The `.deb` installs modules to `/usr/share/klipr/`, a launcher to `/usr/bin/klipr` (it `cd`s there and runs
`main.py`), the desktop entry as `io.github.nguyenduc2309.klipr.desktop`, and the icon at
`/usr/share/icons/hicolor/128x128/apps/klipr.png`.

**`packaging/build.sh` lists files explicitly.** A new module must be added there, otherwise the package ships
without it. CI catches this: it checks that every `src/**/*.py` exists in the installed package.

Runtime dependencies: `python3`, `python3-gi`, `python3-gi-cairo`, `gir1.2-gtk-4.0`, `python3-pil`.

## Troubleshooting

- **Tray icon missing on GNOME:** `sudo apt install gnome-shell-extension-appindicator`, then log out and back in.
- **Window doesn't appear:** an old instance may be stuck. `pkill -f 'klipr/main.py'` then run `klipr`.
- **Autostart not working:** check that `~/.config/autostart/klipr.desktop` exists and `which klipr` resolves.
- **Shortcut does nothing (non-GNOME):** bind `klipr --toggle` manually in your desktop's keyboard settings.
