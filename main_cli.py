# main_api.py
from rpc_registry import init_registry, is_dev_mode
from api_server import create_api_app
import uvicorn

if __name__ == "__main__":
    init_registry()

    app = create_api_app()
    print("启动 FastAPI JSON 服务：http://127.0.0.1:8000/chat")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        log_config=None,
        use_colors=False
    )
