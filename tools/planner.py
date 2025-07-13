from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

llm = ChatOpenAI(
    model_name="deepseek/deepseek-v3-base:free",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=api_key,
    temperature=0.6
)

TEMPLATE = """
Ты — опытный преподаватель. Составь подробный учебный план по теме: "{topic}".
План должен включать:
1. Краткое введение
2. Основные понятия
3. Практические задания
4. Советы по изучению
5. Временные рамки (по дням или неделям)
"""

prompt = PromptTemplate(input_variables=["topic"], template=TEMPLATE)

def generate_plan(topic: str) -> str:
    chain = prompt | llm
    return chain.invoke({"topic": topic})