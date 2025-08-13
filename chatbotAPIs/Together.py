import os
from dotenv import load_dotenv
from langchain_together import ChatTogether
from langchain.memory import ConversationBufferMemory

load_dotenv()
TOGETHER_KEY= os.getenv("TOGETHER_API_KEY")


if not TOGETHER_KEY:
    raise ValueError("TOGETHER_API_KEY not found in .env file.")

def get_Together(model_id, message, history):
    llm = ChatTogether(model=model_id, api_key=TOGETHER_KEY)
    reply = llm.invoke(f"Context: el siguiente contenido es el historial de la conversación:{history} puedes usarlo para responder al usuario\nUser: {message}")
    return reply.content