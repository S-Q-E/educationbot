from fpdf import FPDF
from datetime import datetime
import os


class PDFLesson(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, self.title, ln=True, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Страница {self.page_no()}", align="C")


def save_lesson_pdf(topic: str, content: str, user_id: int) -> str:
    pdf = PDFLesson()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_title(f"Урок: {topic}")
    pdf.set_font("Arial", size=12)

    # Тело документа
    lines = content.split("\n")
    for line in lines:
        pdf.multi_cell(0, 10, line.strip())

    # Название файла
    safe_topic = "".join(c for c in topic if c.isalnum() or c in (" ", "-")).strip()
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"Урок — {safe_topic}, {date_str}.pdf"
    filepath = os.path.join("pdfs", str(user_id))
    os.makedirs(filepath, exist_ok=True)

    full_path = os.path.join(filepath, filename)
    pdf.output(full_path)

    return full_path
