import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QTextEdit, QLineEdit, QPushButton
)
from PyQt5.QtCore import Qt
from conversation.manager import ConversationManager
from rpc_handler import handle_rpc_request
from tools.worker_thread import WorkerThread
from utils import utils
from agent.agent import Agent
from orchestrator import AgentOrchestrator

def load_stylesheet(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

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
                continue  # 跳过 system 消息（比如 rpc 执行结果）
            content = msg["content"]
            display_role = "你" if role == "user" else "助手"

            # ✅ 如果是结构体，尝试只提取 explanation
            try:
                parsed = json.loads(content)
                if isinstance(parsed, dict) and "explanation" in parsed:
                    self.chat_display.append(f"{display_role}: {parsed['explanation']}\n")
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

            # 追加模型最终回答
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


def run_task(agent, history, first_response=None):
    """
    任务主流程：
    - 获取模型响应（first_response 或 agent.ask）
    - 如果是 JSON-RPC 请求 → 执行 → 加入结果 → 继续问
    - 循环直到模型只返回纯文本回答为止
    """

    current_history = history[:]
    response = first_response or agent.ask(current_history)

    while True:
        # 尝试提取 JSON-RPC 请求
        try:
            json_str = utils.extract_json_from_text(response)
            rpc_data = json.loads(json_str)

            # 如果包含 method 字段，说明是 JSON-RPC 请求，需要执行
            if "method" in rpc_data:
                # 执行请求
                rpc_response = handle_rpc_request(json.dumps(rpc_data))

                # 如果报错是“未知方法”，尝试提示方法列表
                if rpc_response.get("error") and "未知方法" in rpc_response["error"]["message"]:
                    response = agent.ask(current_history, known_methods=agent.available_methods)
                    continue  # 重试一次

                # 添加模型请求、系统执行结果到历史
                current_history += [
                    {"role": "assistant", "content": response},
                    {"role": "system", "content": f"RPC调用结果：{json.dumps(rpc_response, ensure_ascii=False)}"}
                ]

                # 获取模型基于执行结果的最终回答
                response = agent.ask(current_history)
                continue  # 再次检查是否还嵌套调用

            else:
                # 没有 method 字段，说明是最终自然语言回答，可以返回
                break

        except Exception:
            # 解析失败或不是 JSON，说明是纯文本结果，直接返回
            break

    # 如果是 JSON 包含 explanation 字段，提取它
    try:
        parsed = json.loads(response)
        return parsed.get("explanation", response)
    except Exception:
        return response  # fallback




def print_registered_methods():
    from tools.rpc_registry import METHOD_REGISTRY
    print("📌 已注册的 JSON-RPC 方法:")
    for name in sorted(METHOD_REGISTRY.keys()):
        func = METHOD_REGISTRY[name]
        print(f" - {name}: {func.__module__}.{func.__name__}")


if __name__ == "__main__":
    print_registered_methods()
    app = QApplication(sys.argv)
    style_path = os.path.join(os.path.dirname(__file__), "assets", "style.qss")
    stylesheet = load_stylesheet(style_path)
    app.setStyleSheet(stylesheet)
    window = ChatWindow()
    window.resize(900, 600)
    window.show()
    sys.exit(app.exec())
