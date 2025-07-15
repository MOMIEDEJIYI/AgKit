import os
from tools.rpc_registry import register_method

@register_method("create_file")
def create_file(params: dict) -> dict:
    file_name = params.get("file_name", "")
    content = params.get("content", "")
    extension = params.get("extension", "txt")

    name, ext_in_name = os.path.splitext(file_name)
    if not ext_in_name:
        file_name = f"{file_name}.{extension}"

    try:
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(content)
        return {"content": f"✅ 已创建文件：{file_name}", "done": True}
    except Exception as e:
        return {"content": f"❌ 创建失败：{e}", "done": True}

@register_method("create_files")
def create_files(params: dict) -> dict:
    file_names = params.get("file_names", [])
    contents = params.get("contents", [])
    extensions = params.get("extensions", [])

    if not extensions or len(extensions) < len(file_names):
        extensions = ["txt"] * len(file_names)

    messages = []
    for i, file_name in enumerate(file_names):
        content = contents[i] if i < len(contents) else ""
        ext = extensions[i] if i < len(extensions) else "txt"
        msg = create_file({"file_name": file_name, "content": content, "extension": ext})
        messages.append(msg["content"])  # 取出字符串部分拼接

    return {"content": "\n".join(messages), "done": True}