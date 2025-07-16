from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox
)

class HttpRequestConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HTTP请求配置")
        self.resize(400, 300)

        layout = QVBoxLayout()

        # URL 输入
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("请求URL:"))
        self.url_edit = QLineEdit()
        url_layout.addWidget(self.url_edit)
        layout.addLayout(url_layout)

        # 方法选择 GET/POST/PUT/DELETE...
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("请求方法:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(["GET", "POST", "PUT", "DELETE"])
        method_layout.addWidget(self.method_combo)
        layout.addLayout(method_layout)

        # Headers 输入（JSON格式）
        layout.addWidget(QLabel("请求Headers（JSON格式）:"))
        self.headers_edit = QTextEdit()
        layout.addWidget(self.headers_edit)

        # Body 输入（JSON格式）
        layout.addWidget(QLabel("请求Body（JSON格式）:"))
        self.body_edit = QTextEdit()
        layout.addWidget(self.body_edit)

        # 保存按钮
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存")
        self.cancel_btn = QPushButton("取消")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_config(self):
        # 返回用户输入的数据
        return {
            "url": self.url_edit.text().strip(),
            "method": self.method_combo.currentText(),
            "headers": self.headers_edit.toPlainText().strip(),
            "body": self.body_edit.toPlainText().strip()
        }
