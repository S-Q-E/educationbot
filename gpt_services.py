import os
import httpx
from dotenv import load_dotenv
from prompts import build_prompt

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "deepseek/deepseek-r1:free"


async def generate_lesson(topic: str) -> str:
    prompt = build_prompt(topic)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "https://example.com",  # обязательно
        "X-Title": "AI Teacher Bot",
        "Content-Type": "application/json"
    }
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Ты — дружелюбный учитель..."},
            {"role": "user", "content": prompt},

        ],

    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post("https://openrouter.ai/api/v1/chat/completions", json=body, headers=headers)
        data = r.json()

        # Проверим наличие ключа choices
        if "choices" not in data or not data["choices"]:
            err = data.get("error", {}).get("message", r.text)
            return f"⚠️ API вернул ошибку: {err}"

        msg = data["choices"][0].get("message")
        if not msg or "content" not in msg:
            return "⚠️ Ответ от AI пришёл без поля content"

        return msg["content"]
