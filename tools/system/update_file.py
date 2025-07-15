import os
from tools.rpc_registry import register_method
from tools.system.create_file import create_file

@register_method("update_file")
def file_update(params: dict) -> dict:
    file_name = params.get("file_name", "")
    content = params.get("content", "")
    # 复用 create_file 的覆盖写入功能
    return create_file({"file_name": file_name, "content": content})
