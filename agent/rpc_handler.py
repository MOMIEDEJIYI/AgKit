import json
from utils import utils
from agent.models.rpc_base import RpcResponse
from common.error_codes import ErrorCode
from agent.rpc_registry import METHOD_REGISTRY, METHOD_META, PACKAGE_FLAGS

def handle_rpc_request(raw_text: str) -> dict | None:
    try:
        json_str = utils.extract_json_from_text(raw_text)
        parsed = json.loads(json_str)

        request = parsed["jsonrpc"] if isinstance(parsed.get("jsonrpc"), dict) else parsed

        if "method" not in request:
            return None

        if request.get("jsonrpc") != "2.0":
            raise ValueError("无效的 JSON-RPC 请求")

        method = request["method"]
        params = request.get("params", {})
        request_id = request.get("id")

        handler = METHOD_REGISTRY.get(method)
        meta = METHOD_META.get(method)
        if not handler or not meta:
            return RpcResponse(
                error={
                    "code": ErrorCode.UNKNOWN_METHOD["code"],
                    "message": f"{ErrorCode.UNKNOWN_METHOD['message']}: {method}"
                },
                id=request_id
            ).to_dict()

        # 判断包和方法是否启用
        package = meta.get("package")
        pkg_enabled = PACKAGE_FLAGS.get(package, {}).get("enabled", True)
        if not pkg_enabled or not meta.get("enabled", True):
            return RpcResponse(
                error={
                    "code": ErrorCode.UNKNOWN_METHOD["code"],
                    "message": f"方法被禁用: {method}"
                },
                id=request_id
            ).to_dict()

        param_desc = meta.get("params", {})
        missing_params = [
            key for key in param_desc
            if key not in params or params[key] in [None, "", []]
        ]
        if missing_params:
            return RpcResponse(
                error={
                    "code": ErrorCode.MISSING_PARAM["code"],
                    "message": f"{ErrorCode.MISSING_PARAM['message']}: {', '.join(missing_params)}。请根据 param_desc 向用户提问。",
                    "missing_params": missing_params,
                    "param_desc": {k: param_desc[k] for k in missing_params}
                },
                id=request_id
            ).to_dict()

        if isinstance(params, dict):
            result = handler(params)
        elif isinstance(params, list):
            result = handler(*params)
        else:
            result = handler(params)

        tool_result_wrap = meta.get("tool_result_wrap", False)
        if not tool_result_wrap:
            if not isinstance(result, dict):
                raise ValueError(f"工具函数返回值必须是 dict，当前类型: {type(result)}")
            if "content" not in result or "done" not in result:
                raise ValueError("工具函数返回的结果必须包含 'content' 和 'done' 字段")

            if not result.get("success", True):
                return RpcResponse(
                    error={
                        "code": result.get("code", ErrorCode.UNKNOWN_ERROR["code"]),
                        "message": result.get("content", ErrorCode.UNKNOWN_ERROR["message"])
                    },
                    id=request_id
                ).to_dict()

        if request_id is None:
            return None

        return RpcResponse(result=result, id=request_id).to_dict()

    except Exception as e:
        return RpcResponse(
            error={
                "code": ErrorCode.UNKNOWN_ERROR["code"],
                "message": str(e)
            },
            id=request.get("id", None) if 'request' in locals() else None
        ).to_dict()