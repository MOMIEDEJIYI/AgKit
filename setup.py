from cx_Freeze import setup, Executable
from agent.rpc_registry import init_registry
from Cython.Build import cythonize
import os
import shutil
import glob

# 预先生成快照文件
init_registry()

SRC_DIR = os.path.dirname(__file__)

def compile_py_to_pyd():
    """编译除 plugins 外的所有 py 文件"""
    py_files = []
    for root, dirs, files in os.walk(SRC_DIR):
        # 跳过 plugins 目录
        if "plugins" in root:
            continue
        for f in files:
            if f.endswith(".py") and f != "setup.py":
                py_files.append(os.path.join(root, f))
    # 用 Cython 编译
    cythonize(py_files, compiler_directives={"language_level": "3"}, annotate=False)

# 先编译
compile_py_to_pyd()

# 构建选项
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
        ("plugins", "plugins"),  # 保留原始 Python 插件
    ]
}

setup(
    name="AgentApp",
    version="1.0",
    description="AI Agent Desktop App",
    options={"build_exe": build_exe_options},
    executables=[
        Executable("main_gui.py", base="Win32GUI", target_name="ag_gui.exe"),
        Executable("main_cli.py", base=None, target_name="ag_cli.exe"),
    ]
)
