from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
import os
import json
from utils import utils


class MethodSnapshotPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("methodSnapshotPanel")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 卡片容器
        self.card_container = QWidget()
        self.card_container.setObjectName("modelCardContainer")
        card_layout = QVBoxLayout(self.card_container)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)

        # 标题
        title_label = QLabel("方法注册快照")
        title_label.setObjectName("cardTitle")
        card_layout.addWidget(title_label)

        # 分割线
        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        card_layout.addWidget(divider)

        # 滚动区域
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        card_layout.addWidget(self.scroll)

        self.container = QWidget()
        self.container.setObjectName("methodSnapshotContainer")
        self.scroll.setWidget(self.container)

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(10, 10, 10, 10)
        self.container_layout.setSpacing(20)

        main_layout.addWidget(self.card_container)

        self.load_method_snapshot()

        self.setStyleSheet("""
        /* 整体卡片容器 */
        #modelCardContainer {
            background-color: #ffffff;
            border-radius: 12px;
            font-family: 'Microsoft YaHei';
            border: 1px solid #e2e8f0;
        }

        /* 卡片标题 */
        #cardTitle {
            font-size: 18px;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 10px;
        }

        /* 分割线 */
        #divider {
            border: 1px solid #edf2f7;
            margin: 0;
        }

        /* 方法名称 */
        QLabel#methodName {
            font-size: 16px;
            font-weight: 600;
            color: #2b6cb0;
        }

        /* 描述文本 */
        QLabel#description {
            font-size: 14px;
            color: #4a5568;
            margin-top: 4px;
            margin-bottom: 8px;
        }

        /* 参数列表 */
        QLabel#params {
            font-size: 13px;
            color: #718096;
            margin-left: 15px;
            white-space: pre-wrap;
        }

        /* 分割线条 */
        QFrame#methodDivider {
            background-color: #e2e8f0;
            max-height: 1px;
            min-height: 1px;
            margin-top: 15px;
            margin-bottom: 15px;
            border: none;
        }
        """)

    def load_method_snapshot(self):
        snapshot_path = utils.resource_path("runtime/method_registry_snapshot.json")
        if not os.path.exists(snapshot_path):
            label = QLabel(f"方法快照文件不存在: {snapshot_path}")
            label.setObjectName("description")
            self.container_layout.addWidget(label)
            return

        with open(snapshot_path, "r", encoding="utf-8") as f:
            snapshot = json.load(f)

        methods = snapshot.get("methods", [])
        docs = snapshot.get("docs", {})

        if not methods:
            label = QLabel("方法快照中没有注册任何方法。")
            label.setObjectName("description")
            self.container_layout.addWidget(label)
            return

        for method_name in methods:
            doc = docs.get(method_name, {})
            description = doc.get("description", "无描述")
            params = doc.get("params", {})

            # 方法名
            method_label = QLabel(method_name)
            method_label.setObjectName("methodName")
            self.container_layout.addWidget(method_label)

            # 描述
            desc_label = QLabel(f"描述: {description}")
            desc_label.setObjectName("description")
            desc_label.setWordWrap(True)
            self.container_layout.addWidget(desc_label)

            # 参数
            if params:
                param_lines = []
                for param_name, param_desc in params.items():
                    param_lines.append(f"{param_name}: {param_desc}")
                params_label = QLabel("\n".join(param_lines))
                params_label.setObjectName("params")
                params_label.setWordWrap(True)
                self.container_layout.addWidget(params_label)

            # 方法间分割线
            method_divider = QFrame()
            method_divider.setObjectName("methodDivider")
            method_divider.setFrameShape(QFrame.HLine)
            method_divider.setFrameShadow(QFrame.Plain)
            self.container_layout.addWidget(method_divider)
