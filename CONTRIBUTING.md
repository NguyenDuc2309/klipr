# Contributing to Klipr

**English** · [Tiếng Việt](CONTRIBUTING.vi.md)

Thanks for helping! Bug reports, fixes, features and docs are all welcome.

- **Found a bug?** [Open an issue](https://github.com/NguyenDuc2309/klipr/issues) with your distro + version,
  desktop (GNOME/KDE…, X11/Wayland), how you installed Klipr (APT/Snap/.deb/source), steps to reproduce, and the
  terminal output of `klipr` if it crashed.
- **Want to add a feature?** Open an issue first so we can agree on the approach before you write code.

## Development setup

Klipr is Python + GTK4 through PyGObject. The easiest setup uses your distro's packages, no pip needed:

```bash
sudo apt install git python3 python3-gi python3-gi-cairo gir1.2-gtk-4.0 python3-pil
git clone https://github.com/NguyenDuc2309/klipr.git
cd klipr
python3 src/main.py
```

Run it **from the repo root**: that way it uses the repo's `setting.json` as its defaults.

> **Quit any installed Klipr first** (tray → Quit). Klipr is single-instance: if the installed copy is running,
> `python3 src/main.py` just shows *its* window and exits, and you'll be testing the wrong code.
> The dev copy uses your real data in `~/.local/share/klipr` and `~/.config/klipr`.

<details>
<summary>Prefer a virtualenv?</summary>

Reuse the system PyGObject (building it with pip needs C headers):

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
```

Or build everything from pip:

```bash
sudo apt install libgirepository-2.0-dev libcairo2-dev pkg-config python3-dev
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
</details>

## Project layout

```
src/            the app (entry point: src/main.py) — see docs/architecture.md
assets/         logos and README screenshots
setting.json    bundled default settings + the app version (source of truth)
packaging/      .deb inputs: build.sh, launcher, .desktop file
snap/           snapcraft recipe (built by Launchpad)
debian/         Debian-archive packaging (separate from CI, maintainer only)
landing/        website on GitHub Pages, includes the APT repo (landing/apt/)
tests/          automated tests (run in CI) + tests/e2e/ manual tests on a real desktop
scripts/        maintainer tools: release, APT publish, benchmarks, debugging
docs/           architecture notes
```

## Before you open a PR

Run the same checks CI runs:

```bash
# 1. Lint: syntax errors and undefined names
python3 -m compileall -q src tests scripts
pipx run ruff check src tests scripts --select E9,F63,F7,F82

# 2. GUI tests under a virtual X server (sudo apt install xvfb)
xvfb-run -a dbus-run-session -- python3 tests/smoke_test.py
xvfb-run -a dbus-run-session -- python3 tests/test_keyboard.py

# 3. Build the package and try it
./packaging/build.sh
sudo apt install ./klipr_*_all.deb
```

For bigger changes, the end-to-end tests exercise the installed app on your real desktop (they need `sudo`):
`tests/e2e/test_deb.sh ./klipr_<ver>_all.deb` and `tests/e2e/test_snap.sh ./klipr_<ver>_amd64.snap`.

### Rules that bite

- **New Python file? Add it to `packaging/build.sh`.** The script copies files one by one. If you forget, the
  `.deb` ships without it and crashes on import. CI fails with `missing in .deb: …` when this happens.
- **Don't hard-code GSettings schemas.** `Gio.Settings.new()` on a schema that isn't installed kills the process
  (it can't be caught). Use a lookup like `utils.gnome_interface_settings()`.
- **Don't bump the version.** The maintainer does it when cutting a release.
- **Don't commit build output** (`*.deb`, `*.snap`, `build/`, `parts/`…). It's git-ignored; keep it that way.

## Pull requests

1. Fork, then create a branch: `feat/<short-name>`, `fix/<short-name>`, `docs/…`.
2. Write commits as [Conventional Commits](https://www.conventionalcommits.org/): `feat: …`, `fix(tray): …`,
   `docs: …`, `ci: …`, `chore: …`. One logical change per commit.
3. Keep the PR focused. Describe **what** changed and **why**, and how you tested it (desktop + X11/Wayland).
   Screenshots for UI changes.
4. **CI must be green before merge.** It runs lint → build `.deb` → install + GUI tests on Ubuntu 22.04 and 24.04.
   CI only runs when app code changes, so docs-only PRs have no checks. That's expected.

## License

By contributing you agree that your contributions are licensed under the [MIT License](LICENSE).
