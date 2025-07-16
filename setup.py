from cx_Freeze import setup, Executable
from tools.rpc_registry import init_registry

# 先生成快照文件
init_registry(dev_mode=True)

build_exe_options = {
    "packages": ["tools", "ui", "agent", "api_server"],  # 你的模块
    "include_files": [
        ("runtime/method_registry_snapshot.json", "runtime/method_registry_snapshot.json"),
        ("assets", "assets"),
    ]
}

setup(
    name="AgentApp",
    version="1.0",
    description="AI Agent Desktop App",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base="Win32GUI", target_name="ag.exe")]
)
