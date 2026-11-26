
from backend.memory.conversation_memory import conversation_memory


def get_conversation_context(session_id):

    history = conversation_memory.get_history(session_id)

    if not history:
        return "No previous conversation."

    context = []

    for message in history:
        role = message["role"].upper()
        content = message["content"]

        context.append(f"{role}: {content}")

    return "\n".join(context)


def save_conversation(session_id, question, answer):

    conversation_memory.add_message(
        session_id,
        "user",
        question
    )

    conversation_memory.add_message(
        session_id,
        "assistant",
        answer
    )
