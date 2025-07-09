# methods/read_file.py
import re
import json
import os

def read_file(file_name: str) -> str:
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"❌ 读取失败：{e}"


def read_files(file_names: list[str]) -> dict:
    result = {}
    for file_name in file_names:
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                result[file_name] = f.read()
        except Exception as e:
            result[file_name] = f"❌ 读取失败：{e}"
    return result
def read_folder(folder_path: str) -> dict:
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

def find_imported_files(file_content: str) -> list:
    pattern = r"from\s+(\S+)\s+import|import\s+(\S+)"
    matches = re.findall(pattern, file_content)
    modules = set()

    for m in matches:
        module = m[0] or m[1]
        # 简单处理本地模块（假设模块和文件名一致）
        if "." not in module:  # 排除标准库或 pip 包
            modules.add(module.strip())

    return [f"{m}.py" for m in modules]

def read_related_files(base_file: str) -> dict:
    try:
        with open(base_file, "r", encoding="utf-8") as f:
            content = f.read()
        related = find_imported_files(content)
        return read_files(related)
    except Exception as e:
        return {base_file: f"❌ 分析失败：{e}"}
    

def list_files(directory: str) -> list[str]:
    try:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except Exception as e:
        return [f"❌ 读取失败：{e}"]
