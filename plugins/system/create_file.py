import os
from rpc_registry import register_method
from agent.models.rpc_base import RpcResultBase
from plugins.system.error_codes import ErrorCode

@register_method("system.create_file", param_desc={"file_name": "文件名", "content": "文件内容", "extension": "文件扩展名"})
def create_file(params: dict) -> dict:
    file_name = params.get("file_name") or params.get("filename", "")
    content = params.get("content", "")
    extension = params.get("extension", "txt")

    if not file_name:
        return RpcResultBase("❌ 缺少文件名", success=False, code=ErrorCode.FILE_READ_ERROR["code"]).to_dict()

    # 拼接文件名带扩展
    if not file_name.endswith(f".{extension}"):
        file_name = f"{file_name}.{extension}"
    try:
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(content)
        return RpcResultBase(f"✅ 已创建文件：{file_name}").to_dict()
    except Exception as e:
        return RpcResultBase(f"❌ 创建失败：{e}", success=False, code=ErrorCode.FILE_CREATION_FAILED["code"]).to_dict()


@register_method("system.create_files", param_desc={"file_names": "文件名列表", "contents": "文件内容列表", "extensions": "文件扩展名列表"})
def create_files(params: dict) -> dict:
    file_names = params.get("file_names", [])
    contents = params.get("contents", [])
    extensions = params.get("extensions", [])

    if not extensions or len(extensions) < len(file_names):
        extensions = ["txt"] * len(file_names)

    messages = []
    all_success = True

    for i, file_name in enumerate(file_names):
        content = contents[i] if i < len(contents) else ""
        ext = extensions[i] if i < len(extensions) else "txt"
        result = create_file({"file_name": file_name, "content": content, "extension": ext})

        messages.append(result["content"])
        if not result.get("success", True):
            all_success = False

    return RpcResultBase(
        content="\n".join(messages),
        success=all_success
    ).to_dict()
