#!/bin/bash
# Benchmark the SAME version packaged as .deb vs .snap: errors, RAM (RSS/PSS),
# startup time, toggle latency, clean quit.
# So sánh cùng một version giữa .deb và .snap. Cần sudo, chạy trong terminal thật:
#   scripts/compare_packaging.sh ./klipr_X.Y.Z_all.deb ./klipr_X.Y.Z_amd64.snap
#
# Log chi tiết lưu ở /tmp/klipr-compare/, bảng tóm tắt in ra cuối cùng.

set -u

OUT_DIR="/tmp/klipr-compare"
DEB="$(realpath "${1:?Usage: $0 klipr_X.Y.Z_all.deb klipr_X.Y.Z_amd64.snap}")"
SNAP="$(realpath "${2:?Usage: $0 klipr_X.Y.Z_all.deb klipr_X.Y.Z_amd64.snap}")"

mkdir -p "$OUT_DIR"
rm -f "$OUT_DIR"/deb.txt "$OUT_DIR"/snap.txt

toggle_once() {
    # $1=APP_ID $2=OBJECT_PATH — in "OK <ms>" hoặc "FAIL", không bao giờ treo
    local app_id="$1" obj="$2" t0 t1
    t0=$(date +%s%N)
    if timeout 3 gdbus call --session --dest "$app_id" --object-path "$obj" \
        --method org.gtk.Actions.Activate toggle-window '[]' '{}' >/dev/null 2>&1; then
        t1=$(date +%s%N)
        echo "OK $(( (t1 - t0) / 1000000 ))"
    else
        echo "FAIL"
    fi
}

wait_for_dbus() {
    local app_id="$1" i=0 t0 t1
    t0=$(date +%s%N)
    while [ "$i" -lt 100 ]; do
        if gdbus call --session --dest org.freedesktop.DBus \
            --object-path /org/freedesktop/DBus \
            --method org.freedesktop.DBus.GetNameOwner "'$app_id'" >/dev/null 2>&1; then
            t1=$(date +%s%N)
            echo "$(( (t1 - t0) / 1000000 ))"
            return 0
        fi
        sleep 0.1
        i=$((i + 1))
    done
    echo "TIMEOUT"
    return 1
}

measure_mem() {
    local pid="$1"
    echo "RSS/PMEM: $(ps -o rss=,pmem= -p "$pid" 2>/dev/null | tr -s ' ')"
    grep -E "^(Pss|Private_Dirty):" "/proc/$pid/smaps_rollup" 2>/dev/null
}

run_common() {
    # $1=label $2=binary_path $3=APP_ID $4=OBJECT_PATH $5=match_pattern(pgrep)
    local label="$1" bin="$2" app_id="$3" obj="$4" match="$5"

    echo "=== $label ==="

    echo "--- khởi động ---"
    rm -f /tmp/klipr-run.log
    "$bin" --hidden > /tmp/klipr-run.log 2>&1 &
    local ready_ms
    ready_ms=$(wait_for_dbus "$app_id")
    echo "thời gian khởi động tới D-Bus sẵn sàng: ${ready_ms} ms"

    local pid
    pid=$(pgrep -f "$match" | head -1)
    if [ -z "$pid" ]; then
        echo "LỖI: process không tồn tại sau khi khởi động"
        cat /tmp/klipr-run.log
        return 1
    fi
    echo "PID=$pid"

    echo "--- lỗi trong log khởi động ---"
    grep -iE "traceback|error|critical|denied" /tmp/klipr-run.log || echo "(không có)"

    echo "--- RAM lúc mới khởi động (chưa mở cửa sổ) ---"
    measure_mem "$pid"

    echo "--- toggle lần 1 (mở cửa sổ — warmup, không tính vào trung bình) ---"
    toggle_once "$app_id" "$obj"
    sleep 1

    echo "--- RAM sau khi mở cửa sổ ---"
    measure_mem "$pid"

    echo "--- 10 lần toggle ổn định ---"
    local total=0 count=0 fails=0
    for i in $(seq 1 10); do
        result=$(toggle_once "$app_id" "$obj")
        echo "  lần $i: $result"
        if [[ "$result" == OK\ * ]]; then
            ms="${result#OK }"
            total=$((total + ms))
            count=$((count + 1))
        else
            fails=$((fails + 1))
        fi
        sleep 0.3
    done
    if [ "$count" -gt 0 ]; then
        echo "trung bình toggle: $(( total / count )) ms (${count}/10 thành công, ${fails} lỗi)"
    else
        echo "TẤT CẢ 10 LẦN TOGGLE ĐỀU LỖI"
    fi

    echo "--- lỗi tích luỹ trong log sau toggle ---"
    grep -iE "traceback|gtk-critical|error|denied" /tmp/klipr-run.log | sort -u || echo "(không có)"

    echo "--- quit sạch (SIGTERM) ---"
    kill -TERM "$pid" 2>/dev/null
    sleep 1
    if ps -p "$pid" > /dev/null 2>&1; then
        echo "❌ vẫn còn sống sau SIGTERM, kill -9"
        kill -KILL "$pid" 2>/dev/null
    else
        echo "✅ đã thoát sạch qua SIGTERM"
    fi
}

# ===== .deb =====
{
    pkill -9 -f "python3.*main.py" 2>/dev/null
    sleep 1
    sudo apt remove -y klipr >/dev/null 2>&1
    echo "--- cài .deb ---"
    if sudo apt install -y "$DEB" 2>&1 | tee /tmp/klipr-apt-install.log | grep -qE "^Setting up klipr"; then
        echo "cài .deb OK: $(dpkg -l klipr | tail -1)"
        run_common ".deb" "/usr/bin/klipr" "io.github.nguyenduc2309.klipr" \
            "/io/github/nguyenduc2309/klipr" "python3.*main.py"
    else
        echo "LỖI CÀI .deb:"; cat /tmp/klipr-apt-install.log
    fi
} | tee "$OUT_DIR/deb.txt"

sudo apt remove -y klipr >/dev/null 2>&1
pkill -9 -f "python3.*main.py" 2>/dev/null
sleep 1

# ===== .snap =====
{
    sudo snap remove --purge klipr >/dev/null 2>&1
    echo "--- cài .snap ---"
    if sudo snap install "$SNAP" --dangerous 2>&1 | tee /tmp/klipr-snap-install.log | grep -q "installed"; then
        echo "cài .snap OK: $(snap list klipr | tail -1)"
        run_common ".snap" "/snap/bin/klipr" "snap.klipr" "/snap/klipr" "python3 main.py"
    else
        echo "LỖI CÀI .snap:"; cat /tmp/klipr-snap-install.log
    fi
} | tee "$OUT_DIR/snap.txt"

echo ""
echo "--- kiểm tra loop device sau khi snap remove (nếu đã gỡ ở trên) ---"
losetup -a 2>/dev/null | grep klipr && echo "❌ còn rác loop device" || echo "✅ sạch"

echo ""
echo "############################################"
echo "# TÓM TẮT (chi tiết trong $OUT_DIR/)"
echo "############################################"
for f in "$OUT_DIR/deb.txt" "$OUT_DIR/snap.txt"; do
    [ -f "$f" ] || continue
    echo "--- $f ---"
    grep -E "thời gian khởi động|trung bình toggle:|RSS/PMEM|Pss:|Private_Dirty:|thoát sạch|vẫn còn sống|LỖI" "$f"
    echo ""
done
