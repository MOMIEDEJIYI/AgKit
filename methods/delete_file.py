import os

def delete_file(file_name: str) -> str:
    try:
        if os.path.exists(file_name):
            os.remove(file_name)
            return f"✅ 已删除文件：{file_name}"
        else:
            return f"❌ 文件不存在：{file_name}"
    except Exception as e:
        return f"❌ 删除失败：{e}"

def delete_files(file_names: list[str]) -> str:
    messages = []
    for file_name in file_names:
        msg = delete_file(file_name)
        messages.append(msg)
    return "\n".join(messages)