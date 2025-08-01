from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea
)
import os
from utils import utils
from PyQt5.QtCore import Qt
from config_service import ConfigService
from ui.components.settings.model_settings_panel import ModelSettingsPanel
from ui.components.settings.conversation_settings_panel import ConversationSettingsPanel
from ui.components.settings.voice_settings_panel import VoiceSettingsPanel

class SettingsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建主滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 创建一个容器用于放置多个设置面板
        scroll_container = QWidget()
        scroll_container.setObjectName("scrollContainer")
        scroll_layout = QVBoxLayout(scroll_container)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        scroll_layout.setSpacing(20)

        # 添加面板
        self.model_settings = ModelSettingsPanel()
        self.model_settings.setObjectName("modelSettingsCard")
        scroll_layout.addWidget(self.model_settings)

        self.conversation_settings = ConversationSettingsPanel()
        self.conversation_settings.setObjectName("conversationSettingsCard")
        scroll_layout.addWidget(self.conversation_settings)

        self.voice_settings = VoiceSettingsPanel()
        self.voice_settings.setObjectName("voiceSettingsCard")
        scroll_layout.addWidget(self.voice_settings)
        
        scroll_layout.addStretch()  # 增加底部空间

        # 设置容器到滚动区域
        scroll_area.setWidget(scroll_container)

        # 添加到主布局
        main_layout.addWidget(scroll_area)

        self._load_stylesheet()

    def _load_stylesheet(self):
        """加载样式文件"""
        qss_path = utils.resource_path("assets/styles/settings/settings_panel.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"样式文件未找到: {qss_path}")