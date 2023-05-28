from gaylogger.logger import get_logger
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.ext import ContextTypes

from yearbook import db_connection
from yearbook import models
from yearbook import quiz_handler
from yearbook import settings

logger = get_logger(__name__)

states: dict[int, quiz_handler.QuizHandler] = {}

keyboard = [[KeyboardButton(quiz.name)] for quiz in settings.quizzes]
reply_markup = ReplyKeyboardMarkup(keyboard)
cancel = [[KeyboardButton(settings.bot.cancel)]]
cancel_reply_markup = ReplyKeyboardMarkup(cancel)


def get_desc() -> str:
    return "\n".join(f"{quiz.name}: {quiz.desc}" for quiz in settings.quizzes)


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await normal_reply(update, get_desc())


async def normal_reply(update: Update, text: str) -> None:
    await update.message.reply_text(text, reply_markup=reply_markup)


async def in_quiz_reply(update: Update, text: str) -> None:
    await update.message.reply_text(text, reply_markup=cancel_reply_markup)


def add_to_db(user_id: int, qh: quiz_handler.QuizHandler) -> None:
    with db_connection.DBContextManager() as db:
        logger.info("New db data %s", qh.answers)
        db_quiz = models.db.Quiz(
            user=user_id,
            name=qh.quiz.name,
            answers=qh.answers,
        )
        db.add(db_quiz)
        db.commit()


async def handle_cancel(user_id: int, update: Update) -> None:
    states.pop(user_id)
    await normal_reply(
        update,
        settings.bot.return_home,
    )


async def handle_state(user_id: int, text: str, update: Update) -> None:
    states[user_id].new_message(text)
    next_question = states[user_id].next_question()
    if next_question is not None:
        await in_quiz_reply(update, next_question)
    else:
        add_to_db(user_id, states.pop(user_id))
        await normal_reply(update, settings.bot.done)


async def handle_menu(user_id: int, text: str, update: Update) -> None:
    selected_quiz: None | models.quiz.Quiz = None
    for quiz in settings.quizzes:
        if quiz.name == text:
            selected_quiz = quiz
            break
    if selected_quiz is None:
        await normal_reply(update, settings.bot.invalid_button)
        return
    with db_connection.DBContextManager() as db:
        if (
            db.query(models.db.Quiz)
            .filter_by(user=user_id, name=selected_quiz.name)
            .first()
        ):
            await normal_reply(update, settings.bot.duplicate_answer)
            return
    states[user_id] = quiz_handler.QuizHandler(selected_quiz)
    await in_quiz_reply(update, states[user_id].next_question())


async def user_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    user_id = update.message.from_user.id
    logger.info("new  message from %s: %s", user_id, text)
    if user_id in states and text == settings.bot.cancel:
        await handle_cancel(user_id, update)
    elif user_id in states:
        await handle_state(user_id, text, update)
    else:
        await handle_menu(user_id, text, update)
