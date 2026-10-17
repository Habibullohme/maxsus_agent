"""Ishga tushirish:  python -m agent telegram   yoki   python -m agent cli"""

import sys


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "telegram"
    if mode == "telegram":
        from .telegram_bot import main as run
    elif mode == "cli":
        from .cli import main as run
    else:
        raise SystemExit(f"Noma'lum rejim: {mode}. 'telegram' yoki 'cli' dan foydalaning.")
    run()


if __name__ == "__main__":
    main()
