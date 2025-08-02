from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QButtonGroup, QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt, QPropertyAnimation
import os
from utils import utils
from ui.components.base.icon_text_button import IconTextButton


class NavBar(QWidget):
    def __init__(self, parent=None, on_nav_click=None):
        super().__init__(parent)
        self.on_nav_click = on_nav_click

        self.expanded_width = 150
        self.collapsed_width = 52
        self.is_expanded = True

        self.buttons = {}  # key -> 按钮
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        self.btn_group.buttonClicked.connect(self._on_button_clicked)

        self._init_ui()
        self._load_stylesheet()

        # 启动时展开
        self.setMinimumWidth(self.expanded_width)
        self.setMaximumWidth(self.expanded_width)
        self.setFixedWidth(self.expanded_width)
        self.is_expanded = True
        self.toggle_btn.setText("←")
        self.setAttribute(Qt.WA_TranslucentBackground)

    def _init_ui(self):
        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        nav_widget = QWidget()
        nav_widget.setObjectName("navbar")
        main_layout = QVBoxLayout(nav_widget)
        main_layout.setContentsMargins(0, 0, 10, 0)
        main_layout.setSpacing(0)

        center_widget = QWidget()
        self.center_layout = QVBoxLayout(center_widget)
        self.center_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.setSpacing(5)

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

        self.center_layout.addLayout(top_layout)

        main_layout.addWidget(center_widget)
        main_layout.addStretch()

        # 底部设置按钮区域，单独放置也可动态添加，这里暂时放一起
        self.bottom_widget = QWidget()
        self.bottom_layout = QVBoxLayout(self.bottom_widget)
        self.bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_layout.setSpacing(5)

        main_layout.addWidget(self.bottom_widget)

        outer_layout.addWidget(nav_widget)

        vline = QFrame()
        vline.setFrameShape(QFrame.VLine)
        vline.setFrameShadow(QFrame.Sunken)
        vline.setObjectName("navbarDivider")
        outer_layout.addWidget(vline)

        self.setLayout(outer_layout)

    def add_button(self, key, icon, text, bottom=False):
        """
        动态添加导航按钮

        :param key: 唯一标识，用于点击回调识别
        :param icon: 图标文本或emoji
        :param text: 按钮显示文本
        :param bottom: 是否放到底部（比如设置按钮）
        """
        btn = IconTextButton(icon, text)
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(40)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.key = key  # 给按钮绑定key属性，方便点击事件识别
        self.btn_group.addButton(btn)

        if bottom:
            self.bottom_layout.addWidget(btn)
        else:
            self.center_layout.addWidget(btn)

        self.buttons[key] = btn

        # 默认第一个添加的按钮选中
        if len(self.buttons) == 1:
            btn.set_selected(True)
            btn.setChecked(True)

        return btn

    def _on_button_clicked(self, btn):
        # 先取消其他按钮选中状态，设置当前按钮选中
        for b in self.buttons.values():
            b.set_selected(b == btn)

        if self.on_nav_click and hasattr(btn, "key"):
            self.on_nav_click(btn.key)

    def toggle_expand(self):
        target_width = self.collapsed_width if self.is_expanded else self.expanded_width
        print(f"切换导航栏宽度: {target_width}")

        if self.is_expanded:
            for btn in self.buttons.values():
                btn.set_expanded(False)

        # 动画最小宽度
        anim_min = QPropertyAnimation(self, b"minimumWidth")
        anim_min.setDuration(250)
        anim_min.setStartValue(self.width())
        anim_min.setEndValue(target_width)

        # 动画最大宽度
        anim_max = QPropertyAnimation(self, b"maximumWidth")
        anim_max.setDuration(250)
        anim_max.setStartValue(self.width())
        anim_max.setEndValue(target_width)

        # 结束时处理
        anim_max.finished.connect(self._on_animation_finished)

        anim_min.start()
        anim_max.start()

        # 防止 GC
        self._anim_min = anim_min
        self._anim_max = anim_max

        self.is_expanded = not self.is_expanded
        self.toggle_btn.setText("←" if self.is_expanded else "☰")

    def _on_animation_finished(self):
        for btn in self.buttons.values():
            btn.set_expanded(self.is_expanded)

    def _load_stylesheet(self):
        qss_path = utils.resource_path("assets/styles/navbar.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"样式文件未找到: {qss_path}")
