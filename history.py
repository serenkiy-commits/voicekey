import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "history.db")


def _get_conn(path=None):
    path = path or DB_PATH
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transcriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            duration_sec REAL,
            text TEXT NOT NULL,
            app_name TEXT
        )
    """)
    conn.commit()
    return conn


def save_transcription(text, duration_sec=0.0, app_name=""):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO transcriptions (timestamp, duration_sec, text, app_name) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), duration_sec, text, app_name),
    )
    conn.commit()
    conn.close()


def get_history(limit=100, search=None):
    conn = _get_conn()
    if search:
        rows = conn.execute(
            "SELECT id, timestamp, duration_sec, text, app_name FROM transcriptions WHERE text LIKE ? ORDER BY id DESC LIMIT ?",
            (f"%{search}%", limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, timestamp, duration_sec, text, app_name FROM transcriptions ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    conn.close()
    return rows


def clear_history():
    conn = _get_conn()
    conn.execute("DELETE FROM transcriptions")
    conn.commit()
    conn.close()
