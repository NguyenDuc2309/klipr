<p align="center">
  <img src="assets/logo.png" alt="Klipr" width="128" height="128" />
</p>

<h1 align="center">Klipr</h1>

<p align="center">
  <b>Trình quản lý clipboard hiện đại cho Linux</b><br/>
  Nhẹ, nhanh, viết native bằng GTK4
</p>

<p align="center">
  <a href="README.md">English</a> · <b>Tiếng Việt</b>
</p>

<p align="center">
  <a href="https://github.com/NguyenDuc2309/klipr/releases/latest"><img src="https://img.shields.io/github/v/release/NguyenDuc2309/klipr?style=flat-square&label=version&color=blue" alt="Version" /></a>
  <a href="https://github.com/NguyenDuc2309/klipr/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/NguyenDuc2309/klipr/ci.yml?branch=main&style=flat-square&label=CI" alt="CI" /></a>
  <img src="https://img.shields.io/badge/platform-Linux-green?style=flat-square" alt="Platform" />
  <img src="https://img.shields.io/badge/GTK-4-orange?style=flat-square" alt="GTK4" />
  <img src="https://img.shields.io/badge/python-3.10+-yellow?style=flat-square" alt="Python" />
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License" /></a>
</p>

<p align="center">
  <a href="#cài-đặt">Cài đặt</a> •
  <a href="#tính-năng">Tính năng</a> •
  <a href="#sử-dụng">Sử dụng</a> •
  <a href="#cấu-hình">Cấu hình</a> •
  <a href="#hỗ-trợ-desktop">Hỗ trợ desktop</a> •
  <a href="CONTRIBUTING.vi.md">Đóng góp</a>
</p>

---

Klipr chạy ngầm và lưu lại mọi thứ bạn copy, cả chữ lẫn ảnh, để không bao giờ mất một đoạn đã copy. Không Electron,
không nặng nề: một app GTK4 nhỏ gọn, hòa hợp với desktop của bạn.

<p align="center">
  <img src="assets/home_page.png" alt="Klipr - Trang chính" width="380" />&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/setting_page.png" alt="Klipr - Cài đặt" width="380" />
</p>

## Tính năng

| Tính năng | Mô tả |
|---|---|
| **Lịch sử clipboard** | Lưu mọi đoạn chữ và ảnh bạn copy. Mục cũ nhất tự xóa theo giới hạn lịch sử. |
| **Yêu thích** | Ghim các đoạn hay dùng. Mục yêu thích không bao giờ bị tự xóa. |
| **Tìm kiếm** | Tìm tức thì trong lịch sử và yêu thích, gõ được bằng bộ gõ tiếng Việt. |
| **Ảnh** | Ảnh chụp màn hình và ảnh đã copy, có thumbnail, một click để copy lại. |
| **Trích chữ từ ảnh (AI OCR)** | Lấy chữ trong ảnh bằng Gemini hoặc API tương thích OpenAI (dùng key của bạn). |
| **Giao diện** | Tối, sáng, hoặc theo hệ thống. |
| **Khay hệ thống** | Nằm gọn trong tray, không vướng víu. |
| **Phím tắt toàn cục** | Bật/tắt Klipr từ bất cứ đâu, mặc định `Ctrl+Alt+M`. |
| **Tự khởi động** | Chạy ẩn khi đăng nhập. |

## Cài đặt

Cần Ubuntu 22.04+ / Debian 12+ hoặc distro khác có GTK 4 và Python 3.10+.

### Kho APT (Ubuntu / Debian), khuyên dùng

Bản mới tự đến qua `sudo apt upgrade`.

```bash
curl -fsSL https://nguyenduc2309.github.io/klipr/apt/klipr-archive-keyring.asc \
    | sudo gpg --dearmor -o /usr/share/keyrings/klipr-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/klipr-archive-keyring.gpg] \
https://nguyenduc2309.github.io/klipr/apt stable main" \
    | sudo tee /etc/apt/sources.list.d/klipr.list

sudo apt update
sudo apt install klipr
```

### Snap

```bash
sudo snap install klipr
```

### File `.deb` từ GitHub Releases

Tải `klipr_<version>_all.deb` ở [Releases](https://github.com/NguyenDuc2309/klipr/releases/latest)
(`all` nghĩa là một gói chạy cho mọi loại CPU, vì Klipr viết bằng Python thuần), rồi:

```bash
sudo apt install ./klipr_*_all.deb
```

Mỗi release có kèm file `SHA256SUMS` để kiểm tra: `sha256sum -c SHA256SUMS --ignore-missing`.

### Chạy từ source

Xem [CONTRIBUTING.vi.md](CONTRIBUTING.vi.md#cài-môi-trường-dev).

### Gỡ cài đặt

```bash
sudo apt remove klipr        # hoặc: sudo snap remove klipr
```

Lịch sử và cài đặt vẫn được giữ lại. Muốn xóa luôn:
`rm -rf ~/.local/share/klipr ~/.cache/klipr ~/.config/klipr ~/.config/autostart/klipr.desktop`

## Sử dụng

| Thao tác | Cách làm |
|---|---|
| Mở / ẩn | `Ctrl+Alt+M`, click icon trên tray, hoặc chạy `klipr` |
| Copy lại một mục | Click vào mục hoặc nút copy. Nội dung quay lại clipboard, sẵn sàng để dán. |
| Tìm kiếm | `Ctrl+F` |
| Thêm vào yêu thích | Nút yêu thích trên mục |
| Trích chữ từ ảnh | Nút chữ trên mục ảnh (cần nhập API key trong Cài đặt). Chữ được copy vào clipboard. |
| Thoát hẳn | Icon tray → **Quit** |

Dòng lệnh: `klipr --hidden` chạy ngầm, `klipr --toggle` hiện hoặc ẩn cửa sổ.

## Cấu hình

Bấm icon bánh răng trong app, hoặc sửa file `~/.config/klipr/setting.json`.

| Key | Mặc định | Mô tả |
|---|---|---|
| `historyLimit` | `50` | Số mục lịch sử tối đa |
| `theme` | `system` | `dark`, `light` hoặc `system` |
| `closeToTray` | `true` | Đóng cửa sổ thì ẩn xuống tray thay vì thoát |
| `autostart` | `true` | Chạy ẩn khi đăng nhập |
| `shortcut` | `Ctrl+Alt+M` | Phím tắt bật/tắt cửa sổ |
| `ocrProvider` | `gemini` | `gemini` hoặc `openai` |
| `ocrGeminiKey` / `ocrGeminiModel` | `""` / `gemini-3.1-flash-lite` | API key và model Gemini |
| `ocrOpenAIKey` / `ocrOpenAIModel` | `""` / `gpt-4o-mini` | API key và model OpenAI |
| `ocrOpenAIBaseUrl` | `https://api.openai.com/v1` | Endpoint bất kỳ tương thích OpenAI |
| `ocrNotifyOnExtract` | `true` | Hiện thông báo khi trích chữ xong |

> **Quyền riêng tư:** Klipr lưu lịch sử trên máy, không gửi đi đâu. Ảnh chỉ được gửi tới AI provider bạn cấu hình
> khi bạn bấm trích chữ. API key được lưu **dạng text thường** trong file cài đặt.

## Hỗ trợ desktop

| | Trạng thái |
|---|---|
| GNOME trên X11 | ✅ Hỗ trợ đầy đủ |
| GNOME trên Wayland | ✅ Chạy qua XWayland (Klipr ép dùng backend X11) |
| KDE Plasma | ✅ App và tray chạy tốt. Phím tắt chỉ tự đăng ký trên GNOME: tự gán `klipr --toggle` trong cài đặt phím tắt của KDE. |
| Xfce, Cinnamon, khác | ✅ App chạy được. Tray cần có StatusNotifierItem host. Phím tắt: tự gán `klipr --toggle` trong cài đặt bàn phím. |
| Tray trên GNOME | Cần extension AppIndicator (Ubuntu cài sẵn) |

Gặp lỗi? Xem [xử lý sự cố](docs/architecture.md#troubleshooting) hoặc
[mở issue](https://github.com/NguyenDuc2309/klipr/issues).

## Đóng góp

Mọi báo lỗi, bản sửa và tính năng mới đều được chào đón. Bắt đầu từ [CONTRIBUTING.vi.md](CONTRIBUTING.vi.md).
Cách app hoạt động bên trong: [docs/architecture.md](docs/architecture.md).

## Giấy phép

[MIT](LICENSE) © [Nguyen Duc](https://github.com/NguyenDuc2309)
