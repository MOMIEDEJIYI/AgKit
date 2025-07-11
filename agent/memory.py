# agent/memory.py

import os
import json
from datetime import datetime


class Memory:
    def __init__(self, history_dir: str = "conversation/history"):
        self.history_dir = history_dir
        os.makedirs(self.history_dir, exist_ok=True)
        self.history = []

    def load_latest(self) -> list[dict]:
        """加载最近一条历史对话记录"""
        files = [f for f in os.listdir(self.history_dir) if f.endswith(".json")]
        if not files:
            return []

        latest_file = sorted(files)[-1]
        path = os.path.join(self.history_dir, latest_file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.history = json.load(f)
            return self.history
        except Exception:
            return []

    def save(self, message: dict):
        """将新消息追加到内存中，并写入文件"""
        self.history.append(message)
        filename = datetime.now().strftime("session_%Y%m%d_%H%M%S.json")
        path = os.path.join(self.history_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def get_history(self) -> list[dict]:
        """返回当前历史消息"""
        return self.history.copy()

    def reset(self):
        """清空当前记忆体（内存中）"""
        self.history = []
