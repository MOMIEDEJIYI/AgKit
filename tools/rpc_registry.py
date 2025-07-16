import os
import json
import importlib
import sys

METHOD_REGISTRY = {}
METHOD_DOCS = {}  # 存参数说明

base_dir = os.path.dirname(sys.argv[0])
SNAPSHOT_PATH = os.path.join(base_dir, "runtime", "method_registry_snapshot.json")

def register_method(name, param_desc=None):
    def decorator(func):
        METHOD_REGISTRY[name] = func
        if param_desc:
            METHOD_DOCS[name] = param_desc
        return func
    return decorator

def save_snapshot():
    os.makedirs(os.path.dirname(SNAPSHOT_PATH), exist_ok=True)

    # 检查每个注册方法是否有参数说明
    missing_desc = [name for name in METHOD_REGISTRY if name not in METHOD_DOCS]
    if missing_desc:
        print("以下方法缺少参数说明（param_desc）:")
        for name in missing_desc:
            func = METHOD_REGISTRY[name]
            print(f" - {name}: {func.__module__}.{func.__name__}")
        print("请为每个方法添加参数说明后重试。")
        sys.exit(1)  # 终止程序

    snapshot = {
        "methods": list(METHOD_REGISTRY.keys()),
        "docs": METHOD_DOCS
    }
    with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"方法注册快照已保存到 {SNAPSHOT_PATH}")


def infer_module_from_method(method_name):
    # 按实际规则调整，比如方法名对应模块名，模块在 tools.system 下
    return f"tools.system.{method_name}"

def load_snapshot():
    global METHOD_REGISTRY, METHOD_DOCS
    if not os.path.exists(SNAPSHOT_PATH):
        raise FileNotFoundError(f"快照文件不存在：{SNAPSHOT_PATH}")
    with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
        snapshot = json.load(f)

    METHOD_DOCS.clear()
    METHOD_REGISTRY.clear()

    METHOD_DOCS.update(snapshot.get("docs", {}))

    # 导入所有模块，让装饰器执行注册
    for method_name in snapshot.get("methods", []):
        module_name = infer_module_from_method(method_name)
        try:
            importlib.import_module(module_name)
        except Exception as e:
            print(f"加载模块 {module_name} 失败: {e}")

    print(f"从快照加载了 {len(snapshot.get('methods', []))} 个方法")

def init_registry(dirs=None, dev_mode=True):
    """
    dev_mode=True 时扫描目录导入，注册完成后保存快照
    dev_mode=False 时直接加载快照，避免运行时扫描
    """
    if dev_mode:
        if dirs is None:
            dirs = ["system"]

        base_dir = os.path.dirname(__file__)
        for dir_name in dirs:
            dir_path = os.path.join(base_dir, dir_name)
            if not os.path.isdir(dir_path):
                print(f"目录不存在，跳过: {dir_path}")
                continue

            for filename in os.listdir(dir_path):
                if filename.endswith(".py") and not filename.startswith("__"):
                    module_name = f"tools.{dir_name}.{filename[:-3]}"
                    importlib.import_module(module_name)

        # 只在开发时保存快照，避免每次启动都写文件
        save_snapshot()
    else:
        load_snapshot()

def is_dev_mode():
    import sys
    if getattr(sys, "frozen", False):
        return False
    return True
