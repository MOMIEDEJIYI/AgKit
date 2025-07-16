import sys
import argparse
from PyQt5.QtWidgets import QApplication
from ui.chat_window import ChatWindow
from tools.rpc_registry import init_registry, is_dev_mode, METHOD_REGISTRY, METHOD_DOCS
from api_server import create_api_app
import uvicorn

def print_registered_methods():
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
    # 注册方法
    init_registry(dev_mode=is_dev_mode())

    # 解析 CLI 参数
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-ui", action="store_true", help="不加载 UI，仅作为 API 服务运行")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="API 监听地址")
    parser.add_argument("--port", type=int, default=8000, help="API 监听端口")
    args = parser.parse_args()

    # 无 UI 模式下挂载 API 服务
    if args.no_ui:
        app = create_api_app()
        print(f"启动 FastAPI JSON 服务：http://{args.host}:{args.port}/chat")
        uvicorn.run(app, host=args.host, port=args.port)
        sys.exit(0)

    app = QApplication(sys.argv)
    window = ChatWindow()
    window.resize(900, 600)
    window.show_with_animation()
    sys.exit(app.exec())
