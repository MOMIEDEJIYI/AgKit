from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QLabel, QSizePolicy, QWidget
from PyQt5.QtCore import Qt, QPropertyAnimation
from utils import utils
import os

class IconTextButton(QPushButton):
    def __init__(self, icon: str, text: str):
        super().__init__()
        self.icon = icon
        self.text = text

        self.setFixedHeight(44)
        self.setObjectName("icon_text_button")
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.icon_label = QLabel(icon)
        self.icon_label.setObjectName("icon_label")
        self.icon_label.setFixedSize(40, 40)
        self.icon_label.setAlignment(Qt.AlignCenter)

        # 创建容器包住文字
        self.text_container = QWidget()
        text_layout = QHBoxLayout(self.text_container)
        text_layout.setContentsMargins(8, 0, 0, 0)  # 保留左侧 8px 间距
        text_layout.setSpacing(0)

        self.text_label = QLabel(text)
        self.text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.text_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.text_label.setFixedWidth(120)
        self.text_label.setMinimumWidth(0)
        self.text_label.setMaximumWidth(120)
        self.text_label.setWordWrap(False)
        self.text_label.setTextInteractionFlags(Qt.NoTextInteraction)
        self.text_label.setStyleSheet("white-space: nowrap;")

        text_layout.addWidget(self.text_label)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_container)

        layout.addStretch()

        self.load_stylesheet()

    def set_expanded(self, expanded: bool):
        target_width = 120 if expanded else 0
        anim = QPropertyAnimation(self.text_container, b"maximumWidth")
        anim.setDuration(250)
        anim.setStartValue(self.text_container.width())
        anim.setEndValue(target_width)
        anim.start()
        self._text_anim = anim

    def set_selected(self, selected: bool):
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def mousePressEvent(self, event):
        # 向上传递点击事件给NavBar
        if self.parent() and hasattr(self.parent(), "on_custom_button_clicked"):
            self.parent().on_custom_button_clicked(self)
        super().mousePressEvent(event)

    def load_stylesheet(self):
        qss_path = utils.resource_path("assets/styles/icon_text_button.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"样式文件没找到: {qss_path}")
