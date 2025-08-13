import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_KEY

if not GEMINI_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")


def get_Gemini(model_id, message, history):
    llm = ChatGoogleGenerativeAI(model = model_id, cache = True)
    
    reply = llm.invoke(f"Context: el siguiente contenido es el historial de la conversación:{history} puedes usarlo para responder al usuario\nUser: {message}")
    
    return reply.content


