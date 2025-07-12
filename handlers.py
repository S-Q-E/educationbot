from datetime import datetime

from aiogram import Dispatcher, F
from aiogram.types import Message
from .pf import save_lesson_pdf
from aiogram.types import FSInputFile
from database import Session, LessonHistory
from gpt_services import generate_lesson
import re

def escape_md_v2(text: str) -> str:
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!\\])', r'\\\1', text)


def register_handlers(dp: Dispatcher):
    @dp.message(F.text == "/start")
    async def start_handler(message: Message):
        text = "👋 Привет! Я ИИ-учитель. Напиши мне тему, которую хочешь изучить 📚"
        await message.answer(text=text)

    @dp.message(F.text == "/history")
    async def history_handler(message: Message):
        session = Session()
        rows = session.query(LessonHistory).filter_by(user_id=message.from_user.id).order_by(
            LessonHistory.timestamp.desc()).limit(10).all()
        session.close()

        if not rows:
            await message.answer("📭 У тебя пока нет изученных тем.")
            return

        text = "🕘 *Твои последние темы:*\n\n"
        for row in rows:
            date_str = row.timestamp.strftime("%d.%m.%Y %H:%M")
            text += f"• `{row.topic}` — _{date_str}_\n"

        await message.answer(text)


    @dp.message()
    async def lesson_handler(message: Message):
        topic = message.text.strip()
        await message.answer("🔍 Генерирую учебный план...")
        result = await generate_lesson(topic)

        # Сохраняем в БД
        session = Session()
        history = LessonHistory(
            user_id=message.from_user.id,
            topic=topic,
            content=result,
            timestamp=datetime.utcnow()
        )
        session.add(history)
        session.commit()
        session.close()
        await message.answer(result)

        # pdf_path = save_lesson_pdf(topic, result, message.from_user.id)
        # pdf_file = FSInputFile(pdf_path)
        #
        # await message.answer_document(pdf_file, caption="📝 Вот PDF-файл с уроком!")

    @dp.message(F.text == "/history")
    async def history_handler(message: Message):
        session = Session()
        rows = session.query(LessonHistory).filter_by(user_id=message.from_user.id).order_by(
            LessonHistory.timestamp.desc()).limit(10).all()
        session.close()

        if not rows:
            await message.answer("📭 У тебя пока нет изученных тем.")
            return

        text = "🕘 *Твои последние темы:*\n\n"
        for row in rows:
            date_str = row.timestamp.strftime("%d.%m.%Y %H:%M")
            text += f"• `{row.topic}` — _{date_str}_\n"

        await message.answer(text)
