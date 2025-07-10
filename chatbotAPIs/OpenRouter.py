import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.globals import set_llm_cache
from langchain_core.caches import InMemoryCache

load_dotenv()
OPENROUTER_KEY= os.getenv("OPENROUTER_API_KEY")


if not OPENROUTER_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env file.")

memory = ConversationBufferMemory(return_messages=True)

def get_OpenRouter (model_id, message):
    llm = ChatOpenAI(model= model_id , openai_api_key = OPENROUTER_KEY, openai_api_base = "https://openrouter.ai/api/v1", cache = True)
    history = memory.load_memory_variables({}).get("history", "")
    reply = llm.invoke(f"{history}\nUser: {message}")
    memory.save_context({"input": message}, {"output": reply.content})
    return reply.content