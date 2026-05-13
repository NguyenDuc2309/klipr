#!/usr/bin/env bash
set -e

# Build script for Klipr .deb package
# Supports: fpm (if installed) or dpkg-deb (always available on Debian/Ubuntu)

VERSION="${1:-$(python3 -c "import json; print(json.load(open('setting.json'))['version'])")}"
PACKAGE_NAME="klipr"
BUILD_DIR="build"
ROOT_DIR="$BUILD_DIR/root"

echo "Building Klipr version $VERSION..."

# Clean previous build artifacts for this specific version
rm -rf "$BUILD_DIR"
rm -f "${PACKAGE_NAME}_${VERSION}_all.deb"

# ── Create FHS directory structure ─────────────────────────────
mkdir -p "$ROOT_DIR/usr/share/$PACKAGE_NAME"
mkdir -p "$ROOT_DIR/usr/share/$PACKAGE_NAME/ui"
mkdir -p "$ROOT_DIR/usr/share/$PACKAGE_NAME/assets"
mkdir -p "$ROOT_DIR/usr/bin"
mkdir -p "$ROOT_DIR/usr/share/applications"
mkdir -p "$ROOT_DIR/usr/share/icons/hicolor/128x128/apps"

# ── Copy source files ─────────────────────────────────────────
cp src/main.py              "$ROOT_DIR/usr/share/$PACKAGE_NAME/"
cp src/database.py          "$ROOT_DIR/usr/share/$PACKAGE_NAME/"
cp src/clipboard_manager.py "$ROOT_DIR/usr/share/$PACKAGE_NAME/"
cp src/settings.py          "$ROOT_DIR/usr/share/$PACKAGE_NAME/"
cp src/tray.py              "$ROOT_DIR/usr/share/$PACKAGE_NAME/"
cp src/utils.py             "$ROOT_DIR/usr/share/$PACKAGE_NAME/"
cp src/style.css            "$ROOT_DIR/usr/share/$PACKAGE_NAME/"
cp src/style_light.css      "$ROOT_DIR/usr/share/$PACKAGE_NAME/"
cp src/ui/__init__.py       "$ROOT_DIR/usr/share/$PACKAGE_NAME/ui/"
cp src/ui/window.py         "$ROOT_DIR/usr/share/$PACKAGE_NAME/ui/"
cp src/ui/settings_dialog.py "$ROOT_DIR/usr/share/$PACKAGE_NAME/ui/"
cp setting.json             "$ROOT_DIR/usr/share/$PACKAGE_NAME/"
cp assets/logo.png          "$ROOT_DIR/usr/share/$PACKAGE_NAME/assets/"
cp assets/light_logo.png    "$ROOT_DIR/usr/share/$PACKAGE_NAME/assets/"

# Copy launcher script
cp packaging/klipr "$ROOT_DIR/usr/bin/"
chmod +x "$ROOT_DIR/usr/bin/klipr"

# Copy desktop entry
cp packaging/klipr.desktop "$ROOT_DIR/usr/share/applications/"

# Copy icon
if [ -f "assets/logo.png" ]; then
    cp assets/logo.png "$ROOT_DIR/usr/share/icons/hicolor/128x128/apps/klipr.png"
else
    echo "Warning: assets/logo.png not found, creating placeholder..."
    echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" | base64 -d > "$ROOT_DIR/usr/share/icons/hicolor/128x128/apps/klipr.png"
fi

# ── Post-install / post-remove script ──────────────────────────
cat > "$BUILD_DIR/after-install.sh" << 'POSTINST'
#!/bin/sh
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
fi
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications 2>/dev/null || true
fi
POSTINST
chmod +x "$BUILD_DIR/after-install.sh"

# ── Dependencies ───────────────────────────────────────────────
# python3          — Python runtime
# python3-gi       — PyGObject (includes Gio.DBus for tray)
# python3-gi-cairo — Cairo rendering for GTK
# gir1.2-gtk-4.0   — GTK4 GIR typelib
# python3-pil      — Pillow (image hashing)
#
# Tray: pure D-Bus SNI + DBusMenu via Gio.DBus. No AppIndicator.

DEPENDS="python3, python3-gi, python3-gi-cairo, gir1.2-gtk-4.0, python3-pil"

# ── Build .deb ─────────────────────────────────────────────────

if command -v fpm >/dev/null 2>&1; then
    echo "Using fpm..."
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
        --after-install "$BUILD_DIR/after-install.sh" \
        --after-remove "$BUILD_DIR/after-install.sh" \
        --prefix=/ \
        -C "$ROOT_DIR" .
else
    echo "fpm not found, using dpkg-deb..."

    # Create DEBIAN control files
    mkdir -p "$ROOT_DIR/DEBIAN"

    cat > "$ROOT_DIR/DEBIAN/control" << EOF
Package: $PACKAGE_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: all
Depends: $DEPENDS
Maintainer: Klipr <klipr@dev>
Description: Clipboard history manager for Linux (GTK4)
 Klipr monitors your clipboard and saves text and image history.
 Features: search, favorites, dark/light/system themes, system tray.
EOF

    cp "$BUILD_DIR/after-install.sh" "$ROOT_DIR/DEBIAN/postinst"
    cp "$BUILD_DIR/after-install.sh" "$ROOT_DIR/DEBIAN/postrm"

    DEB_FILE="${PACKAGE_NAME}_${VERSION}_all.deb"
    dpkg-deb --build --root-owner-group "$ROOT_DIR" "$DEB_FILE"
fi

echo ""
echo "Build complete!"
echo "Package: $(ls ${PACKAGE_NAME}_*.deb 2>/dev/null)"
echo ""
echo "Install:   sudo apt install ./${PACKAGE_NAME}_${VERSION}_all.deb"
echo "Uninstall: sudo apt remove ${PACKAGE_NAME}"
