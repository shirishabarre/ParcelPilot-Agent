"""Mock persistence for state-changing actions. SQLite file acts as the
'system of record' stand-in for a real ticketing/escalation system."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "actions_log.db"


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT,
            account_id TEXT,
            order_id TEXT,
            ticket_id TEXT,
            payload TEXT,
            created_at TEXT,
            created_by_role TEXT
        )
    """)
    return conn


def log_action(action_type: str, account_id: str, payload: str, created_by_role: str,
               order_id: str = "", ticket_id: str = "") -> int:
    conn = _conn()
    cur = conn.execute(
        "INSERT INTO actions (action_type, account_id, order_id, ticket_id, payload, created_at, created_by_role) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (action_type, account_id, order_id, ticket_id, payload,
         datetime.now(timezone.utc).isoformat(), created_by_role),
    )
    conn.commit()
    action_id = cur.lastrowid
    conn.close()
    return action_id


def list_actions() -> list[dict]:
    conn = _conn()
    cur = conn.execute("SELECT id, action_type, account_id, order_id, ticket_id, payload, created_at, created_by_role FROM actions ORDER BY id DESC")
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    conn.close()
    return rows
