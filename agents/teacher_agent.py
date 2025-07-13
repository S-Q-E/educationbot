import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool
from langchain.schema import HumanMessage, AIMessage
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from tools.pdf_generator import generate_pdf
from tools.planner import generate_plan
from tools.quiz import generate_quiz
from tools.web_search import web_search
from database.db import SessionLocal
from database.models import UserMessage

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")


llm = ChatOpenAI(
    model_name="deepseek/deepseek-v3-base:free",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=api_key,
    temperature=0.7
)


def get_chat_history(user_id: int):
    db = SessionLocal()
    history = []
    try:
        messages = db.query(UserMessage).filter(UserMessage.user_id == user_id).order_by(UserMessage.timestamp.asc()).limit(10).all()
        for msg in messages:
            history.append(HumanMessage(content=msg.message))
            if msg.response:
                history.append(AIMessage(content=msg.response))
    finally:
        db.close()
    return history

tools = [
    Tool(
        name="PDF Generator",
        func=generate_pdf,
        description="Генерирует PDF по теме урока"
    ),
    Tool(
        name="Study Planner",
        func=generate_plan,
        description="Создает план обучения по теме"
    ),
    Tool(
        name="Quiz Generator",
        func=generate_quiz,
        description="Генерирует тестовые вопросы по теме"
    ),
    Tool(
        name="Web Search",
        func=web_search,
        description="Ищет информацию в интернете"
    ),
]


async def agent_run(prompt: str, user_id: int = 0) -> str:
    history = get_chat_history(user_id)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    for msg in history:
        memory.chat_memory.add_message(msg)

    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3,
        agent_kwargs={"finish_tool_name": "Final Answer"}
    )

    result = await agent_executor.ainvoke({"input": prompt})
    return result["output"]
