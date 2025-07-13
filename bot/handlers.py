import os
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    FSInputFile,
)
from agents.teacher_agent import agent_run
from database.models import UserMessage
from database.db import SessionLocal
from tools.quiz import generate_quiz
from tools.pdf_generator import generate_pdf, generate_pdf_plan
from tools.planner import generate_plan

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Привет! Я твой ИИ-учитель.\n\n"
        "Доступные команды:\n"
        "📘 /pdf <тема> — PDF-урок\n"
        "📋 /план <тема> — план обучения\n"
        "🧠 Викторина <тема> — тест по теме\n"
        "💬 Просто напиши вопрос, и я постараюсь помочь!"
    )

@router.message(Command("pdf"))
async def cmd_pdf(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❗ Укажи тему: /pdf Python")
        return

    topic = args[1]
    try:
        filepath = generate_pdf(topic)
        file = FSInputFile(filepath)
        await message.answer_document(file, caption=f"📘 Урок по теме: <b>{topic}</b>", parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании PDF: {e}")

@router.message(F.text.lower().startswith("викторина"))
async def cmd_quiz(message: Message):
    topic = message.text.replace("викторина", "").strip()
    questions = generate_quiz(topic)

    for i, q in enumerate(questions):
        buttons = [
            [InlineKeyboardButton(text=opt, callback_data=f"quiz:{i}:{opt}:{q['answer']}")]
            for opt in q['options']
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(q['question'], reply_markup=markup)

@router.message(F.text.lower().startswith("/урок"))
async def cmd_lesson(message: Message):
    topic = message.text.replace("/урок", "").strip()
    await message.answer("📝 Генерирую PDF-урок...")
    try:
        pdf_path = generate_pdf(topic)
        file = FSInputFile(pdf_path)
        await message.answer_document(file, caption=f"📚 Урок по теме: <b>{topic}</b>", parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.answer("⚠️ Не удалось создать PDF-файл.")
        print(e)


@router.message(F.text.lower().startswith("/план"))
async def cmd_plan(message: Message):
    topic = message.text.replace("/план", "").strip()
    await message.answer("📋 Формирую PDF-план обучения...")

    try:
        plan = generate_plan(topic)
        filepath = generate_pdf_plan(topic, plan)
        file = FSInputFile(filepath)
        await message.answer_document(file, caption=f"📋 План по теме: <b>{topic}</b>", parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.answer("⚠️ Не удалось создать план.")
        print(e)

@router.message()
async def handle_prompt(message: Message):
    user_input = message.text.strip()
    await message.answer("⏳ Думаю...")

    db = SessionLocal()
    try:
        result = await agent_run(user_input, user_id=message.from_user.id)

        entry = UserMessage(
            user_id=message.from_user.id,
            message=user_input,
            response=result
        )
        db.add(entry)
        db.commit()

        await message.answer(result, parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.answer("⚠️ Ошибка при генерации ответа")
        print(e)
    finally:
        db.close()


@router.callback_query(F.data.startswith("quiz:"))
async def handle_quiz_answer(callback: CallbackQuery):
    try:
        _, q_id, user_choice, correct = callback.data.split(":")
        text = "✅ Верно!" if user_choice == correct else f"❌ Неверно. Правильный ответ: {correct}"
        await callback.message.edit_reply_markup()
        await callback.message.answer(text)
    except Exception as e:
        await callback.message.answer("⚠️ Ошибка при обработке ответа.")
        print(e)


def setup_handlers(dp):
    dp.include_router(router)