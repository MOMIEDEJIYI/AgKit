# methods/create_file.py
import os

def create_file(file_name: str, content: str = "", extension: str = "txt") -> str:
    """
    创建一个文件，默认添加扩展名，如果未提供。
    """
    name, ext_in_name = os.path.splitext(file_name)
    if not ext_in_name:
        file_name = f"{file_name}.{extension}"

    try:
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ 已创建文件：{file_name}"
    except Exception as e:
        return f"❌ 创建失败：{e}"


def create_files(file_names: list[str], contents: list[str], extensions: list[str] = None) -> str:
    """
    批量创建多个文件，支持单独指定扩展名。
    """
    if not extensions:
        extensions = ["txt"] * len(file_names)

    messages = []

    for i, file_name in enumerate(file_names):
        content = contents[i] if i < len(contents) else ""
        ext = extensions[i] if i < len(extensions) else "txt"
        msg = create_file(file_name, content, ext)
        messages.append(msg)

    return "\n".join(messages)