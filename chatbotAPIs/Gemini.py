import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_KEY

def get_Gemini(model_id, message):
    llm = ChatGoogleGenerativeAI(model = model_id)
    response = llm.invoke(message)
    return response.content