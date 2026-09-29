# Releasing Klipr

Maintainer guide. Klipr ships through four channels:

| Channel | How it gets updated |
|---|---|
| GitHub Releases (`.deb`) | **Automatic**: CI builds, tests and publishes when a version tag is pushed |
| Snap Store | **Automatic** to `edge` via Launchpad; promote to `stable` by hand |
| APT repo (`landing/apt/`) | **Manual**: `scripts/publish_apt.sh`, needs the signing key |
| Landing page | **Automatic**: GitHub Pages redeploys on changes under `landing/` |

## 1. Cut a release

```bash
git checkout main && git pull
scripts/release.sh 1.2.8
```

The script refuses to run unless you are on an up-to-date, clean `main`. It then:

1. bumps the version in `setting.json` (source of truth), `snap/snapcraft.yaml` and the fallbacks in
   `landing/index.html` / `landing/js/main.js`;
2. shows the diff and asks for confirmation;
3. commits `release: v1.2.8`, creates tag `v1.2.8` and pushes both.

`.github/workflows/release.yml` then:

1. fails if the tag does not match `setting.json` and `snapcraft.yaml` (don't tag by hand);
2. re-runs the whole CI (lint → build → install + GUI tests on Ubuntu 22.04 / 24.04);
3. publishes the GitHub Release, marked **latest**, with `klipr_1.2.8_all.deb`, `SHA256SUMS` and generated notes.

Docs need no version bump: the README badge and the landing page read the latest release from GitHub.

### What CI runs and when

`ci.yml` runs on pull requests and pushes to `main` **only when app code changes** (`src/`, `assets/`,
`packaging/`, `tests/`, `scripts/`, `setting.json`, `requirements.txt`). Docs, `landing/`, `debian/` and `snap/`
changes don't trigger it. Releases only happen on tags, never on merges.

**Wait for CI to be green before merging a PR.**

## 2. APT repository

Served from `landing/apt/` on GitHub Pages (`https://nguyenduc2309.github.io/klipr/apt/`). It is plain static files:
a `Packages` index, a pool of `.deb`s and a signed `Release`.

After a release, from a machine that has the signing key at `~/.klipr-signing`:

```bash
scripts/publish_apt.sh 1.2.8
git add landing/apt && git commit -m "apt: publish klipr 1.2.8" && git push
```

The script builds the `.deb`, copies it into `pool/main/k/klipr/`, regenerates `Packages(.gz)`, regenerates and
signs `Release`, `Release.gpg` and `InRelease`, and trims the pool to the 3 newest builds. Pages redeploys on push.

This step stays manual on purpose: automating it would mean putting the private signing key in GitHub Secrets, and
anyone who compromises the repo could then sign packages that every user's `apt` trusts.

### Verify before announcing

```bash
python3 -m http.server 8899 --directory landing/apt &

D=/tmp/apt-verify; rm -rf "$D"
mkdir -p "$D/etc/apt/keyrings" "$D/var/lib/dpkg"; touch "$D/var/lib/dpkg/status"
gpg --dearmor < landing/apt/klipr-archive-keyring.asc > "$D/etc/apt/keyrings/klipr.gpg"
echo "deb [signed-by=$D/etc/apt/keyrings/klipr.gpg] http://localhost:8899 stable main" > "$D/klipr.list"

apt-get -o Dir="$D" -o Dir::State::status="$D/var/lib/dpkg/status" \
    -o Dir::Etc::sourcelist="$D/klipr.list" \
    -o Dir::Etc::sourceparts=/dev/null -o Dir::Etc::main=/dev/null update
apt-cache -o Dir="$D" -o Dir::State::status="$D/var/lib/dpkg/status" show klipr   # new version?

kill %1
```

A signature error means signing failed or the key doesn't match `klipr-archive-keyring.asc`. Fix it before pushing.

### Signing key

A dedicated key, not the maintainer's personal one:

```
uid           Klipr APT Repository <klipr-repo@nguyenduc2309.github.io>
fingerprint   1106 754D 164F AC47 3A24  BEFA 7A92 D5BE 7F75 0CF3
type          RSA 4096, expires 2029-08-18
```

- Public half (committed): `landing/apt/klipr-archive-keyring.asc` and `.gpg`.
- Private half (**never in git**): `~/.klipr-signing/`, its own `GNUPGHOME`, `chmod 700`, no passphrase so the
  script can sign unattended. Back it up off the machine. If it is lost, existing users keep working but no new
  release can be signed with the same identity.

**Revoke** (suspected leak):

```bash
GNUPGHOME=~/.klipr-signing gpg --import ~/.klipr-signing/openpgp-revocs.d/*.rev
GNUPGHOME=~/.klipr-signing gpg --armor --export 7A92D5BE7F750CF3 > landing/apt/klipr-archive-keyring.asc
```

**Rotate / regenerate:**

```bash
mkdir -p ~/.klipr-signing && chmod 700 ~/.klipr-signing
cat > /tmp/gpg-gen.batch <<'EOF'
Key-Type: RSA
Key-Length: 4096
Name-Real: Klipr APT Repository
Name-Email: klipr-repo@nguyenduc2309.github.io
Expire-Date: 3y
%no-protection
%commit
EOF
GNUPGHOME=~/.klipr-signing gpg --batch --generate-key /tmp/gpg-gen.batch && rm /tmp/gpg-gen.batch

KEYID=$(GNUPGHOME=~/.klipr-signing gpg --list-secret-keys --with-colons | awk -F: '/^sec/{print $5; exit}')
echo "$KEYID" > ~/.klipr-signing/keyid.txt
GNUPGHOME=~/.klipr-signing gpg --export-secret-keys --armor "$KEYID" > ~/.klipr-signing/klipr-apt-signing-key-PRIVATE.asc
chmod 600 ~/.klipr-signing/klipr-apt-signing-key-PRIVATE.asc
GNUPGHOME=~/.klipr-signing gpg --export --armor "$KEYID" > landing/apt/klipr-archive-keyring.asc
GNUPGHOME=~/.klipr-signing gpg --export "$KEYID" > landing/apt/klipr-archive-keyring.gpg
```

Users don't trust a rotated key automatically: announce it and ask them to re-run the install steps in the README.

### Repo layout

```
landing/apt/
├── klipr-archive-keyring.asc / .gpg   # public key
├── pool/main/k/klipr/klipr_<ver>_all.deb
└── dists/stable/
    ├── Release, Release.gpg, InRelease
    └── main/binary-all/Packages(.gz)
```

One suite, one component, one architecture (`all`, since Klipr is pure Python).

## 3. Snap

Launchpad builds `snap/snapcraft.yaml` on every push to `main` and releases it to the `edge` channel. The version
comes from `snapcraft.yaml`, which `scripts/release.sh` bumps. Promote after testing:

```bash
snapcraft release klipr <revision> stable     # or drag it in the Releases tab on snapcraft.io
```

### Building locally

```bash
sudo snap install snapcraft --classic
sudo snap install lxd && sudo lxd init --auto
snapcraft                        # writes parts/ stage/ prime/ (git-ignored)
```

### Test before promoting to stable

```bash
sudo snap install ./klipr_<ver>_amd64.snap --dangerous
tests/e2e/test_snap.sh ./klipr_<ver>_amd64.snap
```

Strict confinement is what most likely breaks, so check specifically:

- clipboard read/write;
- tray icon (`unity7` plug; watch `journalctl --user -f` for AppArmor denials on the session bus);
- global shortcut (registered through `gsettings` from inside the sandbox);
- data paths are remapped to `~/snap/klipr/current/`.

`scripts/compare_packaging.sh <deb> <snap>` benchmarks the two formats (startup, RAM, toggle latency, clean quit).

## 4. Debian archive

Separate, slow path through mentors.debian.net. See [debian.md](debian.md).
