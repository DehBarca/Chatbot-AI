import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory

load_dotenv()
OPENROUTER_KEY= os.getenv("OPENROUTER_API_KEY")


if not OPENROUTER_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env file.")


def get_OpenRouter (model_id, message, history):
    llm = ChatOpenAI(model= model_id , openai_api_key = OPENROUTER_KEY, openai_api_base = "https://openrouter.ai/api/v1")
    reply = llm.invoke(f"Context: el siguiente contenido es el historial de la conversación:{history} puedes usarlo para responder al usuario\nUser: {message}")
    return reply.content