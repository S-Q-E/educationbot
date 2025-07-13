from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model_name="deepseek/deepseek-v3-base:free",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.5
)

TEMPLATE = """
Ты — преподаватель по теме "{topic}".
Сгенерируй 3 тестовых вопроса с 4 вариантами ответов (A, B, C, D).
Ответ должен быть в формате JSON:
[
  {
    "question": "...",
    "options": ["...", "...", "...", "..."],
    "answer": "B"
  },
  ...
]

Тема: {topic}
"""

prompt = PromptTemplate(input_variables=["topic"], template=TEMPLATE)

def generate_quiz(topic: str) -> list[dict]:
    chain = prompt | llm
    response = chain.invoke({"topic": topic})

    try:
        import json
        data = json.loads(response)
        return data
    except Exception as e:
        return [{"question": "Ошибка генерации викторины", "options": [], "answer": ""}]
