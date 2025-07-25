from cx_Freeze import setup, Executable
from rpc_registry import init_registry
import os

# 预先生成快照文件
init_registry()

build_exe_options = {
    "packages": [
        "ui", "agent", "api_server",
        "uvicorn", "uvicorn.protocols", "uvicorn.loops"
    ],
    "includes": [
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.loops.asyncio",
    ],
    "include_files": [
        ("runtime/method_registry_snapshot.json", "runtime/method_registry_snapshot.json"),
        ("assets", "assets"),
        ("plugins", "plugins")
    ]
}

setup(
    name="AgentApp",
    version="1.0",
    description="AI Agent Desktop App",
    options={"build_exe": build_exe_options},
    executables=[
        Executable("main_gui.py", base="Win32GUI", target_name="ag_gui.exe"),
        Executable("main_cli.py", base=None,      target_name="ag_cli.exe"),
    ]
)
