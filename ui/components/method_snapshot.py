from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QListWidget, QListWidgetItem,
    QHBoxLayout, QPushButton, QSizePolicy, QTextBrowser
)
from PyQt5.QtCore import Qt
import os
import json
from utils import utils
from agent.rpc_registry import enable_method, disable_method, enable_package, disable_package
from utils.event_bus import event_bus

class MethodSnapshotPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("methodSnapshotPanel")
        # 订阅更新事件
        event_bus.subscribe("methods_updated", self.load_method_snapshot)

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

    def load_method_snapshot(self, **kwargs):
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
        pkg_widget = QWidget()
        pkg_layout = QVBoxLayout(pkg_widget)
        pkg_layout.setContentsMargins(0, 0, 0, 0)
        pkg_layout.setSpacing(15)

        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        # 包名容器，保证换行
        pkg_label_container = QWidget()
        pkg_label_layout = QVBoxLayout(pkg_label_container)
        pkg_label_layout.setContentsMargins(0, 0, 0, 0)
        pkg_label = QLabel(f"包: {pkg_name}")
        pkg_label.setObjectName("packageName")
        pkg_label.setWordWrap(True)
        pkg_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        pkg_label_layout.addWidget(pkg_label)

        all_disabled = all(not meta.get("enabled", True) for meta in methods.values())
        status_text = "已禁用" if all_disabled else "启用中"
        status_color = "#e53e3e" if all_disabled else "#38a169"
        status_label = QLabel(f"<span style='color:{status_color};'>{status_text}</span>")
        status_label.setObjectName("packageStatus")

        toggle_btn = QPushButton("启用" if all_disabled else "禁用")
        toggle_btn.setFixedWidth(60)

        def on_toggle_package():
            if toggle_btn.text() == "启用":
                enable_package(pkg_name)
                toggle_btn.setText("禁用")
                status_label.setText("<span style='color:#38a169;'>启用中</span>")
                self._refresh_package_methods(pkg_name, True)
            else:
                disable_package(pkg_name)
                toggle_btn.setText("启用")
                status_label.setText("<span style='color:#e53e3e;'>已禁用</span>")
                self._refresh_package_methods(pkg_name, False)

        toggle_btn.clicked.connect(on_toggle_package)

        header_layout.addWidget(pkg_label_container, 1)
        header_layout.addWidget(status_label, 0)
        header_layout.addWidget(toggle_btn, 0)
        header_layout.addStretch()
        pkg_layout.addWidget(header_widget)

        # 方法卡片
        for method_name, meta in sorted(methods.items()):
            pkg_layout.addWidget(self._create_method_card(method_name, meta))

        pkg_layout.addStretch()
        return pkg_widget

    def _create_method_card(self, method_name, meta):
        method_card = QWidget()
        method_card.setObjectName("methodCard")
        method_card.setProperty("class", "methodCard")
        method_card_layout = QVBoxLayout(method_card)
        method_card_layout.setContentsMargins(10, 10, 10, 10)
        method_card_layout.setSpacing(5)

        enabled = meta.get("enabled", True)
        description = meta.get("description", "无描述")
        params = meta.get("params", {})

        # -----------------------
        # 方法名 + 状态 + 按钮
        # -----------------------
        method_header = QWidget()
        method_header_layout = QHBoxLayout(method_header)
        method_header_layout.setContentsMargins(0, 0, 0, 0)
        method_header_layout.setSpacing(10)

        # 方法名用 QTextBrowser 自动换行 + 高度自适应
        method_label = QTextBrowser()
        method_label.setObjectName("methodName")
        method_label.setText(method_name)
        method_label.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        method_label.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        method_label.setStyleSheet("background: transparent; border: none;")
        method_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        method_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # 去掉 widget 内边距
        method_label.setContentsMargins(0, 0, 0, 0)

        # 去掉 QTextDocument 的默认边距
        doc = method_label.document()
        doc.setDocumentMargin(0)

        if not enabled:
            method_label.setStyleSheet("color: gray; background: transparent; border: none;")
        # 根据内容调整 QTextBrowser 高度
        def adjust_method_label_height():
            method_label.document().setTextWidth(method_label.viewport().width())
            doc_height = method_label.document().size().height()
            method_label.setFixedHeight(int(doc_height) + 2)

        method_header.resizeEvent = lambda event: adjust_method_label_height()
        adjust_method_label_height()

        # 状态标签
        method_status = QLabel("启用中" if enabled else "已禁用")
        method_status.setObjectName("methodStatus")
        method_status.setFixedWidth(40)
        method_status.setStyleSheet("color: #38a169;" if enabled else "color: #e53e3e;")

        # 按钮
        toggle_btn = QPushButton("禁用" if enabled else "启用")
        toggle_btn.setFixedWidth(60)

        # 添加到水平布局，状态和按钮顶对齐
        method_header_layout.addWidget(method_label, 1)
        method_header_layout.addWidget(method_status, 0, Qt.AlignTop)
        method_header_layout.addWidget(toggle_btn, 0, Qt.AlignTop)

        # 按钮逻辑
        def on_toggle():
            if toggle_btn.text() == "启用":
                enable_method(method_name)
                toggle_btn.setText("禁用")
                method_status.setText("启用中")
                method_status.setStyleSheet("color: #38a169;")
                method_label.setStyleSheet("background: transparent; border: none;")
            else:
                disable_method(method_name)
                toggle_btn.setText("启用")
                method_status.setText("已禁用")
                method_status.setStyleSheet("color: #e53e3e;")
                method_label.setStyleSheet("color: gray; background: transparent; border: none;")

        toggle_btn.clicked.connect(on_toggle)
        method_card_layout.addWidget(method_header)

        # -----------------------
        # 描述
        # -----------------------
        desc_label = QLabel(f"描述: {description}")
        desc_label.setObjectName("description")
        desc_label.setWordWrap(True)
        desc_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        method_card_layout.addWidget(desc_label)

        # -----------------------
        # 参数
        # -----------------------
        if params:
            param_title = QLabel("参数:")
            param_title.setObjectName("paramTitle")
            method_card_layout.addWidget(param_title)

            param_lines = [f"• {k}: {v}" for k, v in params.items()]
            params_label = QLabel("\n".join(param_lines))
            params_label.setObjectName("params")
            params_label.setWordWrap(True)
            params_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            method_card_layout.addWidget(params_label)

        return method_card

    def _refresh_package_methods(self, pkg_name, enabled):
        if pkg_name not in self.package_widgets:
            return
        pkg_widget = self.package_widgets[pkg_name]
        # 遍历包内所有方法卡片，更新按钮和状态
        for i in range(pkg_widget.layout().count()):
            item = pkg_widget.layout().itemAt(i)
            if item is None:
                continue
            widget = item.widget()
            if widget is None:
                continue
            # 找到 methodCard（方法卡片）
            if widget.objectName() == "methodCard":
                # 找到方法名、状态标签和按钮
                method_label = widget.findChild(QLabel, "methodName")
                method_label.setWordWrap(True)
                method_status = widget.findChild(QLabel, "methodStatus")
                toggle_btn = widget.findChild(QPushButton)
                if not method_label or not method_status or not toggle_btn:
                    continue
                if enabled:
                    method_status.setText("启用中")
                    method_status.setStyleSheet("color: #38a169;")
                    toggle_btn.setText("禁用")
                    method_label.setStyleSheet("")
                else:
                    method_status.setText("已禁用")
                    method_status.setStyleSheet("color: #e53e3e;")
                    toggle_btn.setText("启用")
                    method_label.setStyleSheet("color: gray;")

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
