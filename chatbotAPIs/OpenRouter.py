import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
OPENROUTER_KEY= os.getenv("OPENROUTER_API_KEY")


if not OPENROUTER_KEY:
    raise ValueError("DEEPSEEK_API_KEY not found in .env file.")


def get_OpenRouter (model_id, message):
    llm = ChatOpenAI(model= model_id , openai_api_key = OPENROUTER_KEY, openai_api_base = "https://openrouter.ai/api/v1")
    reply = llm.invoke(message)
    return reply.content