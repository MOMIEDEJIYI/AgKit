# main_gui.py
import sys
from PyQt5.QtWidgets import QApplication
from ui.chat_window import ChatWindow
from agent.rpc_registry import init_registry

if __name__ == "__main__":
    init_registry()

    app = QApplication(sys.argv)
    window = ChatWindow()
    window.resize(900, 600)
    window.show_with_animation()
    sys.exit(app.exec())
