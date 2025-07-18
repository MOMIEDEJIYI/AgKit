# agent/gemini_client.py
import os
import requests

class GeminiClient:
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash", endpoint: str = None):
        self.api_key = api_key
        self.model = model
        if endpoint:
            self.endpoint = endpoint
        else:
            self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def chat(self, messages: list[dict]) -> str:
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.api_key,
        }

        payload = {
            "contents": [
                {
                    "role": m["role"],
                    "parts": [{"text": m["content"]}]
                } for m in messages
            ]
        }

        resp = requests.post(self.endpoint, headers=headers, json=payload)

        if resp.status_code != 200:
            raise Exception(f"请求失败：Error code {resp.status_code}, body: {resp.text}")

        try:
            result = resp.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            raise Exception(f"解析返回 JSON 出错：{e}, body: {resp.text}")
