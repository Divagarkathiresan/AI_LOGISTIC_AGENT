
from collections import defaultdict


class ConversationMemory:

    def __init__(self, max_chat_turns=3):
        self.conversations = defaultdict(list)
        # One chat turn contains a user message and the assistant reply.
        self.max_messages = max_chat_turns * 2

    def add_message(self, session_id, role, content):

        self.conversations[session_id].append({
            "role": role,
            "content": content
        })

        # Retain only the last three user/assistant chat exchanges, rather than the complete session history.
        self.conversations[session_id] = (
            self.conversations[session_id][-self.max_messages:]
        )

    def get_history(self, session_id):

        return self.conversations.get(session_id, [])

    def clear_history(self, session_id):

        if session_id in self.conversations:
            del self.conversations[session_id]


# Shared memory instance.
conversation_memory = ConversationMemory()
