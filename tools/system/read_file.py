import os
import re
from tools.rpc_registry import register_method

@register_method("read_file")
def read_file(params: dict) -> str:
    file_name = params.get("file_name", "")
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"❌ 读取失败：{e}"

@register_method("read_files")
def read_files(params: dict) -> dict:
    file_names = params.get("file_names", [])
    result = {}
    for file_name in file_names:
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                result[file_name] = f.read()
        except Exception as e:
            result[file_name] = f"❌ 读取失败：{e}"
    return result

@register_method("read_folder")
def read_folder(params: dict) -> dict:
    folder_path = params.get("folder_path", "")
    result = {}
    if not os.path.isdir(folder_path):
        return {"error": f"❌ 路径不存在或不是文件夹：{folder_path}"}
    
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    result[file_name] = f.read()
            except Exception as e:
                result[file_name] = f"❌ 读取失败：{e}"
    return result

@register_method("find_imported_files")
def find_imported_files(params: dict) -> list:
    file_content = params.get("file_content", "")
    pattern = r"from\s+(\S+)\s+import|import\s+(\S+)"
    matches = re.findall(pattern, file_content)
    modules = set()
    for m in matches:
        module = m[0] or m[1]
        if "." not in module:
            modules.add(module.strip())
    return [f"{m}.py" for m in modules]

@register_method("read_related_files")
def read_related_files(params: dict) -> dict:
    base_file = params.get("base_file", "")
    try:
        with open(base_file, "r", encoding="utf-8") as f:
            content = f.read()
        related = find_imported_files({"file_content": content})
        return read_files({"file_names": related})
    except Exception as e:
        return {base_file: f"❌ 分析失败：{e}"}

@register_method("list_files")
def list_files(params: dict) -> list:
    directory = params.get("directory", "")
    try:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except Exception as e:
        return [f"❌ 读取失败：{e}"]
