import sqlite3
from datetime import datetime, timezone


DATABASE = "triage.db"


def init_db():
    connection = sqlite3.connect(DATABASE)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            channel TEXT NOT NULL,
            client_id TEXT NOT NULL,
            category TEXT,
            draft_reply TEXT,
            confidence TEXT,
            escalate BOOLEAN,
            error TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


def save_ticket(
    text,
    channel,
    client_id,
    category=None,
    draft_reply=None,
    confidence=None,
    escalate=None,
    error=None,
):
    connection = sqlite3.connect(DATABASE)

    connection.execute(
        """
        INSERT INTO tickets (
            text,
            channel,
            client_id,
            category,
            draft_reply,
            confidence,
            escalate,
            error,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            text,
            channel,
            client_id,
            category,
            draft_reply,
            confidence,
            escalate,
            error,
            datetime.now(timezone.utc).isoformat(),
        ),
    )

    connection.commit()
    connection.close()