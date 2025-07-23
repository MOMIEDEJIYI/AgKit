import json
from utils import utils
from rpc_registry import METHOD_REGISTRY, METHOD_FLAGS
from agent.models.rpc_base import RpcResponse
from common.error_codes import ErrorCode

def handle_rpc_request(raw_text: str) -> dict | None:
    try:
        json_str = utils.extract_json_from_text(raw_text)
        parsed = json.loads(json_str)

        # 解析 JSON-RPC 请求体
        request = parsed["jsonrpc"] if isinstance(parsed.get("jsonrpc"), dict) else parsed

        if "method" not in request:
            return None  # 非请求（可能是响应）

        if request.get("jsonrpc") != "2.0":
            raise ValueError("无效的 JSON-RPC 请求")

        method = request["method"]
        params = request.get("params", {})
        request_id = request.get("id")

        handler = METHOD_REGISTRY.get(method)
        if not handler:
            return RpcResponse(
                error={
                    "code": ErrorCode.UNKNOWN_METHOD["code"],
                    "message": f"{ErrorCode.UNKNOWN_METHOD['message']}: {method}"
                },
                id=request_id
            ).to_dict()

        # ==== 参数校验 ====
        param_desc = getattr(handler, "_rpc_param_desc", {})
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

        # ==== 执行方法 ====
        if isinstance(params, dict):
            result = handler(params)
        elif isinstance(params, list):
            result = handler(*params)
        else:
            result = handler(params)

        # ==== 返回结构检查 ====
        tool_result_wrap = METHOD_FLAGS.get(method, {}).get("tool_result_wrap", False)

        if not tool_result_wrap:
            if not isinstance(result, dict):
                raise ValueError(f"工具函数返回值必须是 dict，当前类型: {type(result)}")
            if "content" not in result or "done" not in result:
                raise ValueError("工具函数返回的结果必须包含 'content' 和 'done' 字段")

            # 工具返回失败
            if not result.get("success", True):
                return RpcResponse(
                    error={
                        "code": result.get("code", ErrorCode.UNKNOWN_ERROR["code"]),
                        "message": result.get("content", ErrorCode.UNKNOWN_ERROR["message"])
                    },
                    id=request_id
                ).to_dict()

        if request_id is None:
            return None  # Notification 请求无响应

        return RpcResponse(result=result, id=request_id).to_dict()

    except Exception as e:
        return RpcResponse(
            error={
                "code": ErrorCode.UNKNOWN_ERROR["code"],
                "message": str(e)
            },
            id=request.get("id", None) if 'request' in locals() else None
        ).to_dict()