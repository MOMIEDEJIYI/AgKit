from PyQt5.QtWidgets import QApplication, QPushButton, QHBoxLayout, QLabel, QWidget
from PyQt5.QtCore import Qt
import sys

class IconTextButton(QPushButton):
    def __init__(self, icon, text):
        super().__init__()
        self.setObjectName("icon_text_button")
        self.setFixedHeight(44)
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.icon_label = QLabel(icon)
        self.icon_label.setObjectName("icon_label")
        self.icon_label.setFixedSize(20, 20)
        self.icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_label)

        self.text_label = QLabel(text)
        self.text_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        layout.addWidget(self.text_label)

        layout.addStretch()

    def set_selected(self, selected):
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

app = QApplication(sys.argv)

qss = """
QPushButton#icon_text_button {
    background-color: aqua;
    border-radius: 6px;
    border: none;
}

QPushButton#icon_text_button:hover {
    background-color: #f5f5f5;
}

QPushButton#icon_text_button[selected="true"] {
    background-color: #dadada;
    font-weight: bold;
}

QLabel#icon_label {
    background-color: aquamarine;
}
"""

app.setStyleSheet(qss)

window = QWidget()
layout = QHBoxLayout(window)

btn = IconTextButton("💬", "会话")
btn.set_selected(True)

layout.addWidget(btn)

window.show()
sys.exit(app.exec_())
