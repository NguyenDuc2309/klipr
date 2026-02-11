# Hướng dẫn Restore Database MySQL từ File Backup

## Thông tin cấu hình

| Thông tin       | Giá trị                 |
| --------------- | ----------------------- |
| Container MySQL | `mytek-mysql`           |
| Database        | `cms`                   |
| User            | `root`                  |
| Password        | `root`                  |
| Thư mục backup  | `./backups/`            |
| Backup tool     | `databack/mysql-backup` |

## Các bước Restore

### Bước 1: Khởi động MySQL container

```bash
docker compose up -d mysql
```

### Bước 2: Kiểm tra MySQL đã sẵn sàng

```bash
docker exec mytek-mysql mysqladmin ping -uroot -proot --silent
```

> Kết quả mong đợi: `mysqld is alive`

### Bước 3: Giải nén file backup

File backup có định dạng `.tgz`, cần giải nén trước khi restore.

```bash
# Xem nội dung file backup (không giải nén)
tar -tzf ./backups/<TÊN_FILE_BACKUP>.tgz

# Giải nén vào thư mục tạm
mkdir -p ./restore_tmp
tar -xzf ./backups/<TÊN_FILE_BACKUP>.tgz -C ./restore_tmp/
```

**Ví dụ:**

```bash
tar -xzf ./backups/db_backup_2026-02-07T03:00:02Z.tgz -C ./restore_tmp/
```

Sau khi giải nén sẽ có 2 file:

- `cms_<TIMESTAMP>.sql` — File SQL chứa dữ liệu database `cms`
- `RECOVER_YOUR_DATA_<TIMESTAMP>.sql` — File hỗ trợ recover

### Bước 4: Restore database

```bash
docker exec -i mytek-mysql mysql -uroot -proot < ./restore_tmp/cms_<TIMESTAMP>.sql
```

**Ví dụ:**

```bash
docker exec -i mytek-mysql mysql -uroot -proot < ./restore_tmp/cms_2026-02-07T03:00:02Z.sql
```

### Bước 5: Kiểm tra kết quả

```bash
# Kiểm tra danh sách tables
docker exec mytek-mysql mysql -uroot -proot -e "USE cms; SHOW TABLES;"

# Kiểm tra số lượng record trong một table
docker exec mytek-mysql mysql -uroot -proot -e "USE cms; SELECT COUNT(*) FROM product;"
```

### Bước 6: Dọn dẹp file tạm

```bash
rm -rf ./restore_tmp
```

### Bước 7: Khởi động lại toàn bộ services

```bash
docker compose up -d
```

---

## Lệnh nhanh (One-liner)

Nếu muốn chạy nhanh trong 1 lần, thay `<BACKUP_FILE>` và `<SQL_FILE>` tương ứng:

```bash
docker compose up -d mysql && \
sleep 10 && \
mkdir -p ./restore_tmp && \
tar -xzf ./backups/<BACKUP_FILE>.tgz -C ./restore_tmp/ && \
docker exec -i mytek-mysql mysql -uroot -proot < ./restore_tmp/<SQL_FILE>.sql && \
docker exec mytek-mysql mysql -uroot -proot -e "USE cms; SHOW TABLES;" && \
rm -rf ./restore_tmp && \
docker compose up -d
```

**Ví dụ:**

```bash
docker compose up -d mysql && \
sleep 10 && \
mkdir -p ./restore_tmp && \
tar -xzf ./backups/db_backup_2026-02-07T03:00:02Z.tgz -C ./restore_tmp/ && \
docker exec -i mytek-mysql mysql -uroot -proot < ./restore_tmp/cms_2026-02-07T03:00:02Z.sql && \
docker exec mytek-mysql mysql -uroot -proot -e "USE cms; SHOW TABLES;" && \
rm -rf ./restore_tmp && \
docker compose up -d
```

---

## Danh sách file backup hiện có

Kiểm tra các file backup có sẵn:

```bash
ls -lh ./backups/
```

> **Lưu ý:** Backup được tạo tự động hàng ngày lúc **03:00 (GMT+7)** và giữ lại trong **14 ngày**.
