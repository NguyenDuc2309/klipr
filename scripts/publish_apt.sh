#!/usr/bin/env bash
# Build a version and add it to the self-hosted APT repo under landing/apt/,
# so `sudo apt install klipr` works once that directory is live on GitHub
# Pages. See docs/releasing.md for the full one-time setup and release workflow.
set -euo pipefail

VERSION="${1:?Usage: scripts/publish_apt.sh <version> [gnupg-home]}"
GNUPGHOME_DIR="${2:-$HOME/.klipr-signing}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APT_ROOT="$REPO_ROOT/landing/apt"
CODENAME="stable"
COMPONENT="main"
ARCH="all"

if [ ! -d "$GNUPGHOME_DIR" ]; then
    echo "error: signing key directory not found: $GNUPGHOME_DIR" >&2
    echo "       run this on the machine that holds the klipr apt signing key," >&2
    echo "       or pass its GNUPGHOME as the second argument." >&2
    exit 1
fi

KEYID="$(GNUPGHOME="$GNUPGHOME_DIR" gpg --list-secret-keys --with-colons \
    | awk -F: '/^sec/{print $5; exit}')"
if [ -z "$KEYID" ]; then
    echo "error: no secret key found in $GNUPGHOME_DIR" >&2
    exit 1
fi

echo "==> Building klipr $VERSION"
(cd "$REPO_ROOT" && ./packaging/build.sh "$VERSION")

DEB_FILE="$REPO_ROOT/klipr_${VERSION}_all.deb"
if [ ! -f "$DEB_FILE" ]; then
    echo "error: build did not produce $DEB_FILE" >&2
    exit 1
fi

echo "==> Adding to pool"
POOL_DIR="$APT_ROOT/pool/$COMPONENT/k/klipr"
mkdir -p "$POOL_DIR"
cp "$DEB_FILE" "$POOL_DIR/"

# Keep the pool from growing forever: retain the new build plus the 2 most
# recent others, so `apt install klipr=<old-version>` still works briefly
# after a release without the repo accumulating every version ever shipped.
echo "==> Trimming old pool entries (keeping 3 newest)"
ls -1t "$POOL_DIR"/klipr_*_all.deb | tail -n +4 | xargs -r rm -v

echo "==> Regenerating package index"
DIST_DIR="$APT_ROOT/dists/$CODENAME/$COMPONENT/binary-$ARCH"
mkdir -p "$DIST_DIR"
(cd "$APT_ROOT" && dpkg-scanpackages --arch "$ARCH" "pool/$COMPONENT" /dev/null \
    > "$DIST_DIR/Packages")
gzip -9fk "$DIST_DIR/Packages"

echo "==> Writing Release file"
RELEASE_DIR="$APT_ROOT/dists/$CODENAME"
cat > "$RELEASE_DIR/Release" <<EOF
Origin: Klipr
Label: Klipr
Suite: $CODENAME
Codename: $CODENAME
Architectures: $ARCH
Components: $COMPONENT
Description: Klipr clipboard manager APT repository
Date: $(date -Ru)
EOF
(cd "$RELEASE_DIR" && apt-ftparchive release . >> Release.tmp && mv Release.tmp Release.generated)
# apt-ftparchive release regenerates the whole file from scratch and drops
# our Origin/Label/Description headers, so merge: keep our header, append
# its computed hash sections.
{
    cat "$RELEASE_DIR/Release"
    awk '/^MD5Sum:|^SHA1:|^SHA256:/{print; f=1; next} f' "$RELEASE_DIR/Release.generated"
} > "$RELEASE_DIR/Release.final"
mv "$RELEASE_DIR/Release.final" "$RELEASE_DIR/Release"
rm -f "$RELEASE_DIR/Release.generated"

echo "==> Signing (detached Release.gpg + inline InRelease)"
rm -f "$RELEASE_DIR/Release.gpg" "$RELEASE_DIR/InRelease"
GNUPGHOME="$GNUPGHOME_DIR" gpg --default-key "$KEYID" --armor \
    --detach-sign --output "$RELEASE_DIR/Release.gpg" "$RELEASE_DIR/Release"
GNUPGHOME="$GNUPGHOME_DIR" gpg --default-key "$KEYID" --armor \
    --clearsign --output "$RELEASE_DIR/InRelease" "$RELEASE_DIR/Release"

rm -f "$DEB_FILE"

echo
echo "==> Done. Repo staged at $APT_ROOT"
echo "    git add landing/apt && git commit -m 'apt: publish klipr $VERSION' && git push"
echo "    (GitHub Pages redeploys automatically; see docs/releasing.md)"
