import json
import re
import os
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QTextEdit, QLineEdit, QPushButton, QApplication
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from tools.worker_thread import WorkerThread
from agent.agent import Agent
from agent.agent_service import AgentService
from agent.orchestrator import AgentOrchestrator

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TA")

        self.service = AgentService()

        main_layout = QHBoxLayout(self)

        left_layout = QVBoxLayout()
        self.new_session_button = QPushButton("新聊天")
        left_layout.addWidget(self.new_session_button)
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

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        right_layout.addWidget(self.chat_display)

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

        self._apply_stylesheet()

    def _apply_stylesheet(self):
        style_path = os.path.join(os.path.dirname(__file__), "../assets/style.qss")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                QApplication.instance().setStyleSheet(f.read())

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

    # --- 下面是你的业务代码，保持不变 ---
    def agent_methods(self):
        from tools.rpc_registry import METHOD_REGISTRY
        return sorted(METHOD_REGISTRY.keys())

    def on_new_session(self):
        file_name = self.service.manager.create_session("你是遵守 JSON-RPC 2.0 协议的智能助手，返回符合规范的 JSON-RPC 请求。")
        self.session_list.addItem(file_name)
        self.service.manager.switch_session(file_name)
        self.load_history()
        items = self.session_list.findItems(file_name, Qt.MatchFlag.MatchExactly)
        if items:
            self.session_list.setCurrentItem(items[0])

    def load_history(self):
        self.chat_display.clear()
        history = self.service.manager.get_history()
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
                    if extra and extra.strip() not in explanation:
                        full_text += f"\n{extra}"

                    self.chat_display.append(full_text + "\n")
                else:
                    self.chat_display.append(f"{display_role}: {content}\n")
            except Exception:
                self.chat_display.append(f"{display_role}: {content}\n")

    def on_session_changed(self, current, previous):
        if current:
            file_name = current.text()
            self.service.manager.switch_session(file_name)
            self.load_history()

    def on_send(self):
        print("ui on_send triggered")
        user_text = self.input_edit.text().strip()
        if not user_text:
            return

        self.send_button.setEnabled(False)
        self.input_edit.setEnabled(False)
        self.cancel_button.setEnabled(True)

        self.thread = WorkerThread(user_text, self.service, stream_mode=True)
        self.thread.finished.connect(self.on_agent_response)
        self.thread.error.connect(self.on_agent_error)
        self.thread.thinking.connect(self.show_thinking_message)
        self.thread.start()


    def on_cancel(self):
        if hasattr(self, "thread") and self.thread.isRunning():
            self.thread.stop()
            self.cancel_button.setEnabled(False)
            self.chat_display.append("🛑 已取消当前任务\n")


    def show_thinking_message(self, msg):
        self.chat_display.append(msg + "\n")

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

    # def on_agent_response(self, first_response):
    #     print("Agent response:", first_response)
    #     try:
    #         final_answer = self.service.orchestrator.run_task(self.service.manager.get_history(), first_response)

    #         self.service.manager.add_message("assistant", final_answer)
    #         self.load_history()

    #     except Exception as e:
    #         self.service.manager.add_message("assistant", f"执行任务出错：{str(e)}")
    #         self.load_history()
    #     finally:
    #         self.send_button.setEnabled(True)
    #         self.input_edit.setEnabled(True)
    #         self.input_edit.clear()

    def on_delete_session(self):
        current_item = self.session_list.currentItem()
        if not current_item:
            return
        file_name = current_item.text()
        self.service.delete_session(file_name)  # 通过服务层删除
        
        row = self.session_list.row(current_item)
        self.session_list.takeItem(row)
        
        # 刷新UI列表和切换会话显示
        sessions = self.service.manager.list_sessions()
        if sessions:
            self.service.manager.switch_session(sessions[0])
            self.load_history()
            items = self.session_list.findItems(sessions[0], Qt.MatchFlag.MatchExactly)
            if items:
                self.session_list.setCurrentItem(items[0])
        else:
            new_session = self.service.manager.create_session("你是遵守 JSON-RPC 2.0 协议的智能助手")
            self.session_list.addItem(new_session)
            self.service.manager.switch_session(new_session)
            self.load_history()

