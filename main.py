import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QTextEdit, QLineEdit, QPushButton, QLabel
)
from PyQt5.QtCore import Qt
from conversation.manager import ConversationManager
from rpc_handler import handle_rpc_request
from tools.worker_thread import WorkerThread
from utils import utils

def load_stylesheet(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TA")

        self.manager = ConversationManager()
        # 如果没有会话，自动创建一个默认会话
        if not self.manager.list_sessions():
            self.manager.create_session("你是遵守 JSON-RPC 2.0 协议的智能助手，返回符合规范的 JSON-RPC 请求。")
        else:
            # 默认切换到第一个会话
            self.manager.switch_session(self.manager.list_sessions()[0])

        main_layout = QHBoxLayout(self)

        # 左侧会话列表
        self.session_list = QListWidget()
        self.session_list.addItems(self.manager.list_sessions())
        self.session_list.setMaximumWidth(220)
        main_layout.addWidget(self.session_list)

        # 右侧对话布局
        right_layout = QVBoxLayout()

        # 在定义完 right_layout 之后，创建并插入删除按钮
        self.delete_button = QPushButton("删除会话")
        right_layout.insertWidget(0, self.delete_button)
        self.delete_button.clicked.connect(self.on_delete_session)

        # 对话显示区
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        right_layout.addWidget(self.chat_display)

        # 输入区域和发送按钮
        input_layout = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.send_button = QPushButton("发送")
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(self.send_button)
        right_layout.addLayout(input_layout)

        main_layout.addLayout(right_layout)

        # 绑定信号
        self.session_list.currentItemChanged.connect(self.on_session_changed)
        self.send_button.clicked.connect(self.on_send)
        self.input_edit.returnPressed.connect(self.on_send)

        # 载入当前会话历史
        self.load_history()

        # 选中当前会话
        current_file = self.manager.current_session["file"]
        items = self.session_list.findItems(current_file, Qt.MatchFlag.MatchExactly)
        if items:
            self.session_list.setCurrentItem(items[0])


    def load_history(self):
        self.chat_display.clear()
        history = self.manager.get_history()
        import json
        for msg in history:
            role = msg["role"]
            if role == "system":
                continue  # 不显示系统提示

            content = msg["content"]
            if role == "user":
                display_role = "你"
                self.chat_display.append(f"{display_role}: {content}\n")
            elif role == "assistant":
                display_role = "助手"
                # 尝试把内容格式化成漂亮的 JSON，如果失败就直接显示原文
                try:
                    parsed = json.loads(content)
                    pretty_json = json.dumps(parsed, ensure_ascii=False, indent=2)
                    self.chat_display.append(f"{display_role} (JSON):\n```json\n{pretty_json}\n```\n")
                except Exception:
                    self.chat_display.append(f"{display_role}: {content}\n")
            else:
                self.chat_display.append(f"{role}: {content}\n")

        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

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

        # 禁用发送按钮，防止重复点击
        self.send_button.setEnabled(False)
        self.input_edit.setEnabled(False)

        self.thread = WorkerThread(history)
        self.thread.finished.connect(self.on_agent_response)
        self.thread.start()

    def on_agent_response(self, response):
        print("Agent response:", response)
        response = utils.extract_json_from_text(response)
        try:
            data = json.loads(response)
            explanation = data.get("explanation", "")
            rpc_command = data.get("jsonrpc", {})

            # 显示自然语言解释给用户
            self.manager.add_message("assistant", explanation)
            self.load_history()

            # 执行 JSON-RPC 请求
            rpc_response = handle_rpc_request(json.dumps(rpc_command))

            # rpc_response本身是dict，提取result显示
            if isinstance(rpc_response, dict):
                result_str = rpc_response.get("result", str(rpc_response))
            else:
                result_str = str(rpc_response)

            self.manager.add_message("assistant", f"执行结果:\n{result_str}")
            self.load_history()

        except Exception as e:
            self.manager.add_message("assistant", f"解析模型回复出错：{str(e)}")
            self.load_history()

        # 清空输入框，恢复发送按钮
        self.input_edit.clear()
        self.send_button.setEnabled(True)
        self.input_edit.setEnabled(True)

    # 实现删除槽函数
    def on_delete_session(self):
        current_item = self.session_list.currentItem()
        if not current_item:
            return
        file_name = current_item.text()

        # 删除会话文件
        self.manager.delete_session(file_name)  # 你需要在 ConversationManager 实现此方法删除文件和管理内存

        # 从列表中移除
        row = self.session_list.row(current_item)
        self.session_list.takeItem(row)

        # 切换到其他会话或新建默认会话
        sessions = self.manager.list_sessions()
        if sessions:
            self.manager.switch_session(sessions[0])
            self.load_history()
            items = self.session_list.findItems(sessions[0], Qt.MatchFlag.MatchExactly)
            if items:
                self.session_list.setCurrentItem(items[0])
        else:
            # 没有会话了就新建一个
            file_name = self.manager.create_session("你是遵守 JSON-RPC 2.0 协议的智能助手，返回符合规范的 JSON-RPC 请求。")
            self.session_list.addItem(file_name)
            self.manager.switch_session(file_name)
            self.load_history()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    style_path = os.path.join(os.path.dirname(__file__), "assets", "style.qss")
    stylesheet = load_stylesheet(style_path)
    app.setStyleSheet(stylesheet)
    window = ChatWindow()
    window.resize(900, 600)
    window.show()
    sys.exit(app.exec())
