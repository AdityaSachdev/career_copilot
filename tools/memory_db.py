# tools/memory_db.py
"""
Permanent SQLite Memory Store for Career Copilot.
This database ensures that even if you restart your computer or start a new
chat session in ADK Web, your Master Profile and Applied Jobs are never lost.
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

# Place database in the career_copilot root folder
DB_PATH = Path(__file__).parent.parent / "career_memory.db"

def init_memory_db():
    """Initializes SQLite tables for persistent candidate memory."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Candidate Master Profile & Preferences (Key-Value)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidate_memory (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP
        )
    """)
    
    # 2. Applied Jobs Tracker (Prevents applying to the same job twice)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applied_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            job_title TEXT,
            job_url TEXT,
            applied_date TIMESTAMP,
            match_score INTEGER,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

# Auto-initialize database on first import
init_memory_db()


def save_to_long_term_memory(key: str, data: dict | list | str):
    """Saves any Python dictionary or list as JSON into permanent SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    json_val = json.dumps(data)
    cursor.execute(
        "INSERT OR REPLACE INTO candidate_memory (key, value, updated_at) VALUES (?, ?, ?)",
        (key, json_val, datetime.now())
    )
    conn.commit()
    conn.close()


def load_from_long_term_memory(key: str) -> dict | list | str | None:
    """Retrieves JSON data from permanent SQLite and deserializes it."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM candidate_memory WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None


def clear_all_long_term_memory():
    """Clears all stored candidate profiles and applied jobs from SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidate_memory")
    cursor.execute("DELETE FROM applied_jobs")
    conn.commit()
    conn.close()
