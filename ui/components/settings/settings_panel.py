from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, 
    QPushButton, QTabWidget, QFormLayout, QMessageBox, QScrollArea
)
import os
from utils import utils
from PyQt5.QtCore import Qt
from config_service import ConfigService
from ui.components.settings.model_settings_panel import ModelSettingsPanel
from ui.components.settings.conversation_settings_panel import ConversationSettingsPanel

class SettingsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主布局 - 不添加滚动区域
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建Tab控件
        self.tabs = QTabWidget()
        self.tabs.setObjectName("settingsTabs")
        
        # 创建模型设置面板和会话设置面板
        self.model_settings = ModelSettingsPanel()
        self.conversation_settings = ConversationSettingsPanel()
        
        # 为每个面板创建独立的滚动区域
        model_scroll = self.create_scrollable_panel(self.model_settings)
        conversation_scroll = self.create_scrollable_panel(self.conversation_settings)
        
        # 将滚动面板添加到Tab控件
        self.tabs.addTab(model_scroll, "模型设置")
        self.tabs.addTab(conversation_scroll, "会话设置")
        
        # 将标签页添加到主布局
        main_layout.addWidget(self.tabs, 1)  # 添加拉伸因子确保填充
        
        # 加载样式
        self._load_stylesheet()
    
    def create_scrollable_panel(self, panel):
        """为设置面板创建可滚动容器"""
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 设置面板作为滚动区域的内容
        scroll_area.setWidget(panel)
        
        return scroll_area
    
    def _load_stylesheet(self):
        """加载样式文件"""
        qss_path = utils.resource_path("assets/styles/settings/settings_panel.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"样式文件未找到: {qss_path}")