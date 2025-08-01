from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QListWidget, QListWidgetItem,
    QHBoxLayout
)
from PyQt5.QtCore import Qt
import os
import json
from utils import utils


class MethodSnapshotPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("methodSnapshotPanel")

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 卡片容器
        self.card_container = QWidget()
        self.card_container.setObjectName("modelCardContainer")
        card_layout = QVBoxLayout(self.card_container)
        card_layout.setSpacing(15)
        card_layout.setContentsMargins(0, 0, 0, 0)

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

        # 左右主内容区域
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 10, 0, 0)
        card_layout.addLayout(content_layout)

        # 左边包列表
        self.package_list = QListWidget()
        self.package_list.setObjectName("packageList")
        self.package_list.setFixedWidth(200)
        self.package_list.setFocusPolicy(Qt.NoFocus)
        content_layout.addWidget(self.package_list)

        # 右边方法显示区
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setObjectName("methodScrollArea")
        content_layout.addWidget(self.scroll)

        self.right_container = QWidget()
        self.right_container.setObjectName("methodSnapshotRightContainer")
        self.scroll.setWidget(self.right_container)

        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(15, 15, 15, 15)
        self.right_layout.setSpacing(15)

        main_layout.addWidget(self.card_container)

        self.packages = {}         # 包 -> {method_name: meta}
        self.package_widgets = {}  # 包 -> QWidget（缓存渲染结果）
        self.load_method_snapshot()

        self.package_list.currentItemChanged.connect(self.on_package_selected)

        self.load_stylesheet()

    def load_method_snapshot(self):
        snapshot_path = utils.resource_path("runtime/method_registry_snapshot.json")
        if not os.path.exists(snapshot_path):
            label = QLabel(f"方法快照文件不存在: {snapshot_path}")
            label.setObjectName("description")
            self.right_layout.addWidget(label)
            return

        with open(snapshot_path, "r", encoding="utf-8") as f:
            snapshot = json.load(f)

        methods = snapshot.get("methods", {})
        if not methods:
            label = QLabel("方法快照中没有注册任何方法。")
            label.setObjectName("description")
            self.right_layout.addWidget(label)
            return

        # 按包分组方法
        self.packages.clear()
        for method_name, meta in methods.items():
            pkg = meta.get("package", "unknown")
            self.packages.setdefault(pkg, {})[method_name] = meta

        # 左侧列表显示包名
        self.package_list.clear()
        for pkg_name in sorted(self.packages.keys()):
            self.package_list.addItem(pkg_name)

        # 只有包列表有内容时才默认选中第一个包
        if self.package_list.count() > 0:
            self.package_list.setCurrentRow(0)
            # 触发右侧渲染
            self.on_package_selected(self.package_list.currentItem(), None)
        else:
            while self.right_layout.count() > 0:
                item = self.right_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            no_pkg_label = QLabel("无可显示的包")
            no_pkg_label.setObjectName("description")
            self.right_layout.addWidget(no_pkg_label)

    def _create_package_widget(self, pkg_name, methods):
        """构建某个包的右侧 UI 容器"""
        pkg_widget = QWidget()
        pkg_layout = QVBoxLayout(pkg_widget)
        pkg_layout.setContentsMargins(0, 0, 0, 0)
        pkg_layout.setSpacing(15)

        # 包头
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        pkg_label = QLabel(f"包: {pkg_name}")
        pkg_label.setObjectName("packageName")
        all_disabled = all(not meta.get("enabled", True) for meta in methods.values())
        status_text = "已禁用" if all_disabled else "启用中"
        status_color = "#e53e3e" if all_disabled else "#38a169"
        status_label = QLabel(f"<span style='color:{status_color};'>{status_text}</span>")
        status_label.setObjectName("packageStatus")

        header_layout.addWidget(pkg_label)
        header_layout.addWidget(status_label)
        header_layout.addStretch()
        pkg_layout.addWidget(header_widget)

        # 方法卡片
        for method_name, meta in sorted(methods.items()):
            pkg_layout.addWidget(self._create_method_card(method_name, meta))

        pkg_layout.addStretch()  # 保证顶部对齐
        return pkg_widget

    def _create_method_card(self, method_name, meta):
        """构建方法卡片"""
        method_card = QWidget()
        method_card.setObjectName("methodCard")
        method_card.setProperty("class", "methodCard")  # 动态属性，配合QSS类选择器
        method_card_layout = QVBoxLayout(method_card)
        method_card_layout.setContentsMargins(10, 10, 10, 10)
        method_card_layout.setSpacing(5)

        enabled = meta.get("enabled", True)
        description = meta.get("description", "无描述")
        params = meta.get("params", {})

        # 方法名 + 状态
        method_header = QWidget()
        method_header_layout = QHBoxLayout(method_header)
        method_header_layout.setContentsMargins(0, 0, 0, 0)
        method_header_layout.setSpacing(10)

        method_label = QLabel(method_name)
        method_label.setObjectName("methodName")
        if not enabled:
            method_label.setStyleSheet("color: gray;")

        method_status = QLabel("启用中" if enabled else "已禁用")
        method_status.setObjectName("methodStatus")
        method_status.setStyleSheet("color: #38a169;" if enabled else "color: #e53e3e;")

        method_header_layout.addWidget(method_label)
        method_header_layout.addWidget(method_status)
        method_header_layout.addStretch()
        method_card_layout.addWidget(method_header)

        # 描述
        desc_label = QLabel(f"描述: {description}")
        desc_label.setObjectName("description")
        desc_label.setWordWrap(True)
        method_card_layout.addWidget(desc_label)

        # 参数
        if params:
            param_title = QLabel("参数:")
            param_title.setObjectName("paramTitle")
            method_card_layout.addWidget(param_title)

            param_lines = [f"• {k}: {v}" for k, v in params.items()]
            params_label = QLabel("\n".join(param_lines))
            params_label.setObjectName("params")
            params_label.setWordWrap(True)
            method_card_layout.addWidget(params_label)

        return method_card

    def on_package_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        if not current:
            return
        pkg_name = current.text()

        # 隐藏所有已渲染包
        for w in self.package_widgets.values():
            w.hide()

        # 如果没渲染过，先渲染
        if pkg_name not in self.package_widgets:
            pkg_widget = self._create_package_widget(pkg_name, self.packages[pkg_name])
            self.right_layout.addWidget(pkg_widget)
            self.package_widgets[pkg_name] = pkg_widget

        # 显示当前包
        self.package_widgets[pkg_name].show()

    def load_stylesheet(self):
        qss_path = utils.resource_path("assets/styles/method_snapshot_panel.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                qss_content = f.read()
            self.setStyleSheet(qss_content)
        else:
            print(f"样式文件没找到: {qss_path}")
