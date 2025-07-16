# agent/agent.py

from openai import OpenAI
from config import API_KEY
from tools.rpc_registry import METHOD_REGISTRY, METHOD_DOCS


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
你是一个严格遵守 JSON-RPC 2.0 协议的智能助手。

根据用户的中文指令，生成符合 JSON-RPC 2.0 规范的纯 JSON 响应。

你需要输出以下三种类型之一：

1. **调用请求（Request）**

格式如下：

{
  "explanation": "xxx", // 给用户看的说明
  "jsonrpc": {
    "jsonrpc": "2.0",
    "method": "方法名",
    "params": {
      // 方法所需的参数
    },
    "id": 唯一整数ID
  }
}
这里的 id 字段必须是整数且唯一，表示这是一个需要等待响应的请求。
---
2. **通知（Notification）**
格式如下：
{
  "explanation": "xxx", // 给用户看的说明
  "jsonrpc": {
    "jsonrpc": "2.0",
    "method": "方法名",
    "params": {
      // 方法所需参数
    }
    // 这里不带 id 字段，表示这是一个不需要响应的通知。
  }
}
---
3. **响应（Response）**
格式如下：
{
  "explanation": "xxx", // 给用户看的说明
  "jsonrpc": {
    "jsonrpc": "2.0",
    "result": {
      "content": "这里是你要返回给用户的具体内容",
      "done": true
      // 你也可以根据需要添加更多字段，但必须包含 content 和 done。
    },
    "id": 请求中的整数ID，必须与请求中的 id 保持一致
  }
}
---
**严格要求**：

- 只输出纯 JSON，禁止使用 markdown 或多余的自然语言解释。
- JSON 格式必须正确，字段必须完整。
- 根据用户指令自动判断是发送请求、通知还是响应。
- 所有调用请求和响应必须有且仅有一个唯一整数型 id 字段。
- 通知请求不应包含 id 字段。
"""
        self._available_methods = list(METHOD_REGISTRY.keys())
        self.method_docs = METHOD_DOCS  # 参数说明字典
    @property
    def available_methods(self):
        # 动态返回当前所有注册的JSON-RPC方法名列表
        return list(METHOD_REGISTRY.keys())
    @available_methods.setter
    def available_methods(self, methods):
        self._available_methods = methods
    def ask(self, history_messages: list[dict], known_methods=None, extra_prompt=None) -> str:
        print(f"agent ask= history_messages: {history_messages} known_methods: {known_methods} extra_prompt:")
        system_prompt = self.system_prompt
        if known_methods:
            system_prompt += "\n\n请仅使用以下方法名之一调用 JSON-RPC 接口："
            system_prompt += ", ".join(known_methods)

            # 附加参数说明，给模型更清晰指引
            params_info = []
            for method in known_methods:
                if method in self.method_docs:
                    params_desc = self.method_docs[method]
                    params_str = ", ".join(f"{k}: {v}" for k, v in params_desc.items())
                    params_info.append(f"{method}({params_str})")
                else:
                    params_info.append(method)
            if params_info:
                system_prompt += "\n\n方法和参数说明如下：\n" + "\n".join(params_info)

        if extra_prompt:
            system_prompt += "\n\n" + extra_prompt

        messages = [{"role": "system", "content": system_prompt}] + history_messages

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    
    def ask_stream(self, history_messages: list[dict], known_methods=None, extra_prompt=None, check_cancel=lambda: False) -> str:
      system_prompt = self.system_prompt
      if known_methods:
          system_prompt += "\n\n请仅使用以下方法名之一调用 JSON-RPC 接口："
          system_prompt += ", ".join(known_methods)

          # 附加参数说明
          params_info = []
          for method in known_methods:
              if method in self.method_docs:
                  params_desc = self.method_docs[method]
                  params_str = ", ".join(f"{k}: {v}" for k, v in params_desc.items())
                  params_info.append(f"{method}({params_str})")
              else:
                  params_info.append(method)
          if params_info:
              system_prompt += "\n\n方法和参数说明如下：\n" + "\n".join(params_info)

      if extra_prompt:
          system_prompt += "\n\n" + extra_prompt

      messages = [{"role": "system", "content": system_prompt}] + history_messages

      collected_text = ""
      try:
          stream = self.client.chat.completions.create(
              model=self.model,
              messages=messages,
              temperature=0.2,
              stream=True  # 开启流式
          )

          for chunk in stream:
              if check_cancel():
                  print("🛑 中断请求：用户取消")
                  return "🛑 已取消当前任务"

              delta = chunk.choices[0].delta
              if hasattr(delta, "content") and delta.content:
                  collected_text += delta.content

          return collected_text.strip()

      except Exception as e:
          return f"❌ OpenAI 请求失败：{str(e)}"
