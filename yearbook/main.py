from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import filters
from telegram.ext import MessageHandler

from yearbook import bot
from yearbook import settings


def main() -> None:
    application = Application.builder().token(settings.telegram.TOKEN).build()
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(MessageHandler(filters.ALL, bot.user_handler))
    application.run_polling()


if __name__ == "__main__":
    main()
