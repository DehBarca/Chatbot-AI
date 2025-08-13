import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_KEY

if not GEMINI_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")

def get_Gemini(model_id, message, history):
    llm = ChatGoogleGenerativeAI(model = model_id)
    
    # ultimo_humano = next(
    #     (msg for msg in reversed(history) if type(msg).__name__ == "HumanMessage"),
    #     None
    # )
    # if ultimo_humano and ultimo_humano.content == message:
    #     print(ultimo_humano.content)
    # else:
    #     print("No hay mensajes humanos en la historia.") 
    reply = llm.invoke(f"Context: el siguiente contenido es el historial de la conversación:{history} puedes usarlo para responder al usuario\nUser: {message}")
    
    return reply.content


