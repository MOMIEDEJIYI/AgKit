import os
from tools.rpc_registry import register_method

@register_method("delete_file")
def delete_file(params: dict) -> dict:
    file_name = params.get("file_name", "")
    try:
        if os.path.exists(file_name):
            os.remove(file_name)
            return {"content": f"✅ 已删除文件：{file_name}", "done": True}
        else:
            return f"❌ 文件不存在：{file_name}"
    except Exception as e:
        return {"content": f"❌ 删除失败：{e}", "done": True}

@register_method("delete_files")
def delete_files(params: dict) -> dict:
    file_names = params.get("file_names", [])
    messages = []
    for file_name in file_names:
        msg = delete_file({"file_name": file_name})
        messages.append(msg)
    return {"content": "\n".join(messages), "done": True}
