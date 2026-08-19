import sqlite3
import os
import shutil
import time
from contextlib import contextmanager
import settings

DATA_DIR = os.path.expanduser("~/.local/share/klipr")
DB_PATH = os.path.join(DATA_DIR, "clipboard.db")
IMAGE_CACHE_DIR = os.path.expanduser("~/.cache/klipr/images")
IMAGE_PREFIX = "IMAGE::"


@contextmanager
def _get_connection():
    """Context manager for database connections with auto commit/rollback/close."""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database with separate tables for history and favorites."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DB_PATH):
        src_dir = os.path.dirname(os.path.abspath(__file__))
        for old_path in [
            os.path.join(src_dir, "clipboard.db"),
            os.path.join(src_dir, "..", "clipboard.db"),
        ]:
            if os.path.exists(old_path):
                shutil.copy2(old_path, DB_PATH)
                break

    with _get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS clipboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL UNIQUE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        try:
            cursor = conn.execute("PRAGMA table_info(clipboard)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if "is_pinned" in columns:
                print("Migrating favorites...")
                conn.execute('''
                    INSERT OR IGNORE INTO favorites (content, timestamp)
                    SELECT content, timestamp FROM clipboard WHERE is_pinned = 1
                ''')
        except Exception as e:
            print(f"Migration warning: {e}")

        # Clean up any duplicates before creating unique index
        conn.execute('''
            DELETE FROM clipboard 
            WHERE id NOT IN (
                SELECT MAX(id) FROM clipboard GROUP BY content
            )
        ''')

        conn.execute(
            'CREATE UNIQUE INDEX IF NOT EXISTS idx_clipboard_content ON clipboard(content)'
        )
        conn.execute(
            'CREATE UNIQUE INDEX IF NOT EXISTS idx_favorites_content ON favorites(content)'
        )

        # Migration: add optional name column to favorites if missing
        cursor = conn.execute("PRAGMA table_info(favorites)")
        fav_columns = [info[1] for info in cursor.fetchall()]
        if "name" not in fav_columns:
            conn.execute("ALTER TABLE favorites ADD COLUMN name TEXT")


def _is_cached_image(content):
    """True for IMAGE:: rows whose file lives in our own cache directory."""
    if not content or not content.startswith(IMAGE_PREFIX):
        return False
    path = os.path.realpath(content[len(IMAGE_PREFIX):])
    return os.path.dirname(path) == os.path.realpath(IMAGE_CACHE_DIR)


def _drop_unreferenced_images(conn, contents):
    """Delete cache files for removed rows that nothing else points at.

    Pruned/deleted history rows used to leave their PNG on disk forever, so
    the cache grew without bound even though the history stayed capped. An
    image is only removed once neither history nor favorites reference it.
    """
    for content in contents:
        if not _is_cached_image(content):
            continue
        still_used = conn.execute(
            "SELECT 1 FROM clipboard WHERE content = ? "
            "UNION ALL SELECT 1 FROM favorites WHERE content = ? LIMIT 1",
            (content, content)).fetchone()
        if still_used:
            continue
        try:
            os.remove(content[len(IMAGE_PREFIX):])
        except OSError:
            pass


def prune_orphaned_images():
    """Sweep cache files no row references. Returns how many were removed.

    Run once at startup to reclaim what earlier versions leaked; steady-state
    cleanup is handled inline by _drop_unreferenced_images.
    """
    if not os.path.isdir(IMAGE_CACHE_DIR):
        return 0

    with _get_connection() as conn:
        referenced = {
            row[0][len(IMAGE_PREFIX):]
            for row in conn.execute(
                "SELECT content FROM clipboard WHERE content LIKE 'IMAGE::%' "
                "UNION SELECT content FROM favorites WHERE content LIKE 'IMAGE::%'")
        }

    removed = 0
    cutoff = time.time() - 60  # leave in-flight saves alone
    for name in os.listdir(IMAGE_CACHE_DIR):
        path = os.path.join(IMAGE_CACHE_DIR, name)
        if path in referenced or not os.path.isfile(path):
            continue
        try:
            if os.path.getmtime(path) > cutoff:
                continue
            os.remove(path)
            removed += 1
        except OSError:
            pass
    return removed


def add_item(content):
    """Add item to clipboard history. does NOT affect favorites."""
    with _get_connection() as conn:
        c = conn.cursor()

        c.execute("""
            INSERT INTO clipboard (content, timestamp)
            VALUES (?, CURRENT_TIMESTAMP)
            ON CONFLICT(content) DO UPDATE SET timestamp = CURRENT_TIMESTAMP
        """, (content,))

        limit = settings.get("historyLimit")
        count = c.execute("SELECT COUNT(*) FROM clipboard").fetchone()[0]
        if count > limit:
            evicted = [row[0] for row in c.execute("""
                SELECT content FROM clipboard
                ORDER BY timestamp ASC
                LIMIT ?
            """, (count - limit,)).fetchall()]
            c.execute("""
                DELETE FROM clipboard
                WHERE id IN (
                    SELECT id FROM clipboard
                    ORDER BY timestamp ASC
                    LIMIT ?
                )
            """, (count - limit,))
            _drop_unreferenced_images(conn, evicted)


def get_history(search_query=None):
    """Get items from clipboard history."""
    with _get_connection() as conn:
        query = "SELECT id, content, timestamp FROM clipboard"
        params = []
        
        if search_query and search_query.strip():
            query += " WHERE content LIKE ?"
            params.append(f"%{search_query.strip()}%")
            
        query += " ORDER BY timestamp DESC"
        return conn.execute(query, params).fetchall()


def get_favorites(search_query=None):
    """Get items from favorites. Returns (id, content, timestamp, name)."""
    with _get_connection() as conn:
        query = "SELECT id, content, timestamp, name FROM favorites"
        params = []
        
        if search_query and search_query.strip():
            s = search_query.strip()
            query += " WHERE (content LIKE ? OR (COALESCE(name,'') LIKE ?))"
            params.extend([f"%{s}%", f"%{s}%"])
            
        query += " ORDER BY timestamp DESC"
        return conn.execute(query, params).fetchall()


def get_counts():
    """Get total history and favorites counts."""
    with _get_connection() as conn:
        history = conn.execute("SELECT COUNT(*) FROM clipboard").fetchone()[0]
        favs = conn.execute("SELECT COUNT(*) FROM favorites").fetchone()[0]
    return history, favs


def delete_history_item(item_id):
    """Delete from history."""
    with _get_connection() as conn:
        row = conn.execute("SELECT content FROM clipboard WHERE id = ?", (item_id,)).fetchone()
        conn.execute("DELETE FROM clipboard WHERE id = ?", (item_id,))
        if row:
            _drop_unreferenced_images(conn, [row[0]])


def delete_favorite_item(item_id):
    """Delete from favorites."""
    with _get_connection() as conn:
        row = conn.execute("SELECT content FROM favorites WHERE id = ?", (item_id,)).fetchone()
        conn.execute("DELETE FROM favorites WHERE id = ?", (item_id,))
        if row:
            _drop_unreferenced_images(conn, [row[0]])
        

def add_to_favorites(content):
    """Add content to favorites table."""
    with _get_connection() as conn:
        conn.execute("""
            INSERT INTO favorites (content, timestamp)
            VALUES (?, CURRENT_TIMESTAMP)
            ON CONFLICT(content) DO UPDATE SET timestamp = CURRENT_TIMESTAMP
        """, (content,))


def remove_from_favorites(content):
    """Remove content from favorites table by content string."""
    with _get_connection() as conn:
        conn.execute("DELETE FROM favorites WHERE content = ?", (content,))


def update_favorite_name(item_id, name):
    """Update the optional name/label for a favorite by id. Pass None or '' to clear."""
    with _get_connection() as conn:
        value = (name or "").strip() or None
        conn.execute("UPDATE favorites SET name = ? WHERE id = ?", (value, item_id))


def is_favorite(content):
    """Check if content is in favorites."""
    with _get_connection() as conn:
        res = conn.execute(
            "SELECT 1 FROM favorites WHERE content = ?", (content,)
        ).fetchone()
    return bool(res)


def clear_history():
    """Delete ALL history items."""
    with _get_connection() as conn:
        c = conn.cursor()
        images = [row[0] for row in
                  c.execute("SELECT content FROM clipboard WHERE content LIKE 'IMAGE::%'").fetchall()]
        c.execute("DELETE FROM clipboard")
        removed = c.rowcount
        _drop_unreferenced_images(conn, images)
        return removed


def clear_favorites():
    """Delete ALL favorite items."""
    with _get_connection() as conn:
        c = conn.cursor()
        images = [row[0] for row in
                  c.execute("SELECT content FROM favorites WHERE content LIKE 'IMAGE::%'").fetchall()]
        c.execute("DELETE FROM favorites")
        removed = c.rowcount
        _drop_unreferenced_images(conn, images)
        return removed
