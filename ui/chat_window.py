import json
import re
import os
import sys
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QListWidget, QScrollArea, QLineEdit, QPushButton, QApplication, QDialog
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from agent.worker_thread import WorkerThread
from agent.agent_service import AgentService
from ui.components.http_request_config_dialog import HttpRequestConfigDialog
from ui.components.chat_bubble import ChatBubble
from utils import utils

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))

    return os.path.join(base_path, relative_path)

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AG")

        self.service = AgentService()

        main_layout = QHBoxLayout(self)

        left_layout = QVBoxLayout()
        # 添加设置按钮 + 新聊天 按钮（横向排布）
        self.settings_btn = QPushButton("请求设置")
        self.settings_btn.setFixedWidth(80)
        self.settings_btn.clicked.connect(self.open_http_request_config)
        self.http_request_config = {}  # 保存配置（建议改为字典形式）

        self.new_session_button = QPushButton("新聊天")
        self.new_session_button.clicked.connect(self.on_new_session)

        top_button_row = QHBoxLayout()
        top_button_row.addWidget(self.settings_btn)
        top_button_row.addWidget(self.new_session_button)
        left_layout.addLayout(top_button_row)
        self.new_session_button.clicked.connect(self.on_new_session)

        self.session_list = QListWidget()
        self.session_list.addItems(self.service.manager.list_sessions())
        self.session_list.setMaximumWidth(220)
        left_layout.addWidget(self.session_list)

        main_layout.addLayout(left_layout)

        right_layout = QVBoxLayout()

        self.delete_button = QPushButton("删除会话")
        right_layout.insertWidget(0, self.delete_button)
        self.delete_button.clicked.connect(self.on_delete_session)

        # 替换 QTextEdit 为 QScrollArea+QWidget布局
        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.addStretch()  # 让消息靠上排列，底部有弹簧

        self.chat_area.setWidget(self.chat_container)

        right_layout.addWidget(self.chat_area)

        input_layout = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.send_button = QPushButton("发送")
        self.cancel_button = QPushButton("取消执行")
        self.cancel_button.setEnabled(False)

        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.cancel_button)
        right_layout.addLayout(input_layout)
        self.cancel_button.clicked.connect(self.on_cancel)

        main_layout.addLayout(right_layout)

        self.session_list.currentItemChanged.connect(self.on_session_changed)
        self.send_button.clicked.connect(self.on_send)
        self.input_edit.returnPressed.connect(self.on_send)

        self.load_history()

        current_file = self.service.manager.current_session["file"]
        items = self.session_list.findItems(current_file, Qt.MatchFlag.MatchExactly)
        if items:
            self.session_list.setCurrentItem(items[0])

        # 新增一个思考中显示区
        self.thinking_label = QLabel()
        self.thinking_label.setStyleSheet("color: gray; font-style: italic;")
        right_layout.addWidget(self.thinking_label)

        self._apply_stylesheet()

    def _apply_stylesheet(self):
        style_path = resource_path("assets/styles/style.qss")
        print(f"Loading style from: {style_path}")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                QApplication.instance().setStyleSheet(f.read())

    def add_chat_bubble(self, text, is_user):
        bubble = ChatBubble(text, is_user)
        # 插入到倒数第二个位置，保持底部弹簧在最底部
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        # 滚动到底部
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def show_with_animation(self):
        screen = self.screen().availableGeometry()
        final_rect = QRect(
            (screen.width() - 900) // 2,
            (screen.height() - 600) // 2,
            900,
            600,
        )
        start_rect = QRect(
            final_rect.center().x(),
            final_rect.center().y(),
            0,
            0,
        )
        self.setGeometry(start_rect)
        self.setWindowOpacity(0)
        self.show()

        # 几何形状动画（弹跳放大）
        self.anim_geometry = QPropertyAnimation(self, b"geometry")
        self.anim_geometry.setDuration(400)
        self.anim_geometry.setStartValue(start_rect)
        self.anim_geometry.setEndValue(final_rect)
        self.anim_geometry.setEasingCurve(QEasingCurve.OutBack)

        # 透明度动画（淡入）
        self.anim_opacity = QPropertyAnimation(self, b"windowOpacity")
        self.anim_opacity.setDuration(400)
        self.anim_opacity.setStartValue(0)
        self.anim_opacity.setEndValue(1)

        # 同时启动动画
        self.anim_geometry.start()
        self.anim_opacity.start()

    def agent_methods(self):
        from rpc_registry import METHOD_REGISTRY
        return sorted(METHOD_REGISTRY.keys())

    def on_new_session(self):
        file_name = self.service.manager.create_session("你是遵守 JSON-RPC 2.0 协议的智能助手，返回符合规范的 JSON-RPC 请求。")

        existing_items = self.session_list.findItems(file_name, Qt.MatchFlag.MatchExactly)
        if not existing_items:
            self.session_list.addItem(file_name)
        self.service.manager.switch_session(file_name)
        self.load_history()
        # 选中刚创建的项
        items = self.session_list.findItems(file_name, Qt.MatchFlag.MatchExactly)
        if items:
            self.session_list.setCurrentItem(items[0])

    def load_history(self):
        for i in reversed(range(self.chat_layout.count() - 1)):  # 保留底部弹簧
            widget = self.chat_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        history = self.service.manager.get_history()
        for msg in history:
            role = msg["role"]
            if role == "system":
                continue
            content = msg["content"]
            is_user = (role == "user")

            if not is_user:
                # 解析AI内容
                content = utils.process_assistant_content(content)

            self.add_chat_bubble(content, is_user)
    def on_session_changed(self, current, previous):
        if current:
            file_name = current.text()
            self.service.manager.switch_session(file_name)
            self.load_history()

    def on_send(self):
        user_text = self.input_edit.text().strip()
        if not user_text:
            return

        self.add_chat_bubble(user_text, is_user=True)  # 显示用户消息气泡

        # 这里正常发送消息，禁用按钮，启动线程等...
        self.send_button.setEnabled(False)
        self.input_edit.setEnabled(False)
        self.cancel_button.setEnabled(True)

        self.thread = WorkerThread(user_text, self.service, stream_mode=True)
        self.thread.finished.connect(self.on_agent_response)
        self.thread.error.connect(self.on_agent_error)
        self.thread.thinking.connect(self.show_thinking_message)
        self.thread.start()

        self.input_edit.clear()

    def open_http_request_config(self):
        dialog = HttpRequestConfigDialog(self)
        if dialog.exec() == QDialog.Accepted:
            config = dialog.get_config()
            print("用户配置了HTTP请求参数:", config)
            # 这里可以保存到当前会话配置里，或者直接传给Agent
            self.http_request_config = config

    def on_cancel(self):
        if hasattr(self, "thread") and self.thread.isRunning():
            self.thread.stop()
            self.cancel_button.setEnabled(False)
            self.add_chat_bubble("已取消当前任务", is_user=False)

    def show_thinking_message(self, msg):
        self.thinking_label.setText(msg)

    def on_agent_response(self):
        self.load_history()
        self.send_button.setEnabled(True)
        self.input_edit.setEnabled(True)
        self.input_edit.clear()
        self.cancel_button.setEnabled(False)


    def on_agent_error(self, error_msg):
        self.service.manager.add_message("assistant", error_msg)
        self.load_history()
        self.send_button.setEnabled(True)
        self.input_edit.setEnabled(True)
        self.input_edit.clear()
        self.cancel_button.setEnabled(False)

    def on_delete_session(self):
        current_item = self.session_list.currentItem()
        if not current_item:
            return
        file_name = current_item.text()

        # 删除会话文件
        self.service.delete_session(file_name)

        # 清空UI列表
        self.session_list.clear()

        # 重新加载剩余会话列表
        sessions = self.service.manager.list_sessions()
        print("剩余会话列表:", sessions)

        self.session_list.addItems(sessions)

        if sessions:
            first_session = sessions[0]
            print("切换到会话:", first_session)
            self.service.manager.switch_session(first_session)
            self.load_history()

            # 选中第一个会话
            items = self.session_list.findItems(first_session, Qt.MatchFlag.MatchExactly)
            if items:
                self.session_list.setCurrentItem(items[0])
            else:
                print("警告：找不到对应的列表项")
        else:
            print("没有会话了，自动新建一个")
            new_session = self.service.manager.create_session("你是遵守 JSON-RPC 2.0 协议的智能助手")
            self.session_list.addItem(new_session)
            self.service.manager.switch_session(new_session)
            self.load_history()
            items = self.session_list.findItems(new_session, Qt.MatchFlag.MatchExactly)
            if items:
                self.session_list.setCurrentItem(items[0])
            else:
                print("警告：新建的会话列表项没有找到")




