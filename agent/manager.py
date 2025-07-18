# conversation/manager.py
import os
import json
from datetime import datetime
import logging
from utils import utils

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, user_id="default"):
        self.history_dir = f"conversation/history/{user_id}"
        os.makedirs(self.history_dir, exist_ok=True)
        self.current_session = None
        logger.info(f"[ConversationManager] 正在加载 {user_id} 的对话记录...")
        self.sessions = self._load_sessions()

    def _load_sessions(self):
        files = os.listdir(self.history_dir)
        return sorted([f for f in files if f.endswith(".json")])

    def create_session(self, system_prompt: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"session_{timestamp}.json"
        self.current_session = {
            "file": file_name,
            "history": [],  # 不写入 system
            "rpc_id": 1,
            "system_prompt": system_prompt  # 单独保存 system_prompt
        }
        self._save()
        return file_name


    def switch_session(self, file_name: str):
        path = os.path.join(self.history_dir, file_name)
        with open(path, "r", encoding="utf-8") as f:
            self.current_session = json.load(f)

    def get_history(self):
        return self.current_session["history"]

    def add_message(self, role, content):
        # if role == "system":
        #     return
        if role == "assistant":
            content = utils.extract_json_from_text(content)
        self.current_session["history"].append({"role": role, "content": content})
        self._save()

    def get_next_id(self):
        rpc_id = self.current_session["rpc_id"]
        self.current_session["rpc_id"] += 1
        self._save()
        return rpc_id

    def list_sessions(self):
        return self._load_sessions()

    def _save(self):
        path = os.path.join(self.history_dir, self.current_session["file"])
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.current_session, f, ensure_ascii=False, indent=2)

    def delete_session(self, file_name):
        path = os.path.join(self.history_dir, file_name)
        if os.path.exists(path):
            os.remove(path)
        if self.current_session and self.current_session.get("file") == file_name:
            self.current_session = None
        self.sessions = self._load_sessions()
