from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QHBoxLayout, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt
import os
from utils import utils
from config_service import ConfigService
from ui.components.base.popup_dialog import PopupDialog


class VoiceSettingsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.config_service = ConfigService()
        self.model_path_input = QLineEdit()

        self.setup_ui()
        self._load_stylesheet()
        self.load_voice_settings()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 卡片容器
        card_container = QFrame()
        card_container.setObjectName("settingsCard")
        card_layout = QVBoxLayout(card_container)
        card_layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)
        title_label = QLabel("语言设置")
        title_label.setObjectName("cardTitle")
        header_layout.addWidget(title_label)
        card_layout.addLayout(header_layout)

        # 分隔线
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setObjectName("divider")
        card_layout.addWidget(divider)

        # 内容
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 15, 20, 20)
        content_layout.setSpacing(15)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(15)

        path_label = QLabel("语音模型路径:")
        path_label.setObjectName("inputLabel")
        self.model_path_input.setObjectName("styledInput")

        form_layout.addRow(path_label, self.model_path_input)
        content_layout.addLayout(form_layout)

        # 保存按钮
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignRight)
        
        self.save_button = QPushButton("保存设置")
        self.save_button.setObjectName("primaryButton")
        self.save_button.setFixedSize(150, 40)
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)

        content_layout.addLayout(button_layout)
        card_layout.addLayout(content_layout)

        main_layout.addWidget(card_container)

    def load_voice_settings(self):
        """加载配置"""
        voice_cfg = self.config_service.get_section("voice") or {}
        self.model_path_input.setText(voice_cfg.get("path", "models/vosk-model-small-cn-0.22"))

    def save_settings(self):
        """保存配置"""
        try:
            new_path = self.model_path_input.text().strip()
            if not new_path:
                QMessageBox.warning(self, "警告", "模型路径不能为空")
                return

            self.config_service.set_section("voice", {"path": new_path})
            self.config_service.save()
            PopupDialog(title="成功", message="语音设置已保存!").exec_()
        except Exception as e:
            QMessageBox.critical(self, "保存失败", str(e))

    def _load_stylesheet(self):
        qss_path = utils.resource_path("assets/styles/settings/voice_settings_panel.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
