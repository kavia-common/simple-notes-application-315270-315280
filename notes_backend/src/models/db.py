"""SQLite database utilities for the Notes backend.

Uses Python's stdlib `sqlite3` module (no ORM) for a small, easy-to-deploy app.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def _utc_now_iso() -> str:
    """Return current UTC time as an ISO-8601 string with 'Z' suffix."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# PUBLIC_INTERFACE
def get_db_path() -> str:
    """Get the SQLite database path used by this backend.

    The database container creates `myapp.db`. In local/dev, the backend may be run
    from its own working directory, so we default to a `myapp.db` file colocated
    with the backend codebase (repo deployment can mount/provide the same file).

    Override via `SQLITE_DB_PATH` env var when needed.
    """
    env_path = os.getenv("SQLITE_DB_PATH")
    if env_path:
        return env_path

    # Default: keep DB alongside the backend container root to avoid surprises.
    # src/models/db.py -> notes_backend/ (3 parents up: models -> src -> notes_backend)
    backend_root = Path(__file__).resolve().parents[3]
    return str(backend_root / "myapp.db")


def _dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row) -> Dict[str, Any]:
    """sqlite row_factory that produces dicts keyed by column name."""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


# PUBLIC_INTERFACE
def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection with sane defaults for API use."""
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    conn.row_factory = _dict_factory
    # Enforce FK constraints if any are added later
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# PUBLIC_INTERFACE
def init_db() -> None:
    """Ensure the required `notes` table exists.

    The separate database container already creates this table, but we also ensure
    it here so the backend is robust when run standalone.
    """
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


# PUBLIC_INTERFACE
def note_row_to_out(row: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a raw DB row dict into API output shape."""
    return {
        "id": int(row["id"]),
        "title": row["title"],
        "content": row["content"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


# PUBLIC_INTERFACE
def create_note(title: str, content: str) -> Dict[str, Any]:
    """Insert and return a created note row."""
    now = _utc_now_iso()
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO notes (title, content, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (title, content, now, now),
        )
        note_id = cur.lastrowid
        conn.commit()

        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        # row is a dict because of row_factory
        return note_row_to_out(row)


# PUBLIC_INTERFACE
def get_note(note_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single note by id. Returns None if not found."""
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        if row is None:
            return None
        return note_row_to_out(row)


# PUBLIC_INTERFACE
def list_notes() -> list[Dict[str, Any]]:
    """List notes ordered by updated_at desc, then id desc."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM notes
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()
        return [note_row_to_out(r) for r in rows]


# PUBLIC_INTERFACE
def update_note(note_id: int, title: Optional[str], content: Optional[str]) -> Optional[Dict[str, Any]]:
    """Update a note. Returns updated note, or None if not found."""
    existing = get_note(note_id)
    if existing is None:
        return None

    new_title = title if title is not None else existing["title"]
    new_content = content if content is not None else existing["content"]
    now = _utc_now_iso()

    with get_connection() as conn:
        conn.execute(
            """
            UPDATE notes
            SET title = ?, content = ?, updated_at = ?
            WHERE id = ?
            """,
            (new_title, new_content, now, note_id),
        )
        conn.commit()

        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return note_row_to_out(row)


# PUBLIC_INTERFACE
def delete_note(note_id: int) -> bool:
    """Delete a note. Returns True if deleted, False if not found."""
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        return cur.rowcount > 0
