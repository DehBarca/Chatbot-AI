import os
from dotenv import load_dotenv
from langchain_together import ChatTogether
from langchain.memory import ConversationBufferMemory
from langchain_core.globals import set_llm_cache
from langchain_core.caches import InMemoryCache

load_dotenv()
TOGETHER_KEY= os.getenv("TOGETHER_API_KEY")


if not TOGETHER_KEY:
    raise ValueError("TOGETHER_API_KEY not found in .env file.")

set_llm_cache(InMemoryCache())
memory = ConversationBufferMemory(return_messages=True)

def get_Together(model_id, message):
    llm = ChatTogether(model=model_id, api_key=TOGETHER_KEY, cache=True)
    history = memory.load_memory_variables({}).get("history", "")
    reply = llm.invoke(f"{history}\nUser: {message}")
    memory.save_context({"input": message}, {"output": reply.content})
    return reply.content