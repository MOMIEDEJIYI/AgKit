from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QLabel,
    QHBoxLayout, QVBoxLayout, QStackedWidget, QSizePolicy, QApplication
)
import os
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QPainterPath
from utils import utils

class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("title_bar")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._drag_pos = None
        self.parent = parent

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)

        self.title_label = QLabel("Agent")
        self.title_label.setObjectName("title_label")
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setObjectName("close_button")
        self.close_button.clicked.connect(self.parent.close)
        layout.addWidget(self.close_button)

        self.load_stylesheet()
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.close_button.geometry().contains(event.pos()):
                self._drag_pos = event.globalPos() - self.parent.frameGeometry().topLeft()
                event.accept()
            else:
                event.ignore()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.parent.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def load_stylesheet(self):
        qss_path = utils.resource_path("assets/styles/title_bar.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.setStyleSheet(content)
        else:
            print(f"样式文件没找到: {qss_path}")

    # def paintEvent(self, event):
    #     painter = QPainter(self)
    #     painter.setRenderHint(QPainter.Antialiasing)
    #     gradient = QLinearGradient(0, 0, 0, self.height())
    #     gradient.setColorAt(0, QColor("#f38181"))
    #     gradient.setColorAt(1, QColor("#dcee79"))
    #     painter.setBrush(gradient)
    #     painter.setPen(Qt.NoPen)

    #     path = QPainterPath()
    #     radius = 8.0
    #     rect = self.rect()

    #     # 只给顶部两个角圆角，底部为直角
    #     path.moveTo(rect.left(), rect.bottom())
    #     path.lineTo(rect.left(), rect.top() + radius)
    #     path.quadTo(rect.left(), rect.top(), rect.left() + radius, rect.top())
    #     path.lineTo(rect.right() - radius, rect.top())
    #     path.quadTo(rect.right(), rect.top(), rect.right(), rect.top() + radius)
    #     path.lineTo(rect.right(), rect.bottom())
    #     path.lineTo(rect.left(), rect.bottom())
    #     path.closeSubpath()

    #     painter.drawPath(path)
