# Đóng góp cho Klipr

[English](CONTRIBUTING.md) · **Tiếng Việt**

Cảm ơn bạn đã muốn góp sức! Báo lỗi, sửa lỗi, tính năng mới hay tài liệu đều được chào đón.

- **Gặp lỗi?** [Mở issue](https://github.com/NguyenDuc2309/klipr/issues), ghi rõ distro + phiên bản, desktop
  (GNOME/KDE…, X11/Wayland), cách cài Klipr (APT/Snap/.deb/source), các bước tái hiện, và output terminal khi chạy
  `klipr` nếu app bị crash.
- **Muốn thêm tính năng?** Mở issue trước để thống nhất hướng làm rồi mới viết code.

## Cài môi trường dev

Klipr viết bằng Python + GTK4 qua PyGObject. Cách dễ nhất là dùng gói của distro, không cần pip:

```bash
sudo apt install git python3 python3-gi python3-gi-cairo gir1.2-gtk-4.0 python3-pil
git clone https://github.com/NguyenDuc2309/klipr.git
cd klipr
python3 src/main.py
```

Chạy **từ thư mục gốc của repo**: khi đó app lấy `setting.json` của repo làm cấu hình mặc định.

> **Thoát Klipr đã cài trước** (tray → Quit). Klipr chỉ cho chạy một instance: nếu bản đã cài đang chạy,
> `python3 src/main.py` chỉ bật cửa sổ của *bản đó* rồi thoát, và bạn sẽ test nhầm code.
> Bản dev dùng dữ liệu thật của bạn ở `~/.local/share/klipr` và `~/.config/klipr`.

<details>
<summary>Muốn dùng virtualenv?</summary>

Dùng lại PyGObject của hệ thống (build PyGObject bằng pip cần header C):

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
```

Hoặc cài hết bằng pip:

```bash
sudo apt install libgirepository-2.0-dev libcairo2-dev pkg-config python3-dev
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
</details>

## Cấu trúc thư mục

```
src/            code app (entry point: src/main.py) — xem docs/architecture.md
assets/         logo và ảnh chụp cho README
setting.json    cấu hình mặc định đóng kèm app + version của app (nguồn chuẩn duy nhất)
packaging/      đầu vào để build .deb: build.sh, launcher, file .desktop
snap/           recipe snapcraft (Launchpad tự build)
debian/         đóng gói cho kho Debian chính thức (tách khỏi CI, chỉ maintainer dùng)
landing/        website trên GitHub Pages, chứa luôn kho APT (landing/apt/)
tests/          test tự động (chạy trong CI) + tests/e2e/ test tay trên desktop thật
scripts/        tool cho maintainer: release, publish APT, benchmark, debug
docs/           tài liệu kiến trúc
```

## Trước khi mở PR

Chạy đúng những gì CI sẽ chạy:

```bash
# 1. Lint: lỗi cú pháp, tên biến không tồn tại
python3 -m compileall -q src tests scripts
pipx run ruff check src tests scripts --select E9,F63,F7,F82

# 2. Test GUI trên X server ảo (sudo apt install xvfb)
xvfb-run -a dbus-run-session -- python3 tests/smoke_test.py
xvfb-run -a dbus-run-session -- python3 tests/test_keyboard.py

# 3. Build gói và cài thử
./packaging/build.sh
sudo apt install ./klipr_*_all.deb
```

Với thay đổi lớn, chạy thêm test end-to-end trên desktop thật (cần `sudo`):
`tests/e2e/test_deb.sh ./klipr_<ver>_all.deb` và `tests/e2e/test_snap.sh ./klipr_<ver>_amd64.snap`.

### Những lỗi hay gặp

- **Thêm file Python mới? Khai báo nó trong `packaging/build.sh`.** Script copy từng file một. Quên là `.deb`
  thiếu file và crash lúc import. CI sẽ báo `missing in .deb: …` nếu bạn quên.
- **Không gọi thẳng GSettings schema.** `Gio.Settings.new()` với schema chưa cài sẽ giết cả process, không
  `try/except` được. Hãy tra schema trước, như `utils.gnome_interface_settings()`.
- **Không tự sửa version.** Maintainer sẽ bump khi release.
- **Không commit file build** (`*.deb`, `*.snap`, `build/`, `parts/`…). Chúng đã nằm trong `.gitignore`, giữ nguyên như vậy.

## Pull request

1. Fork, tạo nhánh: `feat/<tên-ngắn>`, `fix/<tên-ngắn>`, `docs/…`.
2. Commit theo [Conventional Commits](https://www.conventionalcommits.org/): `feat: …`, `fix(tray): …`,
   `docs: …`, `ci: …`, `chore: …`. Mỗi commit là một thay đổi logic.
3. PR tập trung vào một việc. Mô tả **thay đổi gì**, **tại sao**, và đã test thế nào (desktop + X11/Wayland).
   Có ảnh chụp nếu đổi UI.
4. **CI phải xanh rồi mới merge.** CI chạy lint → build `.deb` → cài + test GUI trên Ubuntu 22.04 và 24.04.
   CI chỉ chạy khi đổi code app, nên PR chỉ sửa docs sẽ không có check nào. Đó là bình thường.

## Giấy phép

Khi đóng góp, bạn đồng ý rằng phần đóng góp được cấp phép theo [MIT License](LICENSE).
