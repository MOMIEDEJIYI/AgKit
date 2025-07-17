from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel
)
from PyQt5.QtCore import Qt

class ChatBubble(QWidget):
    def __init__(self, text, is_user=True):
        super().__init__()
        self.is_user = is_user
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 10, 2)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setMaximumWidth(400)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # 允许选中文本

        if is_user:
            layout.addStretch()  # 左边留空，右对齐
            layout.addWidget(label)
            label.setStyleSheet("""
                background-color: #d1eaff;
                color: #000;
                border-radius: 12px;
                padding: 8px;
            """)
        else:
            layout.addWidget(label)
            layout.addStretch()  # 右边留空，左对齐
            label.setStyleSheet("""
                background-color: #f0f0f0;
                color: #333;
                border-radius: 12px;
                padding: 8px;
            """)

        self.setLayout(layout)