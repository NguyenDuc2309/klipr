# Báo cáo Khắc phục Sự cố & Tăng cường Bảo mật Hệ thống

Tài liệu này tổng hợp các vấn đề an ninh đã phát hiện, nguyên nhân gốc rễ, và các biện pháp kỹ thuật đã được thực thi để khắc phục và bảo vệ hệ thống.

---

## 1. Tổng quan Sự cố

| Vấn đề               | Triệu chứng                                               | Nguyên nhân Gốc rễ                                                                                            |
| :------------------- | :-------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------ |
| **Ransomware MySQL** | Xuất hiện database lạ `RECOVER_YOUR_DATA` đòi tiền chuộc. | Port MySQL (3307) mở public ra Internet (`0.0.0.0:3307`), mật khẩu có thể bị brute-force hoặc exploit.        |
| **Backup Dư thừa**   | 1 ngày có 2 file backup `.sql`.                           | `mysql-backup` tool backup tất cả user databases, bao gồm cả database ransomware của hacker.                  |
| **Mất Dữ liệu**      | Volume MySQL bị xóa sạch.                                 | Sử dụng lệnh `docker compose down -v` (xóa volumes) hoặc hacker xóa dữ liệu.                                  |
| **Admin App Crash**  | Log tràn ngập lỗi `ETIMEDOUT` và `returnNaN`.             | Botnet scan/tấn công trực tiếp vào IP Server qua port 8002 (bypass Cloudflare/Nginx), gây quá tải connection. |

---

## 2. Các Biện pháp Bảo mật Đã Thực thi

### A. Tường lửa & Mạng (Network Hardening)

Đã kích hoạt tường lửa UFW (Uncomplicated Firewall) để chặn tất cả các kết nối không mong muốn từ Internet.

- **Chính sách:**
  - **Chặn (Deny):** Tất cả traffic vào (Incoming) mặc định.
  - **Cho phép (Allow):** Chỉ mở 3 port thiết yếu:
    - `22/tcp` (SSH)
    - `80/tcp` (HTTP - Nginx)
    - `443/tcp` (HTTPS - Nginx)

**Lệnh đã chạy:**

```bash
# 1. Thiết lập chính sách mặc định: Chặn tất cả kết nối đi vào
ufw default deny incoming

# 2. Cho phép SSH (QUAN TRỌNG: Phải chạy trước khi enable)
ufw allow 22/tcp comment "SSH"

# 3. Cho phép Web Server (HTTP/HTTPS)
ufw allow 80/tcp comment "HTTP"
ufw allow 443/tcp comment "HTTPS"

# 4. Kích hoạt tường lửa
ufw enable

# 5. Kiểm tra lại trạng thái
ufw status verbose
```

### B. Bảo mật Docker Container (Container Hardening)

#### 1. Đóng kín Database & Cache

Loại bỏ hoàn toàn việc expose port của MySQL và Redis ra máy chủ (Host). Các service này giờ chỉ giao tiếp trong mạng nội bộ Docker (Docker Network).

- **Trước:**
  - MySQL: `0.0.0.0:3307` -> Internet truy cập được.
  - Redis: `0.0.0.0:6379` -> Internet truy cập được.
- **Sau:**
  - MySQL: Không có port mapping (Chỉ truy cập được từ BE/Backup container).
  - Redis: Không có port mapping.

#### 2. Giới hạn Ứng dụng về Localhost (Localhost Binding)

Buộc các ứng dụng (BE, FE, Admin) chỉ được lắng nghe trên địa chỉ Loopback (`127.0.0.1`).

- **Mục đích:** Ngăn chặn bot scan trực tiếp vào IP server (ví dụ: `http://1.2.3.4:8002`). Bắt buộc mọi traffic phải đi qua Nginx (đã được bảo vệ bởi Cloudflare).
- **Cấu hình `docker-compose.yml`:**
  ```yaml
  ports:
    - "127.0.0.1:8000:8000" # BE
    - "127.0.0.1:8001:8001" # FE
    - "127.0.0.1:8002:8002" # Admin
  ```

### C. Dọn dẹp Database (Cleanup)

Đã xóa bỏ cơ sở dữ liệu độc hại do hacker tạo ra.

**Lệnh đã chạy:**

```bash
docker exec mytek-mysql mysql -uroot -proot -e "DROP DATABASE IF EXISTS RECOVER_YOUR_DATA;"
```

---

## 3. Hướng dẫn Vận hành An toàn (Best Practices)

Để tránh tái diễn tình trạng mất dữ liệu hay bị tấn công, vui lòng tuân thủ:

1.  **KHÔNG BAO GIỜ** chạy lệnh với cờ `-v` nếu không muốn xóa dữ liệu:
    - ❌ `docker compose down -v` (Nguy hiểm: Xóa sạch database/redis data)
    - ✅ `docker compose down` (An toàn: Chỉ tắt container)

2.  **Backup:**
    - Hệ thống hiện tại đang tự động backup lúc **03:00 sáng** hàng ngày.
    - File backup nằm tại: `./backups/`
    - Giữ lại trong: **14 ngày**.

3.  **Khi cần truy cập Database thủ công:**
    - Không mở port ra ngoài. Hãy dùng lệnh:
      ```bash
      docker exec -it mytek-mysql mysql -uroot -proot cms
      ```
    - Hoặc nếu dùng tool (Navicat/DBeaver), hãy sử dụng tính năng **SSH Tunnel** (kết nối qua SSH port 22, sau đó trỏ tới `127.0.0.1:3306`).

4.  **Kiểm tra trạng thái bảo mật:**
    Chạy lệnh sau để đảm bảo không có port lạ nào đang mở (LISTEN) trên `0.0.0.0` ngoại trừ Nginx và SSH:
    ```bash
    ss -tlnp
    ```

---

_Tài liệu được tạo tự động sau quá trình khắc phục sự cố ngày 11/02/2026._
