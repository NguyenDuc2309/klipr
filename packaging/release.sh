#!/usr/bin/env bash
# Bump the version everywhere, commit, tag and push.
# GitHub Actions (release.yml) then tests, builds the .deb and publishes the release.
#
# Usage: packaging/release.sh 1.2.8
set -euo pipefail

cd "$(dirname "$0")/.."

NEW="${1:-}"
[[ "$NEW" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "Usage: $0 X.Y.Z"; exit 1; }

OLD=$(python3 -c "import json; print(json.load(open('setting.json'))['version'])")
[ "$OLD" != "$NEW" ] || { echo "Already at $NEW"; exit 1; }

[ "$(git branch --show-current)" = "main" ] || { echo "Run from main"; exit 1; }
[ -z "$(git status --porcelain)" ] || { echo "Working tree not clean"; exit 1; }
git fetch -q origin main --tags
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || { echo "main is not in sync with origin/main"; exit 1; }
! git rev-parse -q --verify "refs/tags/v$NEW" >/dev/null || { echo "Tag v$NEW already exists"; exit 1; }

old_re="${OLD//./\\.}"
sed -i "s/\"version\": \"$old_re\"/\"version\": \"$NEW\"/" setting.json
sed -i "s/^version: '$old_re'/version: '$NEW'/" snap/snapcraft.yaml
# Landing fallbacks (the page fetches the real latest release at runtime)
sed -i "s/$old_re/$NEW/g" landing/index.html
sed -i "s/'v$old_re'/'v$NEW'/g" landing/js/main.js

echo "$OLD -> $NEW"
git --no-pager diff --stat
read -r -p "Commit, tag v$NEW and push? [y/N] " ok
[ "$ok" = "y" ] || { git checkout -- .; echo "Aborted, changes reverted"; exit 1; }

git commit -qam "release: v$NEW"
git tag -a "v$NEW" -m "v$NEW"
git push --atomic origin main "v$NEW"
echo "Pushed. Follow the build: https://github.com/NguyenDuc2309/klipr/actions"
