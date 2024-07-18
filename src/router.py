#!/usr/bin/env python

from src.language.utils.logger import BaseLogger
from src.language.utils.secrets import get_secret

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.language.chat import chat_engine

TELEGRAM_TOKEN = get_secret("TELEGRAM_TOKEN")
logger = BaseLogger(__name__)
query = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""

    await update.message.reply_text(
        "Hi! I'm Casper. Please ask me a question and I'll try to answer it.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return query


async def query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives a query and answers a question"""
    user = update.message.from_user
    user_query = update.message.text
    logger.info(f"User {user.first_name}: {user_query}")
    response = str(chat_engine.chat(user_query))
    await update.message.reply_text(
        response,
        reply_markup=ReplyKeyboardRemove(),
    )

    return query


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info(f"User {user.first_name} canceled the conversation.")
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            query: [MessageHandler(filters.TEXT, query_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
