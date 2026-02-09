import sqlite3
import os
import shutil
from contextlib import contextmanager

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
    """Initialize database, migrating from old locations if needed."""
    os.makedirs(DATA_DIR, exist_ok=True)

    # Migrate from old locations if DB doesn't exist yet
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
                is_pinned INTEGER DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ── Dedup migration ────────────────────────────────────────
        # Clean up any existing duplicates (keep the newest per content)
        conn.execute('''
            DELETE FROM clipboard WHERE id NOT IN (
                SELECT MAX(id) FROM clipboard GROUP BY content
            )
        ''')
        # Add UNIQUE index as a DB-level safety net against future dupes
        conn.execute(
            'CREATE UNIQUE INDEX IF NOT EXISTS idx_content_unique ON clipboard(content)'
        )


def add_item(content):
    """Add or update a clipboard item (atomic upsert). Returns the item id."""
    with _get_connection() as conn:
        c = conn.cursor()

        # Atomic upsert — no gap between SELECT and INSERT
        c.execute("""
            INSERT INTO clipboard (content, timestamp)
            VALUES (?, CURRENT_TIMESTAMP)
            ON CONFLICT(content) DO UPDATE SET timestamp = CURRENT_TIMESTAMP
        """, (content,))

        item_id = c.execute(
            "SELECT id FROM clipboard WHERE content = ?", (content,)
        ).fetchone()[0]

        # Prune oldest unpinned items beyond 50-item limit
        count = c.execute("SELECT COUNT(*) FROM clipboard").fetchone()[0]
        if count > 50:
            c.execute("""
                DELETE FROM clipboard
                WHERE id IN (
                    SELECT id FROM clipboard
                    WHERE is_pinned = 0
                    ORDER BY timestamp ASC
                    LIMIT ?
                )
            """, (count - 50,))

    return item_id


def get_items(search_query=None, filter_pinned=None):
    """Get clipboard items with optional search and pin filter."""
    with _get_connection() as conn:
        query = "SELECT id, content, is_pinned, timestamp FROM clipboard"
        params = []
        conditions = []

        if search_query:
            conditions.append("content LIKE ?")
            params.append(f"%{search_query}%")

        if filter_pinned is not None:
            conditions.append("is_pinned = ?")
            params.append(1 if filter_pinned else 0)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY is_pinned DESC, timestamp DESC"
        return conn.execute(query, params).fetchall()


def get_counts():
    """Get total and favorites counts."""
    with _get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM clipboard").fetchone()[0]
        favorites = conn.execute(
            "SELECT COUNT(*) FROM clipboard WHERE is_pinned = 1"
        ).fetchone()[0]
    return total, favorites


def delete_item(item_id):
    """Delete a single clipboard item."""
    with _get_connection() as conn:
        conn.execute("DELETE FROM clipboard WHERE id = ?", (item_id,))


def toggle_pin(item_id):
    """Toggle pin state. Returns the new is_pinned state (bool) or None if not found."""
    with _get_connection() as conn:
        conn.execute(
            "UPDATE clipboard SET is_pinned = NOT is_pinned WHERE id = ?", (item_id,)
        )
        result = conn.execute(
            "SELECT is_pinned FROM clipboard WHERE id = ?", (item_id,)
        ).fetchone()
    return bool(result[0]) if result else None


def clear_unpinned():
    """Delete all unpinned items. Returns count of deleted items."""
    with _get_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM clipboard WHERE is_pinned = 0")
        return c.rowcount


def clear_favorites():
    """Delete all favorited (pinned) items. Returns count of deleted items."""
    with _get_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM clipboard WHERE is_pinned = 1")
        return c.rowcount
