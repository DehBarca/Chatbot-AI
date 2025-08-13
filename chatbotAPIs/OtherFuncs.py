from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(return_messages=True)

def make_history(input, output):
    history = memory.load_memory_variables({}).get("history", "")
    memory.save_context({"input": input}, {"output": output})
    return history