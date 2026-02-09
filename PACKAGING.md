# Klipr - Packaging Guide

## Package Information

- **Package Name**: `klipr`
- **Version Convention**: Semantic versioning (e.g., `1.0.0`, `1.1.0`, `1.1.1`)
- **Architecture**: `amd64` (x86_64 Linux)

## Dependencies

The package requires the following system dependencies:

- `python3` (Python 3.8+)
- `python3-gi` (Python GTK bindings)
- `gir1.2-gtk-4.0` (GTK 4.0 introspection data)
- `python3-pil` (Pillow for image processing)

These are automatically declared in the `.deb` package and will be installed when installing Klipr.

## Build Requirements

To build the `.deb` package, you need:

```bash
sudo apt install ruby ruby-dev build-essential
sudo gem install --no-document fpm
```

## Building the Package

From the project root directory:

```bash
cd /path/to/clipboard
./packaging/build.sh [VERSION]
```

Example:
```bash
./packaging/build.sh 1.0.0
```

If no version is specified, it defaults to `1.0.0`.

The build script will:
1. Clean previous build artifacts
2. Create the package directory structure
3. Copy source files to `/usr/share/klipr/`
4. Install launcher script to `/usr/bin/klipr`
5. Install desktop entry to `/usr/share/applications/`
6. Install icon to `/usr/share/icons/hicolor/128x128/apps/`
7. Build the `.deb` package using `fpm`

Output: `klipr_VERSION_amd64.deb`

## Installing the Package

```bash
sudo dpkg -i klipr_1.0.0_amd64.deb
sudo apt -f install  # Install any missing dependencies
```

## Uninstalling

```bash
sudo apt remove klipr
```

**Note**: User data (clipboard history database) is stored in `~/.local/share/klipr/` and is **not** removed during uninstall. This allows users to preserve their clipboard history if they reinstall later.

## Running Klipr

After installation, you can run Klipr in several ways:

1. **Command line**: `klipr`
2. **Application launcher**: Search for "Klipr" in your application menu
3. **Hidden start** (for autostart): `klipr --hidden`

## Application Lifecycle

### Close-to-Background

When you close the Klipr window (click X), the application **hides** but continues running in the background. This allows clipboard monitoring to continue.

To bring the window back:
- Run `klipr` again from command line or launcher
- The existing process will show the hidden window

### Quit Completely

To fully exit Klipr:
- Click the **Quit** button (power icon) in the header
- Or use the Quit option from the application menu

### Autostart

Klipr supports optional autostart on login:

1. Click the **Settings** (gear) icon in the header
2. Toggle **"Start on login"** ON/OFF

When enabled:
- Creates `~/.config/autostart/klipr.desktop`
- Klipr starts automatically on login (hidden, in background)
- You can bring up the window by running `klipr` manually

When disabled:
- Removes the autostart desktop file
- Klipr will not start automatically on login

## Data Storage

Klipr stores user data in standard XDG directories:

- **Database**: `~/.local/share/klipr/clipboard.db`
- **Image cache**: `~/.cache/klipr/images/`

These directories are created automatically on first run. User data persists across updates and reinstalls.

## Icon

The package includes an icon at `/usr/share/icons/hicolor/128x128/apps/klipr.png`.

If you want to customize the icon:
1. Place your icon file at `packaging/klipr.png` (128x128 PNG recommended)
2. Rebuild the package

If no icon is provided, the build script creates a minimal placeholder.

## Version Management

When releasing a new version:

1. Update version in `packaging/build.sh` default or pass as argument
2. Build: `./packaging/build.sh 1.1.0`
3. Test the `.deb` package locally
4. Tag the release: `git tag v1.1.0`
5. Upload `klipr_1.1.0_amd64.deb` to GitHub Releases or your distribution channel

## Troubleshooting

### Import Errors After Installation

If you see import errors when running `klipr`, ensure:
- All Python dependencies are installed: `sudo apt install python3-gi gir1.2-gtk-4.0 python3-pil`
- The launcher script has execute permissions: `ls -l /usr/bin/klipr`

### Autostart Not Working

If autostart doesn't work:
- Check if `~/.config/autostart/klipr.desktop` exists
- Verify your desktop environment supports `.desktop` autostart files
- Check desktop environment logs for errors

### Window Doesn't Appear

If the window doesn't appear when running `klipr`:
- Check if Klipr is already running: `ps aux | grep klipr`
- Kill existing process: `pkill -f klipr`
- Try running again: `klipr`

