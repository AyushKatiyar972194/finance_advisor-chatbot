from langchain.memory import ConversationBufferWindowMemory

def get_memory():
    """
    Remembers last 10 messages in conversation
    """
    return ConversationBufferWindowMemory(
        k=10,
        memory_key="chat_history",
        return_messages=True
    )