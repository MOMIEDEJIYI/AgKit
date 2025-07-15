import sys
import os
from PyQt5.QtWidgets import QApplication
from ui.chat_window import ChatWindow

def load_stylesheet(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def print_registered_methods():
    from tools.rpc_registry import METHOD_REGISTRY
    print("📌 已注册的 JSON-RPC 方法:")
    for name in sorted(METHOD_REGISTRY.keys()):
        func = METHOD_REGISTRY[name]
        print(f" - {name}: {func.__module__}.{func.__name__}")

if __name__ == "__main__":
    print_registered_methods()
    app = QApplication(sys.argv)
    style_path = os.path.join(os.path.dirname(__file__), "assets", "style.qss")
    stylesheet = load_stylesheet(style_path)
    app.setStyleSheet(stylesheet)
    window = ChatWindow()
    window.resize(900, 600)
    window.show()
    sys.exit(app.exec())
