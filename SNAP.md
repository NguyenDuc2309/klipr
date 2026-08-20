# Publishing Klipr to the Snap Store (`sudo snap install klipr`)

This is what gets a real one-command, zero-setup install: every stock Ubuntu
already trusts the Snap Store, so once `klipr` is published here,
`sudo snap install klipr` works on a machine that has never heard of the
project. Compare with `PUBLISH.md` (the self-hosted APT repo), where a machine
has to be told the repository exists before `apt install` can find anything.

## Why not Debian

Klipr's ITP was filed as [#1144904](https://bugs.debian.org/1144904) and
closed the same day by a Debian Developer: *"Self-packaged toy project with no
users. Closing."* That is not a packaging defect — the `debian/` directory in
this repo builds clean and lints clean — it is Debian's social gate: a
package is a standing maintenance commitment, and an author packaging their
own project with no outside adoption gets filtered before a technical review
even starts. That path stays closed until there is a real user base to point
to.

Snap's gate is different in kind. The Store runs a manual review on
registering a new snap **name**, but it is a fraud check — added in response
to cryptocurrency scams abusing the old auto-approve interface — not a
judgment on the project's maturity or user count. A correctly described
open-source app with no financial claims clears it; Canonical says roughly two
business days.

## Status

`snap/snapcraft.yaml` is written and has been **built successfully** —
`klipr_1.2.4_amd64.snap`, 32MB — confirming the recipe itself is correct. It
has not been installed or run on a real desktop, because this environment has
no GTK4 session to test tray, clipboard or the global shortcut against. Do
that before publishing past a beta channel.

## 1. Building

This needs `snapcraft`, which normally needs a full LXD or Multipass VM as its
build backend. Root wasn't available in this environment, so the build below
instead used Canonical's official OCI image
(`ghcr.io/canonical/snapcraft:8_core24`, see
[canonical/snapcraft-rocks](https://github.com/canonical/snapcraft-rocks))
under Docker with `--destructive-mode` — the mode the rock's own maintainers
recommend for exactly this, a short-lived CI-style container. If you have a
normal Ubuntu desktop with `sudo`, skip all of this and just run:

```bash
sudo snap install snapcraft --classic
sudo snap install lxd && sudo lxd init --auto
snapcraft
```

If you want to reproduce the Docker route instead, know that this specific
rock image (`8_core24`, pulled 2026-08-20) has two real bugs, not anything
about this recipe:

1. **The `gnome` extension's own data files are missing.** Snapcraft's `gnome`
   extension looks for command-chain wrapper scripts at
   `/usr/share/snapcraft/extensions/desktop/command-chain`; in this rock that
   directory doesn't exist, while the actual files sit at
   `/usr/lib/python3.12/site-packages/extensions/desktop/command-chain`. A
   symlink fixes it.
2. **`craftctl` isn't on `PATH`** when running build scriptlets in
   `--destructive-mode`; it lives at `/usr/libexec/snapcraft/craftctl` and has
   to be added explicitly.

```bash
docker pull ghcr.io/canonical/snapcraft:8_core24

# from the repo root, with only the app's own files needed at build time —
# landing/, debian/ etc. are irrelevant to the snap and were excluded here
cat > /tmp/snap-build.sh <<'EOF'
set -e
mkdir -p /usr/share/snapcraft
rm -rf /usr/share/snapcraft/extensions
ln -sfn /usr/lib/python3.12/site-packages/extensions /usr/share/snapcraft/extensions
apt-get update -qq
export PATH="/usr/libexec/snapcraft:$PATH"
cd /project
snapcraft pack --destructive-mode --verbosity=verbose
EOF

docker run --rm -v "$PWD":/project -v /tmp/snap-build.sh:/fix.sh \
  --entrypoint sh ghcr.io/canonical/snapcraft:8_core24 /fix.sh
```

The container runs as root and writes `parts/`, `stage/`, `prime/` into the
project directory — `chown -R` them back, or `git clean -fdx` them out, when
done; they aren't meant to be committed.

## 2. Test locally before publishing anything

```bash
sudo snap install ./klipr_1.2.4_amd64.snap --dangerous
klipr
```

Check specifically, since these are what strict confinement is most likely to
break and the build above could not exercise:

- **Clipboard read/write** — the core feature.
- **Tray icon** — `unity7` is the plug added for StatusNotifierItem; if the
  icon never appears, check `journalctl --user -f` while launching for
  AppArmor denials on the session bus.
- **Global shortcut** — the `.deb` registers it via `gsettings` as a GNOME
  custom keybinding; confirm that still works from inside the sandbox.
- **Settings and history paths** — strict confinement remaps
  `~/.config/klipr/` and `~/.local/share/klipr/` under
  `~/snap/klipr/current/...`; make sure nothing assumes the unsandboxed paths
  from `CLAUDE.md`.

`sudo snap remove klipr` between attempts.

## 3. Publish

Needs your own Ubuntu One / Snapcraft account — not something to do on your
behalf:

```bash
snapcraft login
snapcraft register klipr
snapcraft upload klipr_1.2.4_amd64.snap --release=beta
```

Given the fraud-review change, expect roughly two business days on
`register` for a new name before upload is accepted. Release to `beta` first,
have a few people actually run it, then `snapcraft release klipr <revision>
stable`.

## 4. Once it's live

Confirm from a machine that never touched this repo:

```bash
sudo snap install klipr
```

That should be the whole install experience. Tell me once it's confirmed and
the landing page's install command gets switched over to it — right now it
still points at the APT repository, which stays accurate until this is
actually live in the Store.
