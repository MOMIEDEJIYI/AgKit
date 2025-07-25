import os
import re
from rpc_registry import register_method
from agent.models.rpc_base import RpcResultBase

@register_method(
    name="system.read_file",
    param_desc={"file_name": "文件名", "extension": "文件扩展名"},
    description="读取文件",
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
        return RpcResultBase(f"❌ 读取失败：{e}", success=False, code=1001).to_dict()

@register_method(
    name="system.read_files",
    param_desc={"file_names": "文件名列表"},
    description="读取多个文件",
)
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

@register_method(
    name="system.read_folder",
    param_desc={"folder_path": "文件夹路径"},
    description="读取文件夹",
)
def read_folder(params: dict) -> dict:
    folder_path = params.get("folder_path", "")
    result = {}
    if not os.path.isdir(folder_path):
        return RpcResultBase(f"❌ 路径不存在或不是文件夹：{folder_path}", success=False, code=1002).to_dict()
    
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

@register_method(
    name="system.list_files",
    param_desc={"directory": "文件夹路径"},
    description="列出文件夹下的文件",
)
def list_files(params: dict) -> dict:
    directory = params.get("directory", "")
    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        return RpcResultBase(files).to_dict()
    except Exception as e:
        return RpcResultBase([f"❌ 读取失败：{e}"], success=False, code=1004).to_dict()
