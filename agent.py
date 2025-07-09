from openai import OpenAI
from config import API_KEY

client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com/v1")

def ask_agent(history_messages):
    system_prompt = """
你是一个遵守 JSON-RPC 2.0 协议的助手。

根据用户的中文指令，返回如下格式的 JSON：
{
  "jsonrpc": "2.0",
  "method": "create_file",
  "params": {
    "file_name": "xxx.txt",
    "content": "内容"
  },
  "id": 1
}

禁止使用 markdown，禁止自然语言解释，只返回纯 JSON。
"""
    # import json
    messages = [{"role": "system", "content": system_prompt}] + history_messages

    # print("发送给模型的消息（部分）：")
    # print(json.dumps(messages, ensure_ascii=False, indent=2)[:1000])

    res = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.2,
    )
    return res.choices[0].message.content.strip()
