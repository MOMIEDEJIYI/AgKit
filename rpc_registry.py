import os
import json
import importlib
import sys
import inspect

METHOD_REGISTRY = {}
METHOD_DOCS = {}  # 存参数说明
METHOD_FLAGS = {}

if getattr(sys, "frozen", False):
    # 打包模式：获取 exe 所在目录
    base_dir = os.path.dirname(sys.executable)
else:
    # 开发模式：当前文件路径
    base_dir = os.path.dirname(__file__)

# 插件目录和快照路径
PLUGINS_DIR = os.path.join(base_dir, "plugins")
SNAPSHOT_PATH = os.path.join(base_dir, "runtime", "method_registry_snapshot.json")

# 插入 sys.path 以便 import plugins.xxx
if PLUGINS_DIR not in sys.path:
    sys.path.insert(0, PLUGINS_DIR)
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)


def register_method(name, param_desc=None, description=None, **flags):
    def decorator(func):
        sig = inspect.signature(func)
        if len(sig.parameters) == 0:
            raise ValueError(f"注册的方法 {name} 必须至少接收一个参数 (params)，不使用请设置为params=None")
        METHOD_REGISTRY[name] = func
        METHOD_DOCS[name] = {
            "description": description or "",
            "params": param_desc or {}
        }
        METHOD_FLAGS[name] = flags
        return func
    return decorator


def save_snapshot():
    os.makedirs(os.path.dirname(SNAPSHOT_PATH), exist_ok=True)

    missing_desc = []
    for name in METHOD_REGISTRY:
        doc = METHOD_DOCS.get(name)
        if not doc or not doc.get("description", "").strip():
            missing_desc.append(name)

    if missing_desc:
        print("以下方法缺少描述（description）不利于模型理解，请为每个方法添加描述后重试：")
        for name in missing_desc:
            func = METHOD_REGISTRY[name]
            print(f" - {name}: {func.__module__}.{func.__name__}")
        sys.exit(1)

    snapshot = {
        "methods": list(METHOD_REGISTRY.keys()),
        "docs": METHOD_DOCS
    }
    with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"方法注册快照已保存到 {SNAPSHOT_PATH}")


def infer_module_from_method(method_name):
    """
    假设快照里的方法名格式：
    - 带子目录，如 "system.read_files"
    - 不带子目录，默认归到 "system" 子目录
    """
    if '.' in method_name:
        return f"plugins.{method_name}"
    else:
        return f"plugins.system.{method_name}"


def load_snapshot():
    global METHOD_REGISTRY, METHOD_DOCS
    if not os.path.exists(SNAPSHOT_PATH):
        raise FileNotFoundError(f"快照文件不存在：{SNAPSHOT_PATH}")
    with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
        snapshot = json.load(f)

    METHOD_DOCS.clear()
    METHOD_REGISTRY.clear()
    METHOD_DOCS.update(snapshot.get("docs", {}))

    for method_name in snapshot.get("methods", []):
        module_name = infer_module_from_method(method_name)
        try:
            importlib.import_module(module_name)
        except Exception as e:
            print(f"加载模块 {module_name} 失败: {e}")

    print(f"从快照加载了 {len(snapshot.get('methods', []))} 个方法")


def init_registry():
    if not os.path.isdir(PLUGINS_DIR):
        print(f"插件目录不存在，跳过扫描: {PLUGINS_DIR}")
        return

    sub_dirs = [d for d in os.listdir(PLUGINS_DIR) if os.path.isdir(os.path.join(PLUGINS_DIR, d))]
    print("扫描路径为：", PLUGINS_DIR)

    for sub_dir in sub_dirs:
        dir_path = os.path.join(PLUGINS_DIR, sub_dir)
        for filename in os.listdir(dir_path):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                full_module = f"plugins.{sub_dir}.{module_name}"
                try:
                    importlib.import_module(full_module)
                except Exception as e:
                    print(f"加载模块 {full_module} 失败: {e}")

    save_snapshot()
    print(f"已加载 {len(METHOD_REGISTRY)} 个方法")

def is_dev_mode():
    import sys
    return not getattr(sys, "frozen", False)
