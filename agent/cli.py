"""Terminal rejimi: noutbukda to'g'ridan-to'g'ri agent bilan gaplashish."""

import asyncio

from .brain import Brain
from .config import config
from .memory import Memory

OWNER = "cli"


async def _loop() -> None:
    brain = Brain(Memory(config.db_path))
    print("Maxsus agent. Chiqish: /exit, yangi suhbat: /new")
    while True:
        try:
            text = input("\nSiz: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text:
            continue
        if text == "/exit":
            break
        if text == "/new":
            brain.reset(OWNER)
            print("Yangi suhbat boshlandi.")
            continue
        try:
            print("\nAgent:", await brain.ask(OWNER, text))
        except Exception as exc:
            brain.reset(OWNER)
            print(f"\nXatolik: {exc}. Yangi suhbat boshlandi.")


def main() -> None:
    asyncio.run(_loop())
