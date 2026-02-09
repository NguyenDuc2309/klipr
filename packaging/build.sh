#!/usr/bin/env bash
set -e

# Build script for Klipr .deb package using fpm

VERSION="${1:-1.0.0}"
PACKAGE_NAME="klipr"
BUILD_DIR="build"
ROOT_DIR="$BUILD_DIR/root"

echo "Building Klipr version $VERSION..."

# Clean previous build
rm -rf "$BUILD_DIR"
rm -f "${PACKAGE_NAME}"_*.deb

# Create directory structure
mkdir -p "$ROOT_DIR/usr/share/$PACKAGE_NAME"
mkdir -p "$ROOT_DIR/usr/share/$PACKAGE_NAME/ui"
mkdir -p "$ROOT_DIR/usr/bin"
mkdir -p "$ROOT_DIR/usr/share/applications"
mkdir -p "$ROOT_DIR/usr/share/icons/hicolor/128x128/apps"

# Copy source files (no __pycache__, no .db, no dev files)
cp src/main.py           "$ROOT_DIR/usr/share/$PACKAGE_NAME/"
cp src/database.py       "$ROOT_DIR/usr/share/$PACKAGE_NAME/"
cp src/clipboard_manager.py "$ROOT_DIR/usr/share/$PACKAGE_NAME/"
cp src/settings.py       "$ROOT_DIR/usr/share/$PACKAGE_NAME/"
cp src/tray.py           "$ROOT_DIR/usr/share/$PACKAGE_NAME/"
cp src/tray_service.py   "$ROOT_DIR/usr/share/$PACKAGE_NAME/"
cp src/utils.py          "$ROOT_DIR/usr/share/$PACKAGE_NAME/"
cp src/style.css         "$ROOT_DIR/usr/share/$PACKAGE_NAME/"
cp src/style_light.css   "$ROOT_DIR/usr/share/$PACKAGE_NAME/"
cp src/ui/__init__.py    "$ROOT_DIR/usr/share/$PACKAGE_NAME/ui/"
cp src/ui/window.py      "$ROOT_DIR/usr/share/$PACKAGE_NAME/ui/"
cp src/ui/settings_dialog.py "$ROOT_DIR/usr/share/$PACKAGE_NAME/ui/"

# Copy launcher script
cp packaging/klipr "$ROOT_DIR/usr/bin/"
chmod +x "$ROOT_DIR/usr/bin/klipr"

# Copy desktop entry
cp packaging/klipr.desktop "$ROOT_DIR/usr/share/applications/"

# Copy icon (if exists, otherwise create placeholder)
if [ -f "packaging/klipr.png" ]; then
    cp packaging/klipr.png "$ROOT_DIR/usr/share/icons/hicolor/128x128/apps/"
else
    echo "Warning: packaging/klipr.png not found, creating placeholder..."
    echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" | base64 -d > "$ROOT_DIR/usr/share/icons/hicolor/128x128/apps/klipr.png"
fi

# ── System dependencies ────────────────────────────────────────
# All Python dependencies are system packages (apt), NOT pip.
# When user installs the .deb, apt auto-installs these.
#
#   python3          — Python runtime
#   python3-gi       — PyGObject (GI bindings)
#   python3-gi-cairo — Cairo rendering for GTK
#   gir1.2-gtk-4.0   — GTK4 GIR typelib
#   python3-pil      — Pillow (image hashing)
#   gir1.2-ayatanaappindicator3-0.1 — System tray (AppIndicator)
# ────────────────────────────────────────────────────────────────

fpm -s dir -t deb \
    -n "$PACKAGE_NAME" \
    -v "$VERSION" \
    --architecture all \
    --description "Clipboard history manager for Linux (GTK4)" \
    --url "https://github.com/klipr" \
    --license "MIT" \
    --depends "python3" \
    --depends "python3-gi" \
    --depends "python3-gi-cairo" \
    --depends "gir1.2-gtk-4.0" \
    --depends "python3-pil" \
    --depends "gir1.2-ayatanaappindicator3-0.1" \
    --prefix=/ \
    -C "$ROOT_DIR" .

echo ""
echo "Build complete!"
echo "Package: $(ls ${PACKAGE_NAME}_*.deb 2>/dev/null)"
echo ""
echo "Install:   sudo dpkg -i ${PACKAGE_NAME}_${VERSION}_all.deb && sudo apt-get install -f"
echo "Uninstall: sudo dpkg -r ${PACKAGE_NAME}"
