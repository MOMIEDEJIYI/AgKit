import os
from rpc_registry import register_method
from plugins.system.create_file import create_file

@register_method(
    name="system.update_file",
    param_desc={
        "file_name": "文件名",
        "content": "文件内容"
    },
    description="更新文件",
)
def file_update(params: dict) -> dict:
    file_name = params.get("file_name", "")
    content = params.get("content", "")
    # 复用 create_file 的覆盖写入功能
    return create_file({"file_name": file_name, "content": content})
