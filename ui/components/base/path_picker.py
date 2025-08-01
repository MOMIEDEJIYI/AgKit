from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout, QFileDialog


class PathPicker(QWidget):
    def __init__(self, default_path="", mode="directory", file_filter="All Files (*.*)", parent=None):
        """
        :param default_path: 默认路径
        :param mode: "directory"（文件夹） 或 "file"（文件）
        :param file_filter: 选择文件时的过滤器，比如 "Text Files (*.txt);;All Files (*.*)"
        """
        super().__init__(parent)
        self.mode = mode
        self.file_filter = file_filter

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # 输入框
        self.line_edit = QLineEdit(default_path)
        self.line_edit.setObjectName("styledInput")
        self.line_edit.setMinimumHeight(40)

        # 浏览按钮
        self.browse_button = QPushButton("浏览…")
        self.browse_button.setObjectName("secondaryButton")
        self.browse_button.setFixedHeight(40)
        self.browse_button.setFixedWidth(70)

        layout.addWidget(self.line_edit, 1)
        layout.addWidget(self.browse_button)

        self.browse_button.clicked.connect(self.choose_path)

        # 局部样式
        self.setStyleSheet("""
          QPushButton#secondaryButton {
              background-color: #f0f0f0;
              border: 1px solid #cccccc;
              border-radius: 6px;
              padding: 4px 8px;
              color: #333;
          }
          QPushButton#secondaryButton:hover {
              background-color: #e6e6e6;
          }
          QPushButton#secondaryButton:pressed {
              background-color: #d9d9d9;
          }
        """)

    def choose_path(self):
        if self.mode == "directory":
            dir_path = QFileDialog.getExistingDirectory(self, "选择文件夹", self.line_edit.text() or ".")
            if dir_path:
                self.line_edit.setText(dir_path)
        elif self.mode == "file":
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择文件", self.line_edit.text() or ".", self.file_filter
            )
            if file_path:
                self.line_edit.setText(file_path)

    def text(self):
        return self.line_edit.text().strip()

    def setText(self, value: str):
        self.line_edit.setText(value)
