from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QButtonGroup, QSizePolicy
)
from PyQt5.QtCore import Qt, QPropertyAnimation
import os
from utils import utils
from ui.components.base.icon_text_button import IconTextButton


class NavBar(QWidget):
    def __init__(self, parent=None, on_nav_click=None):
        super().__init__(parent)
        self.setObjectName("navbar")
        self.on_nav_click = on_nav_click

        # 展开/折叠宽度
        self.expanded_width = 150
        self.collapsed_width = 40
        self.is_expanded = True  # 默认展开

        self._init_ui()
        self._load_stylesheet()

        self.setMinimumWidth(self.expanded_width)
        self.setMaximumWidth(self.expanded_width)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def _init_ui(self):
        # 主容器布局（垂直）
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(0)

        # 中部按钮区域
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(16)

        # 折叠按钮区域
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)
        top_layout.addStretch()

        self.toggle_btn = QPushButton("←")
        self.toggle_btn.setStyleSheet("text-align: center;")
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_expand)
        top_layout.addWidget(self.toggle_btn)

        center_layout.addLayout(top_layout)

        # 创建按钮组
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        self.btn_group.buttonClicked.connect(self._on_button_clicked)

        # 添加主按钮
        self.chat_btn = IconTextButton("💬", "会话")
        self.req_btn = IconTextButton("⚙️", "请求")
        self.custom_buttons = [self.chat_btn, self.req_btn]

        for btn in self.custom_buttons:
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(40)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.btn_group.addButton(btn)
            center_layout.addWidget(btn)

        # 默认选中第一个按钮
        self.chat_btn.set_selected(True)
        self.chat_btn.setChecked(True)

        # 加入中部区域
        main_layout.addWidget(center_widget)
        main_layout.addStretch()

        # 设置按钮固定底部
        self.settings_btn = IconTextButton("🛠️", "设置")
        self.settings_btn.setCheckable(True)
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.setFixedHeight(40)
        self.settings_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_group.addButton(self.settings_btn)
        main_layout.addWidget(self.settings_btn)

        # 全部按钮收集
        self.custom_buttons.append(self.settings_btn)

        self.setLayout(main_layout)

    def toggle_expand(self):
        """展开/折叠侧边栏"""
        target_width = self.collapsed_width if self.is_expanded else self.expanded_width

        if self.is_expanded:
            for btn in self.custom_buttons:
                btn.set_expanded(False)
        animation = QPropertyAnimation(self, b"minimumWidth")
        animation.setDuration(250)
        animation.setStartValue(self.width())
        animation.setEndValue(target_width)
        animation.finished.connect(self._on_animation_finished)
        animation.start()

        self._anim = animation  # 防止被垃圾回收
        self.is_expanded = not self.is_expanded
        self.toggle_btn.setText("←" if self.is_expanded else "☰")

    def _on_animation_finished(self):
        """动画完成后更新按钮状态"""
        for btn in self.custom_buttons:
            btn.set_expanded(self.is_expanded)

    def _on_button_clicked(self, btn):
        """导航按钮点击"""
        for b in self.custom_buttons:
            b.set_selected(b == btn)

        if self.on_nav_click:
            if btn == self.chat_btn:
                self.on_nav_click("chat")
            elif btn == self.req_btn:
                self.on_nav_click("request")
            elif btn == self.settings_btn:
                self.on_nav_click("settings")

    def _load_stylesheet(self):
        """加载样式文件"""
        qss_path = utils.resource_path("assets/styles/navbar.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"样式文件未找到: {qss_path}")
