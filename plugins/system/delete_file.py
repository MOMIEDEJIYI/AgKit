import os
from rpc_registry import register_method
from agent.models.rpc_base import RpcResultBase
from common.error_codes import ErrorCode

@register_method("system.delete_file", param_desc={"file_name": "文件名"})
def delete_file(params: dict) -> dict:
    file_name = params.get("file_name", "").strip()
    if not file_name:
        return RpcResultBase(
            "缺少文件名",
            success=False,
            code=ErrorCode.MISSING_PARAM["code"]
        ).to_dict()
    try:
        if not os.path.exists(file_name):
            return RpcResultBase(
                f"文件不存在: {file_name}",
                success=False,
                code=ErrorCode.UNKNOWN_ERROR["code"]
            ).to_dict()
        os.remove(file_name)
        return RpcResultBase(f"文件已删除: {file_name}").to_dict()
    except Exception as e:
        return RpcResultBase(
            f"删除失败：{e}",
            success=False,
            code=ErrorCode.UNKNOWN_ERROR["code"]
        ).to_dict()

@register_method("system.delete_files", param_desc={"file_names": "文件名列表"})
def delete_files(params: dict) -> dict:
    file_names = params.get("file_names", [])
    if not isinstance(file_names, list) or not file_names:
        return RpcResultBase(
            "缺少文件名列表",
            success=False,
            code=ErrorCode.MISSING_PARAM["code"]
        ).to_dict()
    messages = []
    success = True
    for file_name in file_names:
        try:
            if not os.path.exists(file_name):
                messages.append(f"文件不存在: {file_name}")
                success = False
                continue
            os.remove(file_name)
            messages.append(f"文件已删除: {file_name}")
        except Exception as e:
            messages.append(f"删除失败: {file_name}，原因：{e}")
            success = False
    return RpcResultBase("\n".join(messages), success=success).to_dict()
