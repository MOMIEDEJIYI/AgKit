from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

class ConfirmDialog(QDialog):
    def __init__(self, title="确认操作", message="你确定要执行此操作吗？", yes_text="确认", no_text="取消", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(320, 160)

        self.result = False  # 默认结果为取消

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        label = QLabel(message)
        label.setWordWrap(True)
        layout.addWidget(label)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton(no_text)
        confirm_btn = QPushButton(yes_text)

        confirm_btn.setObjectName("primaryButton")
        cancel_btn.setObjectName("secondaryButton")

        cancel_btn.clicked.connect(self.reject)
        confirm_btn.clicked.connect(self.accept)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(confirm_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def exec_and_get_result(self):
        result = self.exec_()
        return result == QDialog.Accepted
