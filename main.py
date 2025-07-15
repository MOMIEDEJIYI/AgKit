import sys
import os
import argparse
from PyQt5.QtWidgets import QApplication
from ui.chat_window import ChatWindow

def print_registered_methods():
    from tools.rpc_registry import METHOD_REGISTRY, METHOD_DOCS
    print("📌 已注册的 JSON-RPC 方法:")
    for name in sorted(METHOD_REGISTRY.keys()):
        func = METHOD_REGISTRY[name]
        param_desc = METHOD_DOCS.get(name)
        print(f" - {name}: {func.__module__}.{func.__name__}")
        if param_desc:
            print("   参数说明:")
            for k, v in param_desc.items():
                print(f"     • {k}: {v}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-ui", action="store_true", help="不加载 UI，仅打印方法")
    args = parser.parse_args()

    print_registered_methods()

    if args.no_ui:
        print("✅ CLI 模式：未加载 UI")
        sys.exit(0)

    app = QApplication(sys.argv)
    window = ChatWindow()
    window.resize(900, 600)
    window.show_with_animation()   # 使用带动画的显示方式
    sys.exit(app.exec())
