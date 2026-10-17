"""Sozlamalar .env faylidan yoki muhit o'zgaruvchilaridan o'qiladi."""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _ids(raw: str) -> set[int]:
    return {int(part) for part in raw.replace(" ", "").split(",") if part}


@dataclass(frozen=True)
class Config:
    model: str = os.getenv("AGENT_MODEL", "claude-opus-5-5")
    effort: str = os.getenv("AGENT_EFFORT", "medium")
    db_path: str = os.getenv("AGENT_DB_PATH", "data/agent.db")
    timezone: str = os.getenv("AGENT_TIMEZONE", "Asia/Tashkent")
    # Suhbat shu miqdordagi xabardan oshsa, yangi suhbat avtomatik boshlanadi
    # (xotiradagi faktlar saqlanib qoladi).
    max_turns: int = int(os.getenv("AGENT_MAX_TURNS", "40"))
    telegram_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    allowed_user_ids: set[int] = field(
        default_factory=lambda: _ids(os.getenv("TELEGRAM_ALLOWED_USER_IDS", ""))
    )


config = Config()
