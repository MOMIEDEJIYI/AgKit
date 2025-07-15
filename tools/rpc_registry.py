import os
import importlib

METHOD_REGISTRY = {}
METHOD_DOCS = {}  # 新增：存参数说明

def register_method(name, param_desc=None):
    def decorator(func):
        METHOD_REGISTRY[name] = func
        if param_desc:
            METHOD_DOCS[name] = param_desc
        return func
    return decorator

def init_registry(dirs=None):
    """
    自动导入多个目录下的模块，实现自动注册。
    参数 dirs 是目录列表，默认扫描 system 目录。
    """
    if dirs is None:
        dirs = ["system"]

    base_dir = os.path.dirname(__file__)
    for dir_name in dirs:
        dir_path = os.path.join(base_dir, dir_name)
        if not os.path.isdir(dir_path):
            print(f"⚠️ 目录不存在，跳过: {dir_path}")
            continue

        for filename in os.listdir(dir_path):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = f"tools.system.{filename[:-3]}"
                importlib.import_module(module_name)

# 脚本导入时自动初始化，默认扫描 system
init_registry()
