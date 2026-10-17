"""SQLite asosidagi xotira: suhbatlar tarixi va uzoq muddatli faktlar."""

import json
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    role TEXT NOT NULL,
    content TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


class Memory:
    def __init__(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.executescript(SCHEMA)

    # --- suhbatlar ---

    def current_conversation(self, owner: str) -> tuple[int, str] | None:
        row = self.db.execute(
            "SELECT id, system_prompt FROM conversations WHERE owner = ? ORDER BY id DESC LIMIT 1",
            (owner,),
        ).fetchone()
        return (row[0], row[1]) if row else None

    def new_conversation(self, owner: str, system_prompt: str) -> int:
        cur = self.db.execute(
            "INSERT INTO conversations (owner, system_prompt) VALUES (?, ?)",
            (owner, system_prompt),
        )
        self.db.commit()
        return cur.lastrowid

    def messages(self, conversation_id: int) -> list[dict]:
        rows = self.db.execute(
            "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id",
            (conversation_id,),
        ).fetchall()
        return [{"role": role, "content": json.loads(content)} for role, content in rows]

    def add_message(self, conversation_id: int, role: str, content) -> None:
        self.db.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, role, json.dumps(content, ensure_ascii=False)),
        )
        self.db.commit()

    # --- faktlar ---

    def add_fact(self, owner: str, text: str) -> int:
        cur = self.db.execute("INSERT INTO facts (owner, text) VALUES (?, ?)", (owner, text))
        self.db.commit()
        return cur.lastrowid

    def facts(self, owner: str) -> list[tuple[int, str]]:
        return self.db.execute(
            "SELECT id, text FROM facts WHERE owner = ? ORDER BY id", (owner,)
        ).fetchall()

    def delete_fact(self, owner: str, fact_id: int) -> bool:
        cur = self.db.execute("DELETE FROM facts WHERE owner = ? AND id = ?", (owner, fact_id))
        self.db.commit()
        return cur.rowcount > 0
