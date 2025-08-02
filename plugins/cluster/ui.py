from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class ClusterPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("这是集群管理页面")
        layout.addWidget(label)

def get_ui_pages():
    return [
        ("cluster", ClusterPage(), "🔗", "集群管理", False),
    ]
