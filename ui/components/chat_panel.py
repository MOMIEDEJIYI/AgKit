import json
import re
import os
import sys
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,QMessageBox,
    QListWidget, QScrollArea, QLineEdit, QPushButton, QApplication, QDialog, QListWidgetItem
)
from PyQt5.QtGui import QFont
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import json
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from agent.worker_thread import WorkerThread
from agent.agent_service import AgentService
from ui.components.base.chat_bubble import ChatBubble
from config_service import ConfigService
from utils import utils

class ChatPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("chat_panel")  # 给根组件加上objectName

        self.service = AgentService()

        main_layout = QHBoxLayout(self)

        left_layout = QVBoxLayout()
        
        self.config = ConfigService()

        self.new_session_button = QPushButton("新聊天")
        self.new_session_button.setObjectName("new_session_button")
        self.new_session_button.clicked.connect(self.on_new_session)

        top_button_row = QHBoxLayout()
        top_button_row.addWidget(self.new_session_button)
        left_layout.addLayout(top_button_row)
        self.new_session_button.clicked.connect(self.on_new_session)

        self.session_list = QListWidget()
        self.session_list.setObjectName("session_list")
        # self.session_list.addItems(self.service.manager.list_sessions())
        font = QFont("Microsoft YaHei", 10)
        for session in self.service.manager.list_sessions():
            item = QListWidgetItem(session)
            item.setFont(font)
            self.session_list.addItem(item)

        self.session_list.setFocusPolicy(Qt.NoFocus)
        self.session_list.setMaximumWidth(245)
        left_layout.addWidget(self.session_list)

        main_layout.addLayout(left_layout)

        right_layout = QVBoxLayout()

        self.delete_button = QPushButton("删除会话")
        right_layout.insertWidget(0, self.delete_button)
        self.delete_button.clicked.connect(self.on_delete_session)

        # 替换 QTextEdit 为 QScrollArea+QWidget布局
        self.chat_area = QScrollArea()
        self.chat_area.setObjectName("chat_area")
        self.chat_area.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_container.setObjectName("chat_container")
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.addStretch()  # 让消息靠上排列，底部有弹簧

        self.chat_area.setWidget(self.chat_container)

        right_layout.addWidget(self.chat_area)

        input_layout = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.input_edit.setObjectName("input_edit")
        self.send_voice = QPushButton("语言输入")
        self.send_voice.setObjectName("send_voice")
        self.send_button = QPushButton("发送")
        self.send_button.setObjectName("send_button")
        self.cancel_button = QPushButton("取消执行")
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setEnabled(False)

        # 语音识别模型路径
        voice_cfg = self.config.get_section("voice")
        model_path = voice_cfg.get("path", "models/vosk-model-small-cn-0.22")
        # 检查模型是否存在
        if not os.path.exists(model_path) or not os.path.exists(os.path.join(model_path, "conf")):
            self.send_voice.setEnabled(False)
            self.send_voice.setToolTip("未检测到语音模型，请下载后放入 models 目录")
        else:
            self.send_voice.setEnabled(True)

        self.send_voice.clicked.connect(self.recognize_voice_input)

        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(self.send_voice)
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
        # current_file = self.service.manager.current_session["file"]
        # for i in range(self.session_list.count()):
        #     item = self.session_list.item(i)
        #     if item.data(Qt.UserRole) == current_file:
        #         self.session_list.setCurrentItem(item)
        #         break

        items = self.session_list.findItems(current_file, Qt.MatchFlag.MatchExactly)
        if items:
            self.session_list.setCurrentItem(items[0])
        # 新增一个思考中显示区
        self.thinking_label = QLabel()
        self.thinking_label.setStyleSheet("color: gray; font-style: italic;")
        right_layout.addWidget(self.thinking_label)

        self.load_stylesheet()

    def load_stylesheet(self):
        qss_path = utils.resource_path("assets/styles/chat_panel.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"样式文件没找到: {qss_path}")

    # 在你的某个方法里，比如发送消息后调用
    def animate_message_bubble(self, messageBubble):
        chatArea = self.chat_area
        end_geom = messageBubble.geometry()
        start_geom = QRect(chatArea.width(), end_geom.y(), 0, end_geom.height())

        anim = QPropertyAnimation(messageBubble, b"geometry", self)
        anim.setDuration(300)
        anim.setStartValue(start_geom)
        anim.setEndValue(end_geom)
        anim.setEasingCurve(QEasingCurve.OutBack)
        anim.start()
        # 这里动画变量不能立刻销毁，否则动画不执行，建议保存引用
        self.current_animation = anim

    def add_chat_bubble(self, text, is_user):
        bubble = ChatBubble(text, is_user)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())
        # 动画效果
        # self.animate_message_bubble(bubble)

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
            # file_name = current.data(Qt.UserRole)
            self.service.manager.switch_session(file_name)
            self.load_history()

    def on_send(self):
        user_text = self.input_edit.text().strip()
        if not user_text:
            return

        self.add_chat_bubble(user_text, is_user=True)  # 显示用户消息气泡

        self.send_button.setEnabled(False)
        self.input_edit.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.thinking_label.setText("正在思考...")
        current_model = self.config.get_current_model()
        self.service.switch_model(current_model)
        self.thread = WorkerThread(user_text, self.service, stream_mode=True)
        self.thread.finished.connect(self.on_agent_response)
        self.thread.error.connect(self.on_agent_error)
        self.thread.thinking.connect(self.show_thinking_message)
        self.thread.start()

        self.input_edit.clear()

    def on_cancel(self):
        if hasattr(self, "thread") and self.thread.isRunning():
            self.thread.stop()
            self.cancel_button.setEnabled(False)
            self.add_chat_bubble("已取消当前任务", is_user=False)

    def show_thinking_message(self, msg):
        self.thinking_label.setText(msg)

    def on_agent_response(self):
        self.send_button.setEnabled(True)
        self.input_edit.setEnabled(True)
        self.input_edit.clear()
        self.cancel_button.setEnabled(False)

        last_msg = self.service.manager.get_history()[-1]["content"]

        # 尝试解析为 JSON-RPC 响应
        try:
            parsed = json.loads(last_msg)
            if isinstance(parsed, dict) and parsed.get("jsonrpc") == "2.0":
                method = parsed.get("method")
                if method == "system.confirm_action":
                    question = parsed["params"]["question"]
                    options = parsed["params"]["options"]
                    rpc_id = parsed.get("id")
                    self.show_confirm_dialog(question, options, rpc_id)
                    return
        except Exception as e:
            pass  # 非 JSON，忽略即可

        self.load_history()  # 普通响应就刷新历史

    def show_confirm_dialog(self, question, options, rpc_id):
        dialog = QDialog(self)
        dialog.setWindowTitle("请确认")

        layout = QVBoxLayout()
        label = QLabel(question)
        layout.addWidget(label)

        button_layout = QHBoxLayout()
        for option in options:
            btn = QPushButton(option)
            btn.clicked.connect(lambda _, opt=option: self.handle_confirmation(dialog, opt, rpc_id))
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()

    def handle_confirmation(self, dialog, option, rpc_id):
        dialog.accept()
        # 构造 JSON-RPC 响应格式
        response = {
            "explanation": f"用户选择了 {option}",
            "jsonrpc": {
                "jsonrpc": "2.0",
                "result": {
                    "content": option,
                    "done": True
                },
                "id": rpc_id
            }
        }

        # 将其添加到对话记录中作为用户消息
        self.service.manager.add_message("user", json.dumps(response, ensure_ascii=False, indent=2))

        # 再次调用 agent 处理这个响应
        self.on_send()

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

    def recognize_voice_input(self):
        self.send_voice.setText("录音中...")
        self.send_voice.setEnabled(False)
        QApplication.processEvents()

        model_path = "models/vosk-model-small-cn-0.22"  # 根据你实际路径调整
        try:
            model = Model(model_path)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"模型加载失败：{e}")
            self.send_voice.setText("语言输入")
            self.send_voice.setEnabled(True)
            return

        q = queue.Queue()

        def callback(indata, frames, time, status):
            if status:
                print(status, flush=True)
            q.put(bytes(indata))

        try:
            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                                channels=1, callback=callback):
                rec = KaldiRecognizer(model, 16000)

                self.thinking_label.setText("识别中，请说话...")

                for i in range(100):  # 最多录约5秒
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        break

                result = json.loads(rec.FinalResult())
                text = result.get("text", "")
                self.input_edit.setText(text if text else "（未识别到语音）")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"录音失败：{e}")
        finally:
            self.send_voice.setText("语言输入")
            self.send_voice.setEnabled(True)
            self.thinking_label.setText("")