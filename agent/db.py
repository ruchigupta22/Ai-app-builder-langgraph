import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "runs.db"


def init_db():
    """Creates the runs table if it doesn't already exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            plan_json TEXT,
            review_report_json TEXT,
            status TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_run(prompt: str, plan: dict, review_report: list, status: str) -> int:
    """Saves a completed run and returns its new row id."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "INSERT INTO runs (prompt, plan_json, review_report_json, status, created_at) VALUES (?, ?, ?, ?, ?)",
        (prompt, json.dumps(plan), json.dumps(review_report), status, datetime.utcnow().isoformat())
    )
    conn.commit()
    run_id = cursor.lastrowid
    conn.close()
    return run_id


def get_run(run_id: int) -> dict | None:
    """Fetches a single run by id."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "id": row["id"],
        "prompt": row["prompt"],
        "plan": json.loads(row["plan_json"]),
        "review_report": json.loads(row["review_report_json"]),
        "status": row["status"],
        "created_at": row["created_at"],
    }


def list_runs(limit: int = 20) -> list[dict]:
    """Lists recent runs, most recent first."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT id, prompt, status, created_at FROM runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]