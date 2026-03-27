<p align="center">
  <img src="assets/logo.png" alt="Klipr Logo" width="96" height="96" />
</p>

<h1 align="center">Klipr</h1>

<p align="center">
  <strong>A modern, fast clipboard manager for Linux</strong><br/>
  Built with GTK4 &bull; Lightweight &bull; Beautiful
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.1.0-blue" alt="Version" />
  <img src="https://img.shields.io/badge/platform-Linux-green" alt="Platform" />
  <img src="https://img.shields.io/badge/GTK-4.0-orange" alt="GTK4" />
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="License" />
</p>

---

## What is Klipr?

Klipr is a **lightweight clipboard history manager** designed for Linux desktops. It quietly runs in the background, saving everything you copy — text and images — so you never lose a copied snippet again.

Built natively with **GTK4** and **Python**, Klipr integrates seamlessly with your desktop. No Electron, no bloat — just a fast, minimal, and beautiful clipboard tool.

---

## Features

### Clipboard History

Automatically captures every text and image you copy. Configurable history limit keeps things lean — oldest items are pruned automatically.

### Favorites

Pin frequently used snippets to a separate favorites list. Favorites are never auto-deleted, so your important clips are always one click away.

### Instant Search

Real-time search across your entire clipboard history and favorites. Find any copied content in milliseconds.

### Image Support

Captures images from your clipboard — screenshots, copied graphics — and displays inline thumbnails. Paste images back to any app with one click.

### Dark, Light & System Themes

Sleek dark mode, clean light mode, or let Klipr follow your OS appearance automatically.

### System Tray

Runs silently in the system tray when closed. Always accessible, never in the way.

### Global Shortcut

Toggle the Klipr window from anywhere with `Alt + V`. Works system-wide, even when Klipr is hidden.

### One-Click Actions

Click any item to copy it back instantly. Hover to reveal copy, favorite, and delete actions.

### Autostart

Optionally start Klipr on login. Runs hidden in the background, ready when you need it.

---

## Screenshots

|             Dark Mode              |              Light Mode              |
| :--------------------------------: | :----------------------------------: |
| ![Dark Mode](screenshots/dark.png) | ![Light Mode](screenshots/light.png) |

---

## Installation

### From `.deb` package (Ubuntu / Debian)

```bash
sudo apt install ./klipr_1.2.1_all.deb
```

### From source

```bash
git clone https://github.com/NguyenDuc2309/klipr.git
cd klipr
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate
# Install dependencies
pip install -r requirements.txt
# Run the application
python3 src/main.py
```

---

## License

MIT License

---

<p align="center">
  Made with ❤️ for the Linux desktop
</p>
