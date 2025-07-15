import json
import re
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QTextEdit, QLineEdit, QPushButton
)
from PyQt5.QtCore import Qt
from conversation.manager import ConversationManager
from tools.worker_thread import WorkerThread
from agent.agent import Agent
from orchestrator import AgentOrchestrator

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TA")

        self.manager = ConversationManager()
        if not self.manager.list_sessions():
            self.manager.create_session("你是遵守 JSON-RPC 2.0 协议的智能助手，返回符合规范的 JSON-RPC 请求。")
        else:
            self.manager.switch_session(self.manager.list_sessions()[0])

        main_layout = QHBoxLayout(self)

        left_layout = QVBoxLayout()
        self.new_session_button = QPushButton("新聊天")
        left_layout.addWidget(self.new_session_button)
        self.new_session_button.clicked.connect(self.on_new_session)

        self.session_list = QListWidget()
        self.session_list.addItems(self.manager.list_sessions())
        self.session_list.setMaximumWidth(220)
        left_layout.addWidget(self.session_list)

        main_layout.addLayout(left_layout)

        right_layout = QVBoxLayout()

        self.delete_button = QPushButton("删除会话")
        right_layout.insertWidget(0, self.delete_button)
        self.delete_button.clicked.connect(self.on_delete_session)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        right_layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.send_button = QPushButton("发送")
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(self.send_button)
        right_layout.addLayout(input_layout)

        main_layout.addLayout(right_layout)

        self.session_list.currentItemChanged.connect(self.on_session_changed)
        self.send_button.clicked.connect(self.on_send)
        self.input_edit.returnPressed.connect(self.on_send)

        self.load_history()

        current_file = self.manager.current_session["file"]
        items = self.session_list.findItems(current_file, Qt.MatchFlag.MatchExactly)
        if items:
            self.session_list.setCurrentItem(items[0])

        self.agent = Agent()
        self.orchestrator = AgentOrchestrator(self.agent)
        self.agent.available_methods = list(self.agent_methods())

    def agent_methods(self):
        from tools.rpc_registry import METHOD_REGISTRY
        return sorted(METHOD_REGISTRY.keys())

    def on_new_session(self):
        file_name = self.manager.create_session("你是遵守 JSON-RPC 2.0 协议的智能助手，返回符合规范的 JSON-RPC 请求。")
        self.session_list.addItem(file_name)
        self.manager.switch_session(file_name)
        self.load_history()
        items = self.session_list.findItems(file_name, Qt.MatchFlag.MatchExactly)
        if items:
            self.session_list.setCurrentItem(items[0])

    def load_history(self):
        self.chat_display.clear()
        history = self.manager.get_history()
        for msg in history:
            role = msg["role"]
            if role == "system":
                continue
            content = msg["content"]
            display_role = "你" if role == "user" else "助手"

            try:
                m = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
                if m:
                    content_json_str = m.group(1)
                else:
                    content_json_str = content

                parsed = json.loads(content_json_str)

                if isinstance(parsed, dict) and "explanation" in parsed:
                    explanation = parsed["explanation"]
                    extra = ""

                    jsonrpc = parsed.get("jsonrpc")
                    if isinstance(jsonrpc, dict):
                        result = jsonrpc.get("result")
                        if isinstance(result, dict):
                            extra = result.get("message") or result.get("content") or ""

                    if extra:
                        if isinstance(extra, (dict, list)):
                            import json as json_mod
                            extra = json_mod.dumps(extra, ensure_ascii=False, indent=2)
                        max_len = 1000
                        if len(extra) > max_len:
                            extra = extra[:max_len] + "\n...（内容过长，已截断）"

                    full_text = f"{display_role}: {explanation}"
                    if extra:
                        full_text += f"\n{extra}"

                    self.chat_display.append(full_text + "\n")
                else:
                    self.chat_display.append(f"{display_role}: {content}\n")
            except Exception:
                self.chat_display.append(f"{display_role}: {content}\n")

    def on_session_changed(self, current, previous):
        if current:
            file_name = current.text()
            self.manager.switch_session(file_name)
            self.load_history()

    def on_send(self):
        user_text = self.input_edit.text().strip()
        if not user_text:
            return

        self.manager.add_message("user", user_text)
        self.load_history()

        history = self.manager.get_history()

        self.send_button.setEnabled(False)
        self.input_edit.setEnabled(False)

        self.thread = WorkerThread(history)
        self.thread.finished.connect(self.on_agent_response)
        self.thread.start()

    def on_agent_response(self, first_response):
        print("Agent response:", first_response)
        try:
            final_answer = self.orchestrator.run_task(self.manager.get_history(), first_response)

            self.manager.add_message("assistant", final_answer)
            self.load_history()

        except Exception as e:
            self.manager.add_message("assistant", f"执行任务出错：{str(e)}")
            self.load_history()
        finally:
            self.send_button.setEnabled(True)
            self.input_edit.setEnabled(True)
            self.input_edit.clear()

    def on_delete_session(self):
        current_item = self.session_list.currentItem()
        if not current_item:
            return
        file_name = current_item.text()
        self.manager.delete_session(file_name)
        row = self.session_list.row(current_item)
        self.session_list.takeItem(row)
        sessions = self.manager.list_sessions()
        if sessions:
            self.manager.switch_session(sessions[0])
            self.load_history()
            items = self.session_list.findItems(sessions[0], Qt.MatchFlag.MatchExactly)
            if items:
                self.session_list.setCurrentItem(items[0])
        else:
            file_name = self.manager.create_session("你是遵守 JSON-RPC 2.0 协议的智能助手，返回符合规范的 JSON-RPC 请求。")
            self.session_list.addItem(file_name)
            self.manager.switch_session(file_name)
            self.load_history()
