# main_api.py
from agent.rpc_registry import init_registry
from api.api_server import create_api_app
import uvicorn
import socket
from fastapi.middleware.cors import CORSMiddleware

def find_free_port(start_port=8000, max_port=8100):
    port = start_port
    while port <= max_port:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError(f"No free port found between {start_port} and {max_port}")

if __name__ == "__main__":
    init_registry()

    app = create_api_app()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],  # 你前端地址
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    port = find_free_port(8000, 8100)
    print(f"启动 FastAPI JSON 服务：http://127.0.0.1:{port}")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info",
        log_config=None,
        use_colors=False
    )
