from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QFont, QColor

class PopupDialog(QDialog):
    def __init__(self, title="提示", message="", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        self.setFixedSize(380, 220)

        # 主容器
        container = QFrame(self)
        container.setObjectName("container")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 25)
        layout.setSpacing(20)

        # 标题
        title_label = QLabel(title)
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        layout.addWidget(title_label)

        # 分隔线
        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFixedHeight(1)
        layout.addWidget(divider)

        # 消息内容
        self.message_label = QLabel(message)
        self.message_label.setObjectName("message_label")
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setFont(QFont("Microsoft YaHei", 12))
        layout.addWidget(self.message_label, 1)

        # 按钮容器
        button_container = QFrame()
        button_container.setObjectName("button_container")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(15)
        button_layout.setAlignment(Qt.AlignCenter)

        self.ok_button = QPushButton("好的")
        self.ok_button.setObjectName("ok_button")
        self.ok_button.setFixedSize(120, 42)
        self.ok_button.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

        layout.addWidget(button_container)

        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)

        self.load_stylesheet()
        self.set_shadow_effect()

    def set_shadow_effect(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

    def load_stylesheet(self):
        self.setStyleSheet("""
             /* 主容器样式 */
            #container {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 18px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            /* 标题样式 */
            #title_label {
                color: #2D3748;
                font-size: 18px;
                font-weight: bold;
            }
            
            /* 分隔线样式 */
            #divider {
                background-color: rgba(226, 232, 240, 0.6);
                border: none;
            }
            
            /* 消息内容样式 */
            #message_label {
                color: #4A5568;
                font-size: 14px;
                line-height: 1.5;
                padding: 10px 0;
            }
            
            /* 按钮容器样式 */
            #button_container {
                background-color: transparent;
            }
            
            /* 按钮基础样式 */
            #ok_button {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4F46E5, stop:1 #6366F1
                );
                color: white;
                border-radius: 12px;
                font-weight: 600;
            }
            
            /* 按钮悬停状态 */
            #ok_button:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4338CA, stop:1 #4F46E5
                );
            }
            
            /* 按钮按下状态 */
            #ok_button:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3730A3, stop:1 #4338CA
                );
            }
        """)

    def showEvent(self, event):
        super().showEvent(event)

        # 居中弹窗
        if self.parent():
            parent_geom = self.parent().geometry()
            x = parent_geom.x() + (parent_geom.width() - self.width()) // 2
            y = parent_geom.y() + (parent_geom.height() - self.height()) // 2
        else:
            screen = self.screen().availableGeometry()
            x = screen.x() + (screen.width() - self.width()) // 2
            y = screen.y() + (screen.height() - self.height()) // 2

        self.move(x, y + 20)  # 初始位置略微偏下

        # 淡入动画
        self.setWindowOpacity(0)
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(300)
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.opacity_anim.start()

        # 上移动画
        self.pos_anim = QPropertyAnimation(self, b"pos")
        self.pos_anim.setDuration(350)
        self.pos_anim.setStartValue(self.pos())
        self.pos_anim.setEndValue(QPoint(x, y))
        self.pos_anim.setEasingCurve(QEasingCurve.OutBack)
        self.pos_anim.start()

    def closeEvent(self, event):
        # 淡出动画
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(250)
        self.opacity_anim.setStartValue(1)
        self.opacity_anim.setEndValue(0)
        self.opacity_anim.finished.connect(super().close)
        self.opacity_anim.start()
        event.ignore()
