"""
database.py — SQLite setup for storing profile audits and AI results
"""
import sqlite3
import os
import json
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'optimizer.db')


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS audits (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            linkedin_url TEXT NOT NULL,
            client_name  TEXT,
            client_type  TEXT DEFAULT 'individual',
            raw_input    TEXT,
            audit_json   TEXT,
            overall_score INTEGER DEFAULT 0,
            ai_provider  TEXT DEFAULT 'groq',
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS profile_sections (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            audit_id  INTEGER NOT NULL,
            section   TEXT NOT NULL,
            score     INTEGER DEFAULT 0,
            status    TEXT DEFAULT 'needs_work',
            issues    TEXT,
            suggestions TEXT,
            example   TEXT,
            FOREIGN KEY (audit_id) REFERENCES audits(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS rewrite_history (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            audit_id  INTEGER NOT NULL,
            section   TEXT NOT NULL,
            original  TEXT,
            rewritten TEXT,
            ai_provider TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (audit_id) REFERENCES audits(id) ON DELETE CASCADE
        );
        """)
    print(f"[DB] Ready at {DB_PATH}")


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def row_to_dict(row):
    return dict(row) if row else None


def rows_to_list(rows):
    return [dict(r) for r in rows]
