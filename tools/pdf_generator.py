from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import os
import re

def clean_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def generate_pdf(topic: str) -> str:
    safe_topic = clean_filename(topic)
    filename = f"Урок — {safe_topic}, {datetime.now().strftime('%d-%m-%Y')}.pdf"
    filepath = os.path.join("pdf", "output", filename)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, f"Урок: {topic}")

    c.setFont("Helvetica", 12)
    text = c.beginText(50, height - 100)
    text.textLines([
        "Это автоматически сгенерированный урок с помощью ИИ.",
        "",
        "💡 Изучите материал, выполните задания и повторите.",
        "",
        f"Дата: {datetime.now().strftime('%d.%m.%Y')}"
    ])
    c.drawText(text)

    c.showPage()
    c.save()

    return filepath

def generate_pdf_plan(topic: str, plan_text: str) -> str:
    # Создание папки, если её нет
    output_dir = "pdf/output"
    os.makedirs(output_dir, exist_ok=True)

    # Название файла
    filename = f"{output_dir}/План — {topic.title()}, {datetime.now().date()}.pdf"

    # Генерация PDF
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    margin = 40

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, height - 50, f"План обучения по теме: {topic.title()}")

    c.setFont("Helvetica", 12)

    lines = plan_text.split('\n')
    y = height - 80
    for line in lines:
        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - 40
        c.drawString(margin, y, line)
        y -= 18

    c.save()
    return filename
