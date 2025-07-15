# agent/agent.py

from openai import OpenAI
from config import API_KEY


class Agent:
    def __init__(self, api_key: str = API_KEY, base_url: str = "https://api.deepseek.com/v1", model: str = "deepseek-chat"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.system_prompt = """
你是一个遵守 JSON-RPC 2.0 协议的助手。

根据用户的中文指令，返回一个包含两个字段的 JSON：

{
  "explanation": "请给用户的自然语言回答，描述你做了什么。",
  "jsonrpc": {
    "jsonrpc": "2.0",
    "method": "create_file",
    "params": {
      "file_name": "xxx.txt",
      "content": "内容"
    },
    "id": 1
  }
}

禁止使用 markdown，禁止自然语言解释，必须严格按照上述格式返回纯 JSON。
"""

    def ask(self, history_messages: list[dict]) -> str:
        messages = [{"role": "system", "content": self.system_prompt}] + history_messages

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
