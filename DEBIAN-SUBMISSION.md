# Submitting Klipr to Debian

Getting into Debian is what makes plain `sudo apt install klipr` work on a
machine that has never heard of this project — the same reason `sudo apt
install copyq` works today. Ubuntu does not take submissions directly; it
syncs from Debian, so Debian is the entry point and Ubuntu follows on its
next release cycle.

The `debian/` directory in this repository is the packaging source. It was
written against Debian Policy 4.7.4 and debhelper compat 13.

**What has and has not been verified.** The machine this was written on is
Ubuntu 22.04 with no root access, so `debhelper` and `dh-python` could not be
installed and **the package has never actually been built or run through
lintian.** What *was* checked, and passes: `desktop-file-validate` on the
desktop entry, `dpkg-parsechangelog` on the changelog, DEP-5 parsing of
`debian/copyright`, YAML parsing of `debian/upstream/metadata`, groff
rendering of the manpage with `--warnings` (clean), `make -n` on every
`debian/rules` override under both the default and `nocheck` profiles, and a
staged replica of the install tree confirming that `setting.json`, both CSS
files and both logos resolve from `/usr/share/klipr` exactly where the code
looks for them. Treat the first real `sbuild` run as the point where unknown
problems surface.

---

## Blockers to clear before uploading

These will be raised in review.

### 1. ITP bug number

`debian/changelog` says `Closes: #nnnnnn`. File the Intent To Package bug
first and substitute the real number:

```bash
reportbug --email nguyenminhduc230903@gmail.com wnpp
```

Choose `ITP`, package `klipr`. The bug number comes back by mail; put it in
the changelog. Nothing can be uploaded to mentors before this exists, because
the RFS has to reference it.

The signing key is already in place and needs no change: it is
`rsa4096/11C48069FB3AA8E8`, whose user ID
`Nguyen Duc <nguyenminhduc230903@gmail.com>` matches the `Maintainer` field in
both `debian/control` and `debian/changelog` exactly, which is what `debsign`
and mentors check.

### 2. X11-only is worth a sentence to your sponsor

`src/main.py` sets `GDK_BACKEND=x11` unconditionally, so on Wayland the app
runs through XWayland. This is documented in the manpage under NOTES and is
not a blocker, but expect to be asked about it.

---

## Building the source package

You need a Debian sid environment. On a non-Debian host use a container or a
`sbuild`/`pbuilder` chroot; the packaging assumes tools that Ubuntu 22.04 does
not ship at the required versions.

```bash
sudo apt install devscripts dpkg-dev debhelper dh-python \
                 desktop-file-utils lintian sbuild piuparts \
                 dput-ng reportbug
```

`devscripts` is what provides `debuild`, `debsign` and `uscan`; `dput-ng`
provides `dput` together with a ready-made mentors profile.

The upstream tarball has to be repacked, because the GitHub tag tarball
contains `landing/apt/` — the project's own APT repo, including a committed
`.deb`, a `Packages.gz` and a dearmoured keyring. Shipping prebuilt binaries
in a Debian source package gets it rejected at the NEW queue. `debian/watch`
and the `Files-Excluded` field in `debian/copyright` handle this together, and
that repack is why the version is `1.2.4+ds-1` rather than `1.2.4-1`.

```bash
# fetch and repack the upstream tarball in one step
uscan --verbose --download-current-version

# build binaries locally to test that the package actually works
dpkg-buildpackage -us -uc

# or, the way it should really be checked, in a clean sid chroot
sbuild -d unstable
```

The binary build is for your own testing. What gets uploaded to mentors is the
source-only build described below.

Then look at the result critically:

```bash
lintian -I --pedantic ../klipr_1.2.4+ds-1_amd64.changes
piuparts ../klipr_1.2.4+ds-1_all.deb        # install/upgrade/purge cleanliness
autopkgtest ../klipr_1.2.4+ds-1_all.deb -- null
```

`debian/tests/smoke` is the autopkgtest: it imports the installed private
modules under `xvfb`, builds the main window once, and asserts that the
packaged `setting.json` is found. It has never been executed — expect to
iterate on it.

Also confirm the watch file actually resolves, since GitHub tag layouts vary:

```bash
uscan --verbose --dry-run
```

## Uploading to mentors and finding a sponsor

There is no upload button on the website. mentors.debian.net takes packages
only over `dput`/`dupload` from the command line, so an account with an empty
"My packages" list is the expected state until the first upload goes through.

Mentors keeps the *source* package, not binaries, so build source-only. `-sa`
includes the `.orig.tar.xz`, which is required on a first upload:

```bash
debuild -S -sa
```

That produces the four files mentors wants, next to the source tree:
`klipr_1.2.4+ds-1.dsc`, `klipr_1.2.4+ds.orig.tar.xz`,
`klipr_1.2.4+ds-1.debian.tar.xz` and `klipr_1.2.4+ds-1_source.changes`.

Then:

1. Register at <https://mentors.debian.net> and paste your **public** key into
   the control panel — the upload is rejected if the signature does not match
   a key registered there. Export it with:

   ```bash
   gpg --armor --export 11C48069FB3AA8E8
   ```

   Also push it to a keyserver so a sponsor can find it:
   `gpg --keyserver keys.openpgp.org --send-keys 11C48069FB3AA8E8`

2. Configure the upload target. `dput-ng` already ships a `mentors` profile in
   `/usr/share/dput-ng/profiles/`, so with it installed nothing needs writing.
   Only the older `dput` needs `~/.dput.cf`:

   ```ini
   [mentors]
   fqdn = mentors.debian.net
   incoming = /upload
   method = https
   allow_unsigned_uploads = 0
   progress_indicator = 2
   allowed_distributions = .*
   ```

3. Sign and upload:

   ```bash
   debsign ../klipr_1.2.4+ds-1_source.changes
   dput mentors ../klipr_1.2.4+ds-1_source.changes
   ```

   The importer runs roughly every 15 minutes; the package then appears under
   "My packages" and you get mail.

4. On the package page, turn on **"Needs a sponsor"**.
5. File an RFS (request for sponsorship) bug against the
   `sponsorship-requests` pseudo-package — the package page generates a
   template — linking the mentors page and the ITP number.

A Debian Developer then reviews it. Expect several rounds of comments; a
lintian-clean package with a working autopkgtest is what makes a sponsor
likely to pick it up. After they upload, the package sits in the NEW queue
while ftpmaster checks licensing, and only then enters unstable.

## What happens after that

`unstable` → migrates to `testing` after roughly ten days without release
critical bugs → Ubuntu imports from testing during its next cycle. Realistic
end-to-end time for a first package with no prior relationship with a sponsor
is months, not weeks. Until that lands, the self-hosted APT repository
documented in `PUBLISH.md` stays the way people install Klipr, and the landing
page keeps pointing at it.

## Layout notes

Klipr's modules are private to the application rather than an importable
library, so they go to `/usr/share/klipr` — where Debian Python Policy puts
private modules for an `Architecture: all` package — and `debian/rules` calls
`dh_python3 /usr/share/klipr` so that directory still gets byte-compiled and
still feeds `${python3:Depends}`.

`gsettings` is only a `Recommends` (via `libglib2.0-bin`) rather than a
`Depends`: it is needed to register the global shortcut and to read the
desktop colour scheme, but both call sites already handle its absence, and the
program is fully usable without it.
