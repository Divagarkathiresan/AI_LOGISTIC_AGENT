
from backend.memory.conversation_memory import ConversationMemory


memory = ConversationMemory(max_messages=10)

session_id = "test_session_001"

# First conversation.
memory.add_message(
    session_id,
    "user",
    "Show all orders placed by Divagar."
)

memory.add_message(
    session_id,
    "assistant",
    "Divagar has orders 101, 102 and 103."
)

# Follow-up question.
memory.add_message(
    session_id,
    "user",
    "What is the status of the first order?"
)

# Display conversation history.
history = memory.get_history(session_id)

for message in history:
    print(message["role"], ":", message["content"])
