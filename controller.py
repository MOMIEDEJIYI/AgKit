# controller.py
import os

class ChatContext:
    def __init__(self, system_prompt: str):
        self.history = []
        self.add_system_message(system_prompt)

    def add_system_message(self, content):
        if not isinstance(content, str):
            content = str(content)
        self.history.append({"role": "system", "content": content})

    def add_user_message(self, content):
        if not isinstance(content, str):
            content = str(content)
        self.history.append({"role": "user", "content": content})

    def add_assistant_message(self, content):
        if not isinstance(content, str):
            content = str(content)
        self.history.append({"role": "assistant", "content": content})

    def get_history(self):
        return self.history

    def clear(self):
        system_msgs = [msg for msg in self.history if msg["role"] == "system"]
        self.history = system_msgs.copy()
