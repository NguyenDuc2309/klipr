#!/bin/bash
# End-to-end test for a built .deb on a real desktop session: install, launch,
# D-Bus, real clipboard capture, RAM, clean quit, uninstall, user data kept.
# Test đầy đủ cho .deb trên desktop thật (cần sudo cho apt install/remove).
#
# Usage: tests/e2e/test_deb.sh ./klipr_X.Y.Z_all.deb

set -u

DEB="$(realpath "${1:?Usage: $0 path/to/klipr_X.Y.Z_all.deb}")"
VERSION="$(dpkg-deb -f "$DEB" Version)"
APP_ID="io.github.nguyenduc2309.klipr"
OBJECT_PATH="/io/github/nguyenduc2309/klipr"
DB_PATH="$HOME/.local/share/klipr/clipboard.db"
LOG="/tmp/klipr-deb-fulltest.log"

PASS=0
FAIL=0
check() {
    if [ "$1" = "0" ]; then
        echo "✅ $2"
        PASS=$((PASS + 1))
    else
        echo "❌ $2"
        FAIL=$((FAIL + 1))
    fi
}

kill_klipr() {
    local pids
    pids=$(pgrep -f "python3.*main.py")
    [ -n "$pids" ] && kill -9 $pids
    sleep 1
}

wait_for_dbus() {
    local i=0
    while [ "$i" -lt 100 ]; do
        gdbus call --session --dest "$APP_ID" --object-path /org/freedesktop/DBus \
            --method org.freedesktop.DBus.GetNameOwner "'$APP_ID'" >/dev/null 2>&1 && return 0
        gdbus call --session --dest org.freedesktop.DBus --object-path /org/freedesktop/DBus \
            --method org.freedesktop.DBus.GetNameOwner "'$APP_ID'" >/dev/null 2>&1 && return 0
        sleep 0.1
        i=$((i + 1))
    done
    return 1
}

db_count() {
    # $1=db_path $2=content — dùng module sqlite3 chuẩn của Python thay vì
    # CLI `sqlite3` (không có sẵn trong môi trường này).
    python3 -c "
import sqlite3, sys
try:
    conn = sqlite3.connect('$1')
    cur = conn.execute('SELECT COUNT(*) FROM clipboard WHERE content=?', ('$2',))
    print(cur.fetchone()[0])
except Exception as e:
    print(0)
"
}

set_x11_clipboard() {
    # Đặt clipboard qua đúng backend X11 mà klipr dùng (GDK_BACKEND=x11),
    # tránh phụ thuộc xclip/xsel không có sẵn trong môi trường này.
    GDK_BACKEND=x11 python3 - "$1" <<'EOF'
import sys, gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib

text = sys.argv[1]
app = Gtk.Application(application_id="test.setclip.klipr")

def on_activate(app):
    # Without hold(), GApplication treats activate() returning as "idle"
    # and tears the whole app down immediately — the scheduled timeout
    # below never even fires, regardless of its delay. (Confirmed live:
    # klipr's own real capture works fine; this was purely a bug in this
    # test harness, not in klipr.)
    app.hold()
    display = Gdk.Display.get_default()
    clipboard = display.get_clipboard()
    clipboard.set(text)
    def finish():
        app.release()
        app.quit()
        return False
    GLib.timeout_add(1500, finish)

app.connect("activate", on_activate)
app.run(None)
EOF
}

echo "################ TEST: .deb $VERSION ################"

# ── 1. Cài đặt ───────────────────────────────────────────────────
# KHÔNG BAO GIỜ xoá ~/.local/share/klipr, ~/.config/klipr,
# ~/.cache/klipr ở đây — đó là dữ liệu thật của người dùng chạy script
# này trên máy thật, không phải fixture cô lập. (Từng làm điều này và
# xoá mất lịch sử clipboard thật của người dùng — không tái phạm.)
kill_klipr
sudo apt remove -y klipr >/dev/null 2>&1

echo "--- [1] Cài đặt ---"
sudo apt install -y "$DEB" > /tmp/klipr-apt.log 2>&1
grep -qE "^Setting up klipr" /tmp/klipr-apt.log
check $? "apt install thành công"
dpkg -l klipr 2>/dev/null | grep -q "^ii.*$VERSION"
check $? "dpkg báo đúng version $VERSION"
[ -x /usr/bin/klipr ]
check $? "/usr/bin/klipr tồn tại và executable"
[ -f /usr/share/applications/io.github.nguyenduc2309.klipr.desktop ]
check $? "desktop entry đã cài"
[ -f /usr/share/icons/hicolor/128x128/apps/klipr.png ]
check $? "icon đã cài"

# ── 2. Khởi động ─────────────────────────────────────────────────
echo "--- [2] Khởi động ---"
rm -f "$LOG"
klipr --hidden > "$LOG" 2>&1 &
wait_for_dbus
check $? "D-Bus sẵn sàng trong 10s"

PID=$(pgrep -f "python3.*main.py" | head -1)
[ -n "$PID" ]
check $? "process tồn tại (PID=$PID)"

! grep -iqE "traceback|error" "$LOG"
check $? "không có lỗi/traceback trong log khởi động"

[ -f "$HOME/.local/share/klipr/clipboard.db" ]
check $? "database được tạo tại đúng path"

# ── 3. D-Bus toggle-window ────────────────────────────────────────
echo "--- [3] D-Bus toggle ---"
gdbus call --session --dest "$APP_ID" --object-path "$OBJECT_PATH" \
    --method org.gtk.Actions.Activate toggle-window '[]' '{}' >/dev/null 2>&1
check $? "toggle-window action phản hồi"

# ── 4. Clipboard capture thật (không phải giả lập) ─────────────────
echo "--- [4] Clipboard capture ---"
MARKER="klipr-test-$(date +%s)"
set_x11_clipboard "$MARKER" >/dev/null 2>&1
sleep 1  # debounce 100ms trong ClipboardManager + margin

FOUND=$(db_count "$DB_PATH" "$MARKER")
[ "$FOUND" = "1" ]
check $? "text vừa copy xuất hiện trong DB (content='$MARKER')"

# ── 5. RAM ────────────────────────────────────────────────────────
echo "--- [5] RAM ---"
if [ -n "$PID" ] && [ -f "/proc/$PID/smaps_rollup" ]; then
    RSS=$(ps -o rss= -p "$PID" | tr -d ' ')
    PSS=$(grep "^Pss:" "/proc/$PID/smaps_rollup" | awk '{print $2}')
    echo "  RSS=${RSS}KB  PSS=${PSS}KB"
    [ "$RSS" -lt 250000 ]
    check $? "RSS dưới 250MB (thực tế: ${RSS}KB)"
fi

# ── 6. Quit sạch (SIGTERM — mô phỏng tray Quit) ─────────────────────
echo "--- [6] Quit sạch ---"
kill -TERM "$PID"
sleep 1
! ps -p "$PID" > /dev/null 2>&1
check $? "process thoát trong 1s sau SIGTERM"

# ── 7. Dữ liệu còn nguyên sau khi mở lại ────────────────────────────
echo "--- [7] Dữ liệu tồn tại qua lần khởi động lại ---"
rm -f "$LOG"
klipr --hidden > "$LOG" 2>&1 &
wait_for_dbus
PID2=$(pgrep -f "python3.*main.py" | head -1)
FOUND2=$(db_count "$DB_PATH" "$MARKER")
[ "$FOUND2" = "1" ]
check $? "dữ liệu clipboard cũ vẫn còn sau khi restart"
kill -TERM "$PID2" 2>/dev/null
sleep 1

# ── 8. Gỡ cài đặt, dữ liệu user vẫn được giữ (docs/architecture.md) ─────
echo "--- [8] Gỡ cài đặt ---"
sudo apt remove -y klipr > /tmp/klipr-apt-remove.log 2>&1
! dpkg -l klipr 2>/dev/null | grep -q "^ii"
check $? "klipr đã gỡ khỏi dpkg"
[ ! -x /usr/bin/klipr ]
check $? "/usr/bin/klipr đã bị xoá"
[ -f "$DB_PATH" ]
check $? "database KHÔNG bị xoá sau apt remove (đúng thiết kế)"

echo ""
echo "################ KẾT QUẢ: $PASS PASS / $FAIL FAIL ################"
