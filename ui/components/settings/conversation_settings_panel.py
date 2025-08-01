from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QFormLayout, 
    QFrame, QLabel, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from config_service import ConfigService
from utils import utils
import os

class ConversationSettingsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.config_service = ConfigService()
        self.setup_ui()
        self._load_stylesheet()
        
    def setup_ui(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 卡片容器
        card = QFrame()
        card.setObjectName("settingsCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        
        # 卡片标题
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        title_label = QLabel("会话设置")
        title_label.setObjectName("cardTitle")
        
        header_layout.addWidget(title_label)
        card_layout.addLayout(header_layout)
        
        # 分隔线
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setObjectName("divider")
        card_layout.addWidget(divider)
        
        # 卡片内容
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(15)
        
        # 用户ID
        self.user_id_input = QLineEdit(self.config_service.get_section("conversation").get("user_id", "default"))
        self.user_id_input.setObjectName("styledInput")
        
        # 会话历史目录
        self.history_dir_input = QLineEdit(self.config_service.get_section("conversation").get("history_dir", ""))
        self.history_dir_input.setObjectName("styledInput")
        
        # 添加表单行
        user_id_label = QLabel("用户ID:")
        user_id_label.setObjectName("inputLabel")
        
        history_dir_label = QLabel("历史目录:")
        history_dir_label.setObjectName("inputLabel")
        
        form_layout.addRow(user_id_label, self.user_id_input)
        form_layout.addRow(history_dir_label, self.history_dir_input)
        
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
        main_layout.addWidget(card)
        
        # 添加拉伸因子确保顶部对齐
        main_layout.addStretch(1)
    
    def save_settings(self):
        """保存会话设置"""
        user_id = self.user_id_input.text()
        history_dir = self.history_dir_input.text()

        # 保存会话配置
        self.config_service.set_section("conversation", {"user_id": user_id, "history_dir": history_dir})
        
        # 显示成功消息
        QMessageBox.information(self, "成功", "会话设置已保存!")
    
    def _load_stylesheet(self):
        """加载样式文件"""
        qss_path = utils.resource_path("assets/styles/settings/conversation_settings_panel.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"样式文件未找到: {qss_path}")