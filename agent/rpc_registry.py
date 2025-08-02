import os
import json
import importlib
import sys
import inspect

METHOD_REGISTRY = {}
METHOD_META = {}      # 方法元信息：描述、参数、enabled、package
PACKAGE_FLAGS = {}    # 包级开关：{"pkg": {"enabled": True/False}}

if getattr(sys, "frozen", False):
    # 打包模式：获取 exe 所在目录
    base_dir = os.path.dirname(sys.executable)
else:
    # 开发模式：当前文件路径
     base_dir = os.path.dirname(os.path.dirname(__file__))

# 插件目录和快照路径
PLUGINS_DIR = os.path.join(base_dir, "plugins")
SNAPSHOT_PATH = os.path.join(base_dir, "runtime", "method_registry_snapshot.json")

# 插入 sys.path 以便 import plugins.xxx
if PLUGINS_DIR not in sys.path:
    sys.path.insert(0, PLUGINS_DIR)
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)


def register_method(name, param_desc=None, description=None, enabled=True, **flags):
    def decorator(func):
        package = name.split(".")[0]

        # 默认值来自参数
        enabled_flag = enabled

        # 如果快照里已经存在这个方法，就用快照里的 enabled 覆盖
        if name in METHOD_META:
            enabled_flag = METHOD_META[name].get("enabled", enabled_flag)

        METHOD_REGISTRY[name] = func
        METHOD_META[name] = {
            "package": package,
            "description": description or "",
            "params": param_desc or {},
            "enabled": enabled_flag,
            **flags
        }

        if package not in PACKAGE_FLAGS:
            PACKAGE_FLAGS[package] = {"enabled": True}

        return func
    return decorator


def save_snapshot():
    os.makedirs(os.path.dirname(SNAPSHOT_PATH), exist_ok=True)

    missing_desc = []
    for name, meta in METHOD_META.items():
        if not meta.get("description", "").strip():
            missing_desc.append(name)

    if missing_desc:
        print("以下方法缺少描述（description）不利于模型理解，请为每个方法添加描述后重试：")
        for name in missing_desc:
            func = METHOD_REGISTRY[name]
            print(f" - {name}: {func.__module__}.{func.__name__}")
        sys.exit(1)

    snapshot = {
        "packages": PACKAGE_FLAGS,
        "methods": METHOD_META
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
    global METHOD_META, PACKAGE_FLAGS
    if not os.path.exists(SNAPSHOT_PATH):
        raise FileNotFoundError(f"快照文件不存在：{SNAPSHOT_PATH}")
    with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
        snapshot = json.load(f)

    METHOD_META.clear()
    PACKAGE_FLAGS.clear()

    # 从快照加载
    packages = snapshot.get("packages", {})
    methods = snapshot.get("methods", {})

    PACKAGE_FLAGS.update(packages)
    METHOD_META.update(methods)

    print(f"从快照加载了 {len(METHOD_META)} 个方法")


def init_registry():
    if not os.path.isdir(PLUGINS_DIR):
        print(f"插件目录不存在，跳过扫描: {PLUGINS_DIR}")
        return

    snapshot_loaded = False
    if os.path.exists(SNAPSHOT_PATH):
        try:
            load_snapshot()
            snapshot_loaded = True
        except Exception as e:
            print(f"加载快照失败，使用默认启用: {e}")

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

    # 如果第一次运行（没加载过快照），需要保存一份初始快照
    if not snapshot_loaded:
        save_snapshot()

    print(f"已加载 {len(METHOD_REGISTRY)} 个方法")


def is_dev_mode():
    return not getattr(sys, "frozen", False)


# ==== 开关控制 API ====
from utils.event_bus import event_bus
def disable_method(method_name):
    if method_name in METHOD_META:
        METHOD_META[method_name]["enabled"] = False
        save_snapshot()
        event_bus.publish("methods_updated", source="registry", method=method_name, enabled=False)

def enable_method(method_name):
    if method_name in METHOD_META:
        METHOD_META[method_name]["enabled"] = True
        save_snapshot()
        event_bus.publish("methods_updated", source="registry", method=method_name, enabled=True)

def disable_package(package_name):
    PACKAGE_FLAGS[package_name] = {"enabled": False}
    for m, meta in METHOD_META.items():
        if meta["package"] == package_name:
            meta["enabled"] = False
    save_snapshot()
    event_bus.publish("methods_updated", source="registry", package=package_name, enabled=False)

def enable_package(package_name):
    PACKAGE_FLAGS[package_name] = {"enabled": True}
    for m, meta in METHOD_META.items():
        if meta["package"] == package_name:
            meta["enabled"] = True
    save_snapshot()
    event_bus.publish("methods_updated", source="registry", package=package_name, enabled=True)
