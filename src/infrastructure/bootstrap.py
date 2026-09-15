import logging
from typing import Any

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes

from src.adapters.telegram_bootstrap import BootstrapCommand, reply_for
from src.infrastructure.config import load_bot_config


def build_application(token: str, test_chat_id: int) -> Application[Any, Any, Any, Any, Any, Any]:
    application = ApplicationBuilder().token(token).build()

    async def handle(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        message = update.message
        if message is None or message.text is None:
            return
        sender_is_bot = bool(message.from_user and message.from_user.is_bot)
        command = BootstrapCommand(
            chat_id=message.chat_id, text=message.text, sender_is_bot=sender_is_bot
        )
        reply = reply_for(command, test_chat_id)
        if reply is not None:
            await message.reply_text(reply)

    application.add_handler(CommandHandler(["start", "help"], handle))
    return application


def run() -> None:
    config = load_bot_config()
    logging.basicConfig(level=config.log_level)
    application = build_application(config.telegram_bot_token, config.test_chat_id)
    application.run_polling(allowed_updates=["message"])
