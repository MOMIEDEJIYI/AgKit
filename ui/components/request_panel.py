from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)

class RequestPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("这里是请求面板")
        layout.addWidget(label)
