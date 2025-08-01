from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QSizePolicy
)
import os
import json
from utils import utils

class MethodSnapshotPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll)

        self.container = QWidget()
        self.scroll.setWidget(self.container)

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(10, 10, 10, 10)
        self.container_layout.setSpacing(10)

        self.load_method_snapshot()

    def load_method_snapshot(self):
        snapshot_path = utils.resource_path("runtime/method_registry_snapshot.json")
        if not os.path.exists(snapshot_path):
            label = QLabel(f"方法快照文件不存在: {snapshot_path}")
            self.container_layout.addWidget(label)
            return

        with open(snapshot_path, "r", encoding="utf-8") as f:
            snapshot = json.load(f)

        methods = snapshot.get("methods", [])
        docs = snapshot.get("docs", {})

        if not methods:
            label = QLabel("方法快照中没有注册任何方法。")
            self.container_layout.addWidget(label)
            return

        for method_name in methods:
            doc = docs.get(method_name, {})
            description = doc.get("description", "无描述")
            params = doc.get("params", {})

            # 方法名加粗显示
            method_label = QLabel(f"<b>{method_name}</b>")
            self.container_layout.addWidget(method_label)

            # 描述
            desc_label = QLabel(f"描述: {description}")
            desc_label.setWordWrap(True)
            self.container_layout.addWidget(desc_label)

            # 参数列表（简单展示）
            if params:
                param_lines = []
                for param_name, param_desc in params.items():
                    param_lines.append(f"{param_name}: {param_desc}")
                params_label = QLabel("参数:\n" + "\n".join(param_lines))
                params_label.setWordWrap(True)
                params_label.setStyleSheet("color: gray; font-size: 11pt;")
                self.container_layout.addWidget(params_label)

            # 分割线
            divider = QLabel("<hr>")
            self.container_layout.addWidget(divider)
