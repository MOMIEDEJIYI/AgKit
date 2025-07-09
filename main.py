import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QTextEdit, QLineEdit, QPushButton, QLabel
)
from PyQt5.QtCore import Qt
from conversation.manager import ConversationManager
from rpc_handler import handle_rpc_request
from methods.worker_thread import WorkerThread

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
        for msg in history:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                display_role = "[系统]"
            elif role == "user":
                display_role = "你"
            elif role == "assistant":
                display_role = "助手"
            else:
                display_role = role
            self.chat_display.append(f"{display_role}: {content}\n")

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
        self.manager.add_message("assistant", response)
        self.load_history()

        # 执行 JSON-RPC 请求
        rpc_response = handle_rpc_request(response)

        self.manager.add_message("assistant", f"执行结果:\n{rpc_response}")
        self.load_history()

        # 清空输入框，恢复发送按钮
        self.input_edit.clear()
        self.send_button.setEnabled(True)
        self.input_edit.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.resize(900, 600)
    window.show()
    sys.exit(app.exec())
