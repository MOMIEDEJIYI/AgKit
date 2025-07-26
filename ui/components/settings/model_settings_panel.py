from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, 
    QFormLayout, QMessageBox, QCheckBox, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt
import os
from utils import utils
from config_service import ConfigService


class ModelSettingsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.config_service = ConfigService()
        
        # 先初始化所有输入控件
        self.model_name_input = QLineEdit()
        self.provider_input = QLineEdit()
        self.model_input = QLineEdit()
        self.api_key_input = QLineEdit()
        self.base_url_input = QLineEdit()
        
        self.setup_ui()
        self._load_stylesheet()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 卡片容器
        card_container = QFrame()
        card_container.setObjectName("modelCardContainer")
        card_layout = QVBoxLayout(card_container)
        card_layout.setContentsMargins(0, 0, 0, 0)
        
        # 卡片头部 (包含标题和开关)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        title_label = QLabel("模型设置")
        title_label.setObjectName("cardTitle")
        
        # 启用开关
        switch_layout = QHBoxLayout()
        switch_layout.setAlignment(Qt.AlignRight)
        self.enable_label = QLabel("启用模型")
        self.enable_switch = QCheckBox()
        self.enable_switch.setObjectName("toggleSwitch")
        self.enable_switch.setChecked(True)
        self.enable_switch.setFixedSize(50, 24)
        
        switch_layout.addWidget(self.enable_label)
        switch_layout.addWidget(self.enable_switch)
        
        header_layout.addWidget(title_label)
        header_layout.addLayout(switch_layout)
        
        card_layout.addLayout(header_layout)
        
        # 分隔线
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setObjectName("divider")
        card_layout.addWidget(divider)
        
        # 卡片内容区域
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 15, 20, 20)
        content_layout.setSpacing(15)
        
        # 模型选择
        model_select_layout = QHBoxLayout()
        model_label = QLabel("选择模型:")
        model_label.setObjectName("inputLabel")
        
        self.model_combo = QComboBox()
        self.model_combo.setObjectName("styledCombo")
        self.model_combo.addItems(self.config_service.get_all()["agent"].keys())
        self.model_combo.currentTextChanged.connect(self.update_model_info)
        
        model_select_layout.addWidget(model_label, 1)
        model_select_layout.addWidget(self.model_combo, 3)
        
        content_layout.addLayout(model_select_layout)
        
        # 模型卡片展示
        self.model_card = self.create_model_card()
        content_layout.addWidget(self.model_card)
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(15)
        
        # 表单字段 - 现在控件已经初始化
        fields = [
            ("模型名称:", self.model_name_input, "styledInput"),
            ("Provider:", self.provider_input, "styledInput"),
            ("Model:", self.model_input, "styledInput"),
            ("API Key:", self.api_key_input, "styledInput"),
            ("Base URL:", self.base_url_input, "styledInput"),
        ]
        
        self.api_key_input.setEchoMode(QLineEdit.Password)
        
        for label, field, style in fields:
            field_label = QLabel(label)
            field_label.setObjectName("inputLabel")
            field.setObjectName(style)
            form_layout.addRow(field_label, field)
        
        content_layout.addLayout(form_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.save_button = QPushButton("保存设置")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.save_settings)
        
        self.delete_button = QPushButton("删除模型")
        self.delete_button.setObjectName("dangerButton")
        self.delete_button.clicked.connect(self.delete_model)
        
        self.add_button = QPushButton("新建模型")
        self.add_button.setObjectName("secondaryButton")
        self.add_button.clicked.connect(self.add_model)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.add_button)
        
        content_layout.addLayout(button_layout)
        card_layout.addLayout(content_layout)
        main_layout.addWidget(card_container)
        
        self.update_model_info()
    
    def update_model_info(self):
        model_name = self.model_combo.currentText()
        model_config = self.config_service.get_model_config(model_name)

        if model_config:
            # 更新表单字段
            self.model_name_input.setText(model_name)
            self.provider_input.setText(model_config.get('provider', ''))
            self.model_input.setText(model_config.get('model', ''))
            self.api_key_input.setText(model_config.get('api_key', ''))
            self.base_url_input.setText(model_config.get('base_url', ''))
            
            # 更新模型卡片
            self.update_model_card(model_name, model_config)
        else:
            self.model_name_input.clear()
            self.provider_input.clear()
            self.model_input.clear()
            self.api_key_input.clear()
            self.base_url_input.clear()
    
    def create_model_card(self):
        card = QFrame()
        card.setObjectName("modelInfoCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)
        
        self.card_title = QLabel()
        self.card_title.setObjectName("modelCardTitle")
        self.card_title.setAlignment(Qt.AlignCenter)
        
        self.provider_label = QLabel()
        self.model_label = QLabel()
        self.api_key_label = QLabel()
        self.base_url_label = QLabel()
        
        for label in [self.provider_label, self.model_label, 
                      self.api_key_label, self.base_url_label]:
            label.setObjectName("modelCardLabel")
        
        card_layout.addWidget(self.card_title)
        card_layout.addWidget(self.provider_label)
        card_layout.addWidget(self.model_label)
        card_layout.addWidget(self.api_key_label)
        card_layout.addWidget(self.base_url_label)
        
        return card
    
    def update_model_card(self, model_name, model_config):
        self.card_title.setText(f"当前模型: {model_name}")
        self.provider_label.setText(f"Provider: {model_config.get('provider', '未设置')}")
        self.model_label.setText(f"Model: {model_config.get('model', '未设置')}")
        
        # 安全显示API Key
        api_key = model_config.get('api_key', '')
        if api_key:
            self.api_key_label.setText(f"API Key: {api_key[:4]}****{api_key[-4:]}")
        else:
            self.api_key_label.setText("API Key: 未设置")
            
        self.base_url_label.setText(f"Base URL: {model_config.get('base_url', '未设置')}")
    
    def save_settings(self):
        model_name = self.model_combo.currentText()
        new_model_name = self.model_name_input.text()

        if model_name != new_model_name:
            self.config_service.delete_model_config(model_name)
            
        model_config = {
            'provider': self.provider_input.text(),
            'model': self.model_input.text(),
            'api_key': self.api_key_input.text(),
            'base_url': self.base_url_input.text(),
        }
        
        self.config_service.set_model_config(new_model_name, model_config)
        self.config_service.save()
        
        # 更新模型列表
        self.model_combo.clear()
        self.model_combo.addItems(self.config_service.get_all()["agent"].keys())
        if new_model_name in self.config_service.get_all()["agent"]:
            self.model_combo.setCurrentText(new_model_name)
        
        QMessageBox.information(self, "成功", "模型设置已保存!")
    
    def delete_model(self):
        model_name = self.model_combo.currentText()
        if model_name == 'default':
            QMessageBox.warning(self, "警告", "默认模型不能删除!")
            return

        reply = QMessageBox.question(self, '确认删除', f"您确定要删除模型: {model_name} 吗?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.config_service.delete_model_config(model_name)
            self.config_service.save()
            
            # 更新模型列表
            self.model_combo.clear()
            self.model_combo.addItems(self.config_service.get_all()["agent"].keys())
            
            # 更新表单
            self.update_model_info()
            
            QMessageBox.information(self, "成功", f"模型 {model_name} 已被删除!")

    def add_model(self):
        # 生成唯一的新模型名称
        existing_models = self.config_service.get_all()["agent"].keys()
        new_model_name = "new_model"
        counter = 1
        while f"{new_model_name}_{counter}" in existing_models:
            counter += 1
        new_model_name = f"{new_model_name}_{counter}"
        
        new_model_config = {
            "provider": "deepseek",
            "api_key": "",
            "model": "new_model",
            "base_url": "https://api.deepseek.com/v1"
        }

        self.config_service.set_model_config(new_model_name, new_model_config)
        self.config_service.save()
        
        # 更新模型列表
        self.model_combo.addItem(new_model_name)
        self.model_combo.setCurrentText(new_model_name)
        
        QMessageBox.information(self, "成功", f"已新增模型: {new_model_name}")
    
    def _load_stylesheet(self):
        """加载样式文件"""
        qss_path = utils.resource_path("assets/styles/settings/model_settings_panel.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"样式文件未找到: {qss_path}")