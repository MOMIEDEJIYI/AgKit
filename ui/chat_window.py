import sys
import os
import platform
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QLabel,
    QHBoxLayout, QVBoxLayout, QStackedWidget, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QRect, QEasingCurve
from utils import utils
from ui.components.navbar import NavBar
from ui.components.chat_panel import ChatPanel
from ui.components.request_panel import RequestPanel
from ui.components.title_bar import TitleBar

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(900, 600)
        self.setObjectName("main_window")

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 只给内容区设置白色背景和圆角，不给整个窗口
        content_widget = QWidget()
        content_widget.setObjectName("content_widget")
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(12)

        self.navbar = NavBar(on_nav_click=self.switch_page)
        self.navbar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        content_layout.addWidget(self.navbar)

        self.content_area = QStackedWidget()
        self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chat_panel = ChatPanel()
        self.request_panel = RequestPanel()
        self.content_area.addWidget(self.chat_panel)
        self.content_area.addWidget(self.request_panel)
        content_layout.addWidget(self.content_area)
        
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(content_widget)

        self.setCentralWidget(central_widget)

        # 磨砂效果调用
        self.apply_blur_effect()

        self.load_stylesheet()
        self.switch_page("chat")

    def apply_blur_effect(self):
        system = platform.system()
        if system == 'Windows':
            try:
                from BlurWindow.blurWindow import GlobalBlur
                GlobalBlur(self.winId(), Dark=True, QWidget=self)
                print("Windows: BlurWindow applied")
            except ImportError:
                print("Windows: BlurWindow 未安装，无法使用磨砂效果")
        elif system == 'Darwin':  # macOS
            try:
                import objc
                from Cocoa import NSVisualEffectView, NSView, NSWindow
                self.enable_macos_vibrancy()
                print("macOS: Vibrancy applied")
            except ImportError:
                print("macOS: pyobjc 未安装，无法使用磨砂效果")

    def enable_macos_vibrancy(self):
        import objc
        from Cocoa import NSVisualEffectView, NSView

        ns_win = objc.objc_object(c_void_p=self.winId())
        content_view = ns_win.contentView()

        effect_view = NSVisualEffectView.alloc().initWithFrame_(content_view.frame())
        effect_view.setAutoresizingMask_(NSView.width | NSView.height)
        effect_view.setMaterial_(1)
        effect_view.setBlendingMode_(0)
        effect_view.setState_(1)
        content_view.addSubview_(effect_view)
    def load_stylesheet(self):
        qss_path = utils.resource_path("assets/styles/chat_window.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.setStyleSheet(content)
        else:
            print(f"样式文件没找到: {qss_path}")

    def switch_page(self, page):
        if page == "chat":
            self.content_area.setCurrentIndex(0)
        elif page == "request":
            self.content_area.setCurrentIndex(1)

    def show_with_animation(self):
        screen = self.screen().availableGeometry()
        final_rect = QRect(
            (screen.width() - 900) // 2,
            (screen.height() - 600) // 2,
            900,
            600,
        )
        start_rect = QRect(
            final_rect.center().x(),
            final_rect.center().y(),
            0,
            0,
        )
        self.setGeometry(start_rect)
        self.setWindowOpacity(0)
        self.show()

        self.anim_geometry = QPropertyAnimation(self, b"geometry")
        self.anim_geometry.setDuration(400)
        self.anim_geometry.setStartValue(start_rect)
        self.anim_geometry.setEndValue(final_rect)
        self.anim_geometry.setEasingCurve(QEasingCurve.OutBack)

        self.anim_opacity = QPropertyAnimation(self, b"windowOpacity")
        self.anim_opacity.setDuration(400)
        self.anim_opacity.setStartValue(0)
        self.anim_opacity.setEndValue(1)

        self.anim_geometry.start()
        self.anim_opacity.start()
