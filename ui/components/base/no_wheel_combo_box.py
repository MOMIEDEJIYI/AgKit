from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics

class NoWheelComboBox(QComboBox):
    def __init__(self, parent=None, max_width=200):
        super().__init__(parent)
        self.max_width = max_width

        # 设置省略号策略（避免撑开）
        self.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLength)
        self.setMinimumContentsLength(1)

        # 设置下拉列表的宽度
        self.view().setMinimumWidth(self.max_width)
        self.view().setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def wheelEvent(self, event):
        # 禁用滚轮切换
        event.ignore()

    def addItem(self, text, userData=None):
        """重写 addItem，长内容显示省略号，但保持真实值"""
        fm = QFontMetrics(self.font())
        elided = fm.elidedText(text, Qt.ElideRight, self.max_width)
        super().addItem(elided, userData if userData is not None else text)

    def addItems(self, texts):
        """批量添加 items，支持省略号"""
        for text in texts:
            self.addItem(text)
