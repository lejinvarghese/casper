#!/usr/bin/env python
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)
from src.utils.logger import BaseLogger
from src.utils.secrets import get_secret
from src.chat import chat_engine
from src.agents.research.team import ResearchTeam

TELEGRAM_TOKEN = get_secret("TELEGRAM_TOKEN")
logger = BaseLogger(__name__)
options, chat, research = range(3)
options_keyboard = [["Chat", "Research"]]
options_markup = ReplyKeyboardMarkup(options_keyboard, one_time_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation"""

    await update.message.reply_text(
        "Hi! I'm Casper. How may I help you?",
        reply_markup=options_markup,
    )
    reset_state(context)

    return options


async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """A chat handler that replies to the user's query"""
    user = update.message.from_user
    user_query = update.message.text
    logger.info(f"User: {user.first_name}: {user_query}")

    if user_query == options_keyboard[0][0]:
        response = """I'm here, what's on your mind?"""
    else:
        response = str(chat_engine.chat(user_query))
    await update.message.reply_text(
        response,
        reply_markup=ReplyKeyboardRemove(),
    )

    return chat


async def research_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """A research handler that does research on the user's topic of interest"""
    user_query = update.message.text
    logger.info(f"User: {user_query}")
    if context.user_data.get("has_research_topic", False):
        await update.message.reply_text(
            f"Now conducting research on the topic: {user_query}.",
            reply_markup=ReplyKeyboardRemove(),
        )
        response = str(ResearchTeam().crew().kickoff(inputs={"topic": user_query}))
        await send_message_in_chunks(update, response)

        context.user_data["has_research_topic"] = False
        await update.message.reply_text(
            "What would you like to do next?",
            reply_markup=options_markup,
        )
        return options
    else:
        response = """What topic would you like to research?"""
        await update.message.reply_text(
            response,
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data["has_research_topic"] = True
        return research


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info(f"User {user.first_name} canceled the conversation.")
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def reset_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Resets the user state for a new session"""
    context.user_data["has_research_topic"] = False


async def send_message_in_chunks(
    update: Update, message: str, chunk_size: int = 4096
) -> None:
    """Send a large message in chunks."""
    for i in range(0, len(message), chunk_size):
        await update.message.reply_text(message[i : i + chunk_size])


def main() -> None:
    """Run the bot."""
    persistence = PicklePersistence(filepath="src/data/.conversations")
    application = (
        Application.builder().token(TELEGRAM_TOKEN).persistence(persistence).build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            options: [
                MessageHandler(
                    filters.Regex(f"^({options_keyboard[0][0]})$"), chat_handler
                ),
                MessageHandler(
                    filters.Regex(f"^({options_keyboard[0][1]})$"), research_handler
                ),
            ],
            chat: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler),
            ],
            research: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, research_handler)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("research", research_handler),
        ],
    )
    application.add_handler(conv_handler)
    logger.info("Casper here, at your service.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
