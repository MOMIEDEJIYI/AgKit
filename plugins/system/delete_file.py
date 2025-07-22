import os
import re
from rpc_registry import register_method
from agent.models.rpc_base import RpcResultBase
from plugins.system.error_codes import ErrorCode

@register_method(
    name="system.read_file",
    param_desc={"file_name": "文件名", "extension": "文件扩展名"}, 
    needs_nlg=True,
)
def read_file(params: dict) -> dict:
    file_name = params.get("file_name", "")
    extension = params.get("extension", "")
    full_file_name = f"{file_name}.{extension}" if extension else file_name
    try:
        with open(full_file_name, "r", encoding="utf-8") as f:
            return RpcResultBase(f.read()).to_dict()
    except Exception as e:
        return RpcResultBase(f"❌ 读取失败：{e}", success=False, code=ErrorCode.FILE_READ_ERROR["code"]).to_dict()

@register_method("system.read_files", param_desc={"file_names": "文件名列表"})
def read_files(params: dict) -> dict:
    file_names = params.get("file_names", [])
    result = {}
    success = True
    for file_name in file_names:
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                result[file_name] = f.read()
        except Exception as e:
            result[file_name] = f"❌ 读取失败：{e}"
            success = False
    return RpcResultBase(result, success=success).to_dict()

@register_method("system.read_folder", param_desc={"folder_path": "文件夹路径"})
def read_folder(params: dict) -> dict:
    folder_path = params.get("folder_path", "")
    result = {}
    if not os.path.isdir(folder_path):
        return RpcResultBase(f"❌ 路径不存在或不是文件夹：{folder_path}", success=False, code=ErrorCode.FILE_READ_ERROR["code"]).to_dict()
    
    success = True
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    result[file_name] = f.read()
            except Exception as e:
                result[file_name] = f"❌ 读取失败：{e}"
                success = False
    return RpcResultBase(result, success=success).to_dict()

@register_method("system.find_imported_files", param_desc={"file_content": "文件内容"})
def find_imported_files(params: dict) -> dict:
    file_content = params.get("file_content", "")
    pattern = r"from\s+(\S+)\s+import|import\s+(\S+)"
    matches = re.findall(pattern, file_content)
    modules = set()
    for m in matches:
        module = m[0] or m[1]
        if "." not in module:
            modules.add(module.strip())
    return RpcResultBase([f"{m}.py" for m in modules]).to_dict()

@register_method("system.read_related_files", param_desc={"base_file": "基础文件"})
def read_related_files(params: dict) -> dict:
    base_file = params.get("base_file", "")
    try:
        with open(base_file, "r", encoding="utf-8") as f:
            content = f.read()
        related = find_imported_files({"file_content": content})
        return read_files({"file_names": related.get("content", [])})
    except Exception as e:
        return RpcResultBase({base_file: f"❌ 分析失败：{e}"}, success=False, code=ErrorCode.FILE_DEPENDENCY_ANALYS_IS_ERROR["code"]).to_dict()

@register_method("system.list_files", param_desc={"directory": "文件夹路径"})
def list_files(params: dict) -> dict:
    directory = params.get("directory", "")
    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        return RpcResultBase(files).to_dict()
    except Exception as e:
        return RpcResultBase([f"❌ 读取失败：{e}"], success=False, code=ErrorCode.FILE_READ_ERROR["code"]).to_dict()
