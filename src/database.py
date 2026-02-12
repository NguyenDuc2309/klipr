import sqlite3
import os
import shutil
from contextlib import contextmanager
import settings

DATA_DIR = os.path.expanduser("~/.local/share/klipr")
DB_PATH = os.path.join(DATA_DIR, "clipboard.db")


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
            c.execute("""
                DELETE FROM clipboard
                WHERE id IN (
                    SELECT id FROM clipboard
                    ORDER BY timestamp ASC
                    LIMIT ?
                )
            """, (count - limit,))


def get_history(search_query=None):
    """Get items from clipboard history."""
    with _get_connection() as conn:
        query = "SELECT id, content, timestamp FROM clipboard"
        params = []
        
        if search_query:
            query += " WHERE content LIKE ?"
            params.append(f"%{search_query}%")
            
        query += " ORDER BY timestamp DESC"
        return conn.execute(query, params).fetchall()


def get_favorites(search_query=None):
    """Get items from favorites. Returns (id, content, timestamp, name)."""
    with _get_connection() as conn:
        query = "SELECT id, content, timestamp, name FROM favorites"
        params = []
        
        if search_query:
            query += " WHERE (content LIKE ? OR (COALESCE(name,'') LIKE ?))"
            params.extend([f"%{search_query}%", f"%{search_query}%"])
            
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
        conn.execute("DELETE FROM clipboard WHERE id = ?", (item_id,))


def delete_favorite_item(item_id):
    """Delete from favorites."""
    with _get_connection() as conn:
        conn.execute("DELETE FROM favorites WHERE id = ?", (item_id,))
        

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
        c.execute("DELETE FROM clipboard")
        return c.rowcount


def clear_favorites():
    """Delete ALL favorite items."""
    with _get_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM favorites")
        return c.rowcount
