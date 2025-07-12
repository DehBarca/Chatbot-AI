import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain_core.globals import set_llm_cache
from langchain_core.caches import InMemoryCache



load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_KEY

set_llm_cache(InMemoryCache())
memory = ConversationBufferMemory(return_messages=True)

def get_Gemini(model_id, message):
    llm = ChatGoogleGenerativeAI(model = model_id, cache = True)
    history = memory.load_memory_variables({}).get("history", "")
    response = llm.invoke(f"{history}\nUser: {message}")
    memory.save_context({"input": message}, {"output": response.content})
    return response.content