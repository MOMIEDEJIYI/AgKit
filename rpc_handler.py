import re
import json
from tools.create_file import create_file, create_files
from tools.read_file import read_file, read_files, read_folder, read_related_files, find_imported_files, list_files
from tools.delete_file import delete_file, delete_files
from tools.execute_command import execute_command
from utils import utils

def handle_rpc_request(raw_text: str) -> dict:
    print("RPC 请求文本:", raw_text)
    try:
        json_str = utils.extract_json_from_text(raw_text)
        request = json.loads(json_str)
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id", None)

        if method == "create_file":
            file_name = params.get("file_name")
            content = params.get("content", "")
            result = create_file(file_name, content)

        elif method == "create_files":
            file_names = params.get("file_names", [])
            contents = params.get("contents", [])
            extensions = params.get("extensions", [])
            result = create_files(file_names, contents, extensions)

        elif method == "read_file":
            file_name = params.get("file_name")
            result = read_file(file_name)

        elif method == "update_file":
            file_name = params.get("file_name")
            content = params.get("content", "")
            result = create_file(file_name, content)  # 复用 create_file 实现覆盖

        elif method == "update_files":
            file_names = params.get("file_names", [])
            contents = params.get("contents", [])
            extensions = params.get("extensions", [])
            result = create_files(file_names, contents, extensions)

        elif method == "delete_file":
            file_name = params.get("file_name")
            result = delete_file(file_name)

        elif method == "delete_files":
            file_names = params.get("file_names", [])
            result = delete_files(file_names)
        elif method == "execute_command":
            command = params.get("command", "")
            result = execute_command(command)
        elif method == "read_folder":
            folder_path = params.get("folder_path", "")
            result = read_folder(folder_path)
        elif method == "read_related_files":
            base_file = params.get("base_file", "")
            result = read_related_files(base_file)
        elif method == "read_files":
            file_names = params.get("file_names", [])
            result = read_files(file_names)
        elif method == "find_imported_files":
            file_content = params.get("file_content", "")
            result = find_imported_files(file_content)
        else:
            result = f"未知方法: {method}"

        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": str(e)},
            "id": None
        }
