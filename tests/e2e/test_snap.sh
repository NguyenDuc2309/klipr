#!/bin/bash
# End-to-end test for a built .snap on a real desktop (run after removing the .deb).
# Test .snap trên desktop thật — chạy sau khi đã gỡ .deb.
#
# Usage: tests/e2e/test_snap.sh ./klipr_X.Y.Z_amd64.snap
#
# LƯU Ý QUAN TRỌNG: luôn gọi /snap/bin/klipr bằng đường dẫn tuyệt đối.
# Gọi bare `klipr` là sai: /usr/bin (nơi .deb cài) đứng TRƯỚC /snap/bin
# trong PATH, nên nếu .deb còn cài thì `klipr` khởi động bản .deb, đăng ký
# tên D-Bus io.github.nguyenduc2309.klipr chứ không phải snap.klipr, và mọi
# phép chờ snap.klipr sẽ timeout dù snap hoàn toàn bình thường.

set -u

SNAP="$(realpath "${1:?Usage: $0 path/to/klipr_X.Y.Z_amd64.snap}")"
SNAP_BIN="/snap/bin/klipr"
APP_ID="snap.klipr"
OBJECT_PATH="/snap/klipr"
LOG="/tmp/klipr-snap-test.log"

PASS=0
FAIL=0
check() {
    if [ "$1" = "0" ]; then
        echo "✅ $2"; PASS=$((PASS + 1))
    else
        echo "❌ $2"; FAIL=$((FAIL + 1))
    fi
}

kill_klipr() {
    local pids
    pids=$(pgrep -f "python3.*main.py")
    [ -n "$pids" ] && kill -9 $pids
    sleep 1
}

echo "################ TEST: $(basename "$SNAP") ################"

# ── 0. Điều kiện tiên quyết: .deb PHẢI đã gỡ ─────────────────────
echo "--- [0] Kiểm tra môi trường ---"
! dpkg -l klipr 2>/dev/null | grep -q "^ii"
check $? ".deb đã gỡ (nếu còn sẽ che mất /snap/bin/klipr)"
[ ! -e /usr/bin/klipr ]
check $? "/usr/bin/klipr không tồn tại"

# ── 1. Cài snap ───────────────────────────────────────────────────
kill_klipr
sudo snap remove --purge klipr >/dev/null 2>&1
echo "--- [1] Cài .snap ---"
sudo snap install "$SNAP" --dangerous 2>&1 | tail -1
snap list klipr >/dev/null 2>&1
check $? "snap đã cài"
[ -x "$SNAP_BIN" ]
check $? "$SNAP_BIN tồn tại"

# ── 2. Khởi động ──────────────────────────────────────────────────
echo "--- [2] Khởi động (dùng đường dẫn tuyệt đối) ---"
rm -f "$LOG"
# python3 -u không áp dụng được ở đây; ghi thẳng ra file (không qua tee/pipe)
# để tránh block buffering làm log trông như trống.
setsid "$SNAP_BIN" > "$LOG" 2>&1 < /dev/null &
disown

READY=""
for i in $(seq 1 30); do
    sleep 1
    if gdbus call --session --dest org.freedesktop.DBus \
        --object-path /org/freedesktop/DBus \
        --method org.freedesktop.DBus.GetNameOwner "'$APP_ID'" >/dev/null 2>&1; then
        READY="$i"
        break
    fi
done
[ -n "$READY" ]
check $? "D-Bus name '$APP_ID' đăng ký được (sau ${READY:-30}s)"

# gdbus trả về "(uint32 74319,)" — phải bóc đúng số sau chữ uint32.
# `grep -oE '[0-9]+'` là SAI: nó bắt cả số 32 trong "uint32", làm $PID
# thành hai dòng, khiến `ps -p` lỗi cú pháp và mọi phép kiểm tra
# "process còn sống không" trả về sai (tưởng đã chết ngay lập tức).
PID=$(gdbus call --session --dest org.freedesktop.DBus \
    --object-path /org/freedesktop/DBus \
    --method org.freedesktop.DBus.GetConnectionUnixProcessID "'$APP_ID'" 2>/dev/null \
    | sed -E 's/.*uint32 ([0-9]+).*/\1/')
[ -n "$PID" ]
check $? "lấy được PID thật sở hữu D-Bus name (PID=$PID)"
[ -n "$PID" ] && ps -p "$PID" -o cmd --no-headers

# ── 3. Toggle ─────────────────────────────────────────────────────
echo "--- [3] D-Bus toggle ---"
gdbus call --session --dest "$APP_ID" --object-path "$OBJECT_PATH" \
    --method org.gtk.Actions.Activate toggle-window '[]' '{}' >/dev/null 2>&1
check $? "toggle-window phản hồi"
sleep 1

# ── 4. RAM ────────────────────────────────────────────────────────
if [ -n "$PID" ] && [ -f "/proc/$PID/smaps_rollup" ]; then
    echo "--- [4] RAM ---"
    RSS=$(ps -o rss= -p "$PID" | tr -d ' ')
    PSS=$(grep "^Pss:" "/proc/$PID/smaps_rollup" | awk '{print $2}')
    echo "  RSS=${RSS}KB  PSS=${PSS}KB"
fi

# ── 5. Fix loop-device: snap remove khi app đang chạy nền ──────────
echo "--- [5] snap remove trong khi app ĐANG CHẠY (kịch bản leak gốc) ---"
sudo snap remove klipr

echo "    đợi tối đa 15s cho app tự phát hiện và tự thoát..."
GONE=""
for i in $(seq 1 150); do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        GONE=$((i * 100))
        break
    fi
    sleep 0.1
done
[ -n "$GONE" ]
check $? "app TỰ THOÁT sau ${GONE:-15000}ms"
[ -z "$GONE" ] && kill -9 "$PID" 2>/dev/null

! losetup -a 2>/dev/null | grep -q klipr
check $? "không rò rỉ loop device"

echo "--- log cuối (lý do app thoát) ---"
tail -3 "$LOG"

echo ""
echo "################ KẾT QUẢ: $PASS PASS / $FAIL FAIL ################"
