
from collections import defaultdict


class ConversationMemory:

    def __init__(self, max_messages=10):
        self.conversations = defaultdict(list)
        self.max_messages = max_messages

    def add_message(self, session_id, role, content):

        self.conversations[session_id].append({
            "role": role,
            "content": content
        })

        # Keep only the latest messages.
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
