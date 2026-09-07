# Klipr — Deployment & Packaging Guide

Hướng dẫn đóng gói ứng dụng Klipr cho Debian/Ubuntu (`.deb`) và Canonical Snap (`.snap`).

---

## 1. Đóng gói Debian / Ubuntu (`.deb`)

### Cài đặt môi trường build
```bash
# Bắt buộc (runtime & dpkg-deb có sẵn trên Debian/Ubuntu)
sudo apt update && sudo apt install -y python3 python3-gi python3-gi-cairo gir1.2-gtk-4.0 python3-pil

# (Tùy chọn) Nếu muốn build bằng FPM thay vì dpkg-deb mặc định:
sudo apt install -y ruby ruby-dev build-essential
sudo gem install --no-document fpm
```

### Lệnh build package
```bash
# Cú pháp: ./packaging/build.sh [VERSION]
./packaging/build.sh 1.2.7
```
*Output:* File `klipr_1.2.7_all.deb` tạo tại thư mục gốc.

### Cài đặt kiểm tra & gỡ bỏ
```bash
# Cài đặt file vừa build (tự giải quyết dependencies)
sudo apt install ./klipr_1.2.7_all.deb

# Chạy thử
klipr            # Mở cửa sổ chính
klipr --hidden   # Chạy nền trên tray

# Gỡ bỏ cài đặt
sudo apt remove klipr
```

---

## 2. Đóng gói Snap (`.snap`)

### Cài đặt Snapcraft
```bash
sudo snap install snapcraft --classic
sudo snap install lxd && sudo lxd init --auto   # môi trường build mặc định của Snapcraft
```

### Cấu hình version (nếu cần đổi phiên bản)
Sửa `version` trong file [snap/snapcraft.yaml](snap/snapcraft.yaml):
```yaml
version: '1.2.7'
```

### Lệnh build package
```bash
# Build trong container chuẩn (khuyên dùng):
snapcraft

# HOẶC build trực tiếp trên máy host / CI:
snapcraft --destructive-mode
```
*Output:* File `klipr_1.2.7_amd64.snap` tạo tại thư mục gốc.

### Cài đặt kiểm tra & gỡ bỏ
```bash
# Cài đặt file snap local (bỏ qua xác thực store)
sudo snap install --dangerous klipr_1.2.7_amd64.snap

# Cấp quyền kết nối tray icon (StatusNotifierItem/Unity7) nếu cần
sudo snap connect klipr:unity7

# Chạy thử
snap run klipr

# Gỡ bỏ cài đặt
sudo snap remove klipr
```

### Phát hành lên Snap Store (Tùy chọn)
```bash
# Đăng nhập tài khoản Snapcraft
snapcraft login

# Đăng ký tên package (chỉ thực hiện 1 lần đầu)
snapcraft register klipr

# Upload và phát hành vào kênh stable
snapcraft upload --release=stable klipr_1.2.7_amd64.snap
```

---

## 3. Cheatsheet tóm tắt lệnh

| Tác vụ | Lệnh .deb | Lệnh Snap |
|---|---|---|
| **Build** | `./packaging/build.sh 1.2.7` | `snapcraft` |
| **Cài đặt thử** | `sudo apt install ./klipr_1.2.7_all.deb` | `sudo snap install --dangerous klipr_1.2.7_amd64.snap` |
| **Chạy app** | `klipr` | `snap run klipr` |
| **Gỡ bỏ** | `sudo apt remove klipr` | `sudo snap remove klipr` |
