# agent/agent.py

from openai import OpenAI
from config import API_KEY
from tools.rpc_registry import METHOD_REGISTRY


class Agent:
    def __init__(
        self,
        api_key: str = API_KEY,
        base_url: str = "https://api.deepseek.com/v1",
        model: str = "deepseek-chat",
    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.system_prompt = """
你是一个遵守 JSON-RPC 2.0 协议的助手。

根据用户的中文指令，返回一个包含两个字段的 JSON：

{
  "explanation": "请给用户的自然语言回答，描述你做了什么。",
  "jsonrpc": {
    "jsonrpc": "2.0",
    "method": "xxx",
    "params": {
      "file_name": "xxx",
      "content": "内容"
    },
    // 如果调用的方法需要得到结果，请务必携带唯一的整数型 "id" 字段。
    // 如果调用只是通知，不需要等待结果，则可以省略 "id" 字段。
    "id": xxx
  }
}

禁止使用 markdown，禁止自然语言解释，必须严格按照上述格式返回纯 JSON。
"""

    @property
    def available_methods(self):
        # 动态返回当前所有注册的JSON-RPC方法名列表
        return list(METHOD_REGISTRY.keys())
    @available_methods.setter
    def available_methods(self, methods):
        self._available_methods = methods
    def ask(self, history_messages: list[dict], known_methods=None) -> str:
        print("history_messages", history_messages)
        system_prompt = self.system_prompt
        if known_methods:
            system_prompt += (
                "\n\n请仅使用以下方法名之一调用 JSON-RPC 接口："
                + ", ".join(known_methods)
            )

        messages = [{"role": "system", "content": system_prompt}] + history_messages

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()