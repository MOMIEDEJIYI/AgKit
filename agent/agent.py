# agent/agent.py

from openai import OpenAI
from agent.rpc_registry import METHOD_REGISTRY, METHOD_META, PACKAGE_FLAGS
import logging
from agent.models.gemini_client import GeminiClient

logger = logging.getLogger(__name__)
class Agent:
    def __init__(self, config: dict):
        self.provider = config.get("provider", "deepseek").lower()
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url")
        self.model = config.get("model", "deepseek-chat")
        print(f"provider: {self.provider}")
        print(f"base_url: {self.base_url}")
        print(f"model: {self.model}")
        if self.provider in ["deepseek", "openai"]:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        elif self.provider == "gemini":
            self.client = GeminiClient(api_key=self.api_key, model=self.model, endpoint=self.base_url)
        else:
            raise ValueError(f"不支持的 PROVIDER: {self.provider}")
        # 过滤启用的包和方法
        self._available_methods = []
        self._method_docs = {}

        for method_name in METHOD_REGISTRY.keys():
            meta = METHOD_META.get(method_name)
            if not meta:
                continue
            package = meta.get("package")
            pkg_enabled = PACKAGE_FLAGS.get(package, {}).get("enabled", True)
            method_enabled = meta.get("enabled", True)
            if pkg_enabled and method_enabled:
                self._available_methods.append(method_name)
                # 从 METHOD_META 里取参数说明和描述，构造文档结构
                self._method_docs[method_name] = {
                    "description": meta.get("description", ""),
                    "params": meta.get("params", {})
                }

        self.system_prompt = """
你是一个严格遵守 JSON-RPC 2.0 协议的智能助手。

根据用户的中文指令，生成符合 JSON-RPC 2.0 规范的纯 JSON 响应。

你只允许返回以下三种类型的结构化 JSON：

---

[1]调用请求（Request）：

{
    "explanation": "给用户的自然语言说明",
    "jsonrpc": {
        "jsonrpc": "2.0",
        "method": "方法名",
        "params": {
            // 方法所需的全部参数
        },
        "id": 整数ID（唯一）
    }
}

说明：
- `id` 字段必须是整数，表示此调用需要获取响应。
- 只能在参数 **完全齐全** 且 **无歧义** 的情况下才生成请求；
- **如果某个方法不需要参数，请将 "params": {}，并直接生成调用请求。无需向用户多问。**

---

[2]通知请求（Notification）：

{
    "explanation": "给用户的自然语言说明",
    "jsonrpc": {
        "jsonrpc": "2.0",
        "method": "方法名",
        "params": {
            // 方法所需参数
        }
        // 注意：此处不包含 id 字段
    }
}

说明：
- 用于用户无需响应的操作（如记录日志、后台处理等）。

---

[3]响应（Response）：

{
    "explanation": "给用户的自然语言说明",
    "jsonrpc": {
        "jsonrpc": "2.0",
        "result": {
            "content": "你要展示给用户的提示、问题或结果文本",
            "done": true
        },
        "id": 请求中的 id，必须与用户请求保持一致
    }
}

说明：
- 用于你要向用户询问问题（如参数缺失、值有歧义等）或返回最终结果。
- `result` 中必须包含 `content` 和 `done` 字段。

---

## 绝对禁止的行为：

1. 不得在参数缺失、模糊或不确定的情况下擅自调用接口；
2. 不得自行推测、自动填补任何参数（如文件扩展名、默认值等）；
3. 不得输出 markdown、纯文本或结构外的内容；
4. 不得省略 `id` 字段（除了通知类型）；
5. 不得在响应格式之外添加解释或额外语言。

---

## 遇到参数缺失时必须这么做：

- 你必须生成一个【响应（Response）】格式的 JSON；
- 在 `explanation` 或 `result.content` 中清晰地写出你想问用户的问题；
- **但如果该方法不需要参数，请不要询问任何内容，直接生成请求。**
- 举例：

```json
{
"explanation": "缺少必要参数 file_extension",
"jsonrpc": {
    "jsonrpc": "2.0",
    "result": {
    "content": "请问你要打开的文件扩展名是什么？例如 .txt 或 .md？",
    "done": true
    },
    "id": 1
}
}
请严格遵守上述规范，始终返回结构正确、字段齐全的纯 JSON。
"""
    @property
    def available_methods(self):
        return self._available_methods

    @property
    def method_docs(self):
        return self._method_docs

    @available_methods.setter
    def available_methods(self, methods):
        self._available_methods = methods
    def refresh_available_methods(self):
        self._available_methods = []
        self._method_docs = {}
        for method_name, meta in METHOD_META.items():
            pkg_enabled = PACKAGE_FLAGS.get(meta["package"], {}).get("enabled", True)
            if pkg_enabled and meta.get("enabled", True) and method_name in METHOD_REGISTRY:
                self._available_methods.append(method_name)
                # 同时更新方法文档
                self._method_docs[method_name] = {
                    "description": meta.get("description", ""),
                    "params": meta.get("params", {})
                }

    def ask(self, history_messages: list[dict], known_methods=None, extra_prompt=None) -> str:
      logger.info(f"agent ask")
      print("请求 URL:", self.base_url)

      # 拼接完整 system prompt
      system_prompt = self._build_system_prompt(known_methods, extra_prompt)

      # 构造 provider 兼容的 messages
      messages = self._build_messages(history_messages, system_prompt)

      if self.provider in ["deepseek", "openai"]:
          response = self.client.chat.completions.create(
              model=self.model,
              messages=messages,
              temperature=0.2,
          )
          return response.choices[0].message.content.strip()

      elif self.provider == "gemini":
          return self.client.chat(messages)

      else:
          raise ValueError(f"未知的 provider: {self.provider}")

    def ask_stream(self, history_messages: list[dict], known_methods=None, extra_prompt=None, check_cancel=lambda: False) -> str:
      print("请求 URL:", self.base_url)
      system_prompt = self._build_system_prompt(known_methods, extra_prompt)
      messages = self._build_messages(history_messages, system_prompt)
      print("messages", messages)
      if self.provider == "gemini":
          try:
              repsonse = self.client.chat(messages)
              print(f"Gemini 成功响应：{repsonse}")
              return repsonse
          except Exception as e:
              return f"Gemini 请求失败：{e}"

      elif self.provider in ["deepseek", "openai"]:
          collected_text = ""
          try:
              stream = self.client.chat.completions.create(
                  model=self.model,
                  messages=messages,
                  temperature=0.2,
                  stream=True
              )
              for chunk in stream:
                  if check_cancel():
                      logger.info("中断请求：用户取消")
                      return "已取消当前任务"

                  delta = chunk.choices[0].delta
                  if hasattr(delta, "content") and delta.content:
                      collected_text += delta.content

              print(f"openai类型 成功响应collected_text：{collected_text}")
              return collected_text.strip()

          except Exception as e:
              return f"请求失败：{str(e)}"

      else:
          return f"不支持的 provider: {self.provider}"


    def _build_messages(self, history_messages: list[dict], system_prompt: str) -> list[dict]:
        """
        根据 provider 构造不同格式的消息。
        """
        if self.provider in ["deepseek", "openai"]:
            return [{"role": "system", "content": system_prompt}] + history_messages

        elif self.provider == "gemini":
          # 过滤掉 system 消息，并深拷贝避免改动原数据
          gemini_messages = [dict(m) for m in history_messages if m.get("role") != "system"]

          if gemini_messages and gemini_messages[0]["role"] == "user":
              # 不修改原消息，复制第一条消息内容，拼接系统提示
              new_first_user = {
                  "role": "user",
                  "content": system_prompt + "\n\n" + gemini_messages[0]["content"]
              }
              gemini_messages[0] = new_first_user
          else:
              gemini_messages.insert(0, {"role": "user", "content": system_prompt})

          return gemini_messages

        else:
            raise ValueError(f"未知的 provider: {self.provider}")
    def _build_system_prompt(self, known_methods=None, extra_prompt=None) -> str:
        prompt = self.system_prompt
        if known_methods:
            prompt += "\n\n请仅使用以下方法名之一调用 JSON-RPC 接口："
            prompt += ", ".join(known_methods)

            params_info = []
            for method in known_methods:
                if method in self._method_docs:
                    params_desc = self._method_docs[method]
                    params_str = ", ".join(f"{k}: {v}" for k, v in params_desc.items())
                    params_info.append(f"{method}({params_str})")
                else:
                    params_info.append(method)
            if params_info:
                prompt += "\n\n方法和参数说明如下：\n" + "\n".join(params_info)

        if extra_prompt:
            prompt += "\n\n" + extra_prompt

        return prompt
