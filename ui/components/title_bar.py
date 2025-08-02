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

        # 标题
        self.title_label = QLabel("Agent")
        self.title_label.setObjectName("title_label")
        layout.addWidget(self.title_label)
        layout.addStretch()

        # 最小化按钮
        self.min_button = QPushButton("—")
        self.min_button.setFixedSize(30, 30)
        self.min_button.setObjectName("min_button")
        self.min_button.clicked.connect(self.parent.showMinimized)
        layout.addWidget(self.min_button)

        # 最大化/还原按钮
        self.max_button = QPushButton("⬜")
        self.max_button.setFixedSize(30, 30)
        self.max_button.setObjectName("max_button")
        self.max_button.clicked.connect(self.toggle_max_restore)
        layout.addWidget(self.max_button)

        # 关闭按钮
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setObjectName("close_button")
        self.close_button.clicked.connect(self.parent.close)
        layout.addWidget(self.close_button)

        self.load_stylesheet()

    def toggle_max_restore(self):
        """切换最大化 / 还原"""
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.max_button.setText("⬜")  # 还原后显示最大化符号
        else:
            self.parent.showMaximized()
            self.max_button.setText("❐")  # 最大化后显示还原符号

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not (self.close_button.geometry().contains(event.pos()) or 
                    self.min_button.geometry().contains(event.pos()) or 
                    self.max_button.geometry().contains(event.pos())):
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

    def load_stylesheet(self):
        qss_path = utils.resource_path("assets/styles/title_bar.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"样式文件没找到: {qss_path}")
