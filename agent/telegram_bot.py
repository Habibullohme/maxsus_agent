"""Telegram bot: telefon va noutbukdagi Telegram ilovasi orqali agent bilan gaplashish."""

import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from .brain import Brain
from .config import config
from .memory import Memory

log = logging.getLogger(__name__)
TELEGRAM_LIMIT = 4096


def _allowed(update: Update) -> bool:
    user = update.effective_user
    return user is not None and user.id in config.allowed_user_ids


async def _send_long(update: Update, text: str) -> None:
    for start in range(0, len(text), TELEGRAM_LIMIT):
        await update.message.reply_text(text[start : start + TELEGRAM_LIMIT])


def build_app() -> Application:
    if not config.telegram_token:
        raise SystemExit("TELEGRAM_BOT_TOKEN o'rnatilmagan (.env faylini tekshiring).")
    if not config.allowed_user_ids:
        raise SystemExit("TELEGRAM_ALLOWED_USER_IDS o'rnatilmagan - bot hammaga ochiq bo'lib qoladi.")

    brain = Brain(Memory(config.db_path))

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not _allowed(update):
            return
        await update.message.reply_text(
            "Salom! Men sizning shaxsiy agentingizman.\n"
            "/new - yangi suhbat\n/memory - xotiradagi faktlar"
        )

    async def new(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not _allowed(update):
            return
        brain.reset(str(update.effective_user.id))
        await update.message.reply_text("Yangi suhbat boshlandi. Xotiradagi faktlar saqlanib qoldi.")

    async def memory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not _allowed(update):
            return
        facts = brain.memory.facts(str(update.effective_user.id))
        text = "\n".join(f"[{i}] {t}" for i, t in facts) or "Xotira hozircha bo'sh."
        await _send_long(update, text)

    async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not _allowed(update):
            log.warning("Ruxsatsiz foydalanuvchi: %s", update.effective_user)
            return
        owner = str(update.effective_user.id)
        await update.message.chat.send_action(ChatAction.TYPING)
        try:
            reply = await brain.ask(owner, update.message.text)
        except Exception:
            log.exception("Agent xatosi")
            # Yarim qolgan suhbat keyingi so'rovlarni buzmasligi uchun yangisini boshlaymiz.
            brain.reset(owner)
            reply = "Xatolik yuz berdi, yangi suhbat boshlandi. Qaytadan yozib ko'ring."
        await _send_long(update, reply)

    app = Application.builder().token(config.telegram_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new", new))
    app.add_handler(CommandHandler("memory", memory))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    return app


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    build_app().run_polling()
