import json
from utils import utils
from rpc_registry import METHOD_REGISTRY, METHOD_FLAGS
from agent.models.rpc_base import RpcResponse

def handle_rpc_request(raw_text: str) -> dict | None:
    try:
        json_str = utils.extract_json_from_text(raw_text)
        parsed = json.loads(json_str)

        # 解析 JSON-RPC 请求体
        request = parsed["jsonrpc"] if "jsonrpc" in parsed and isinstance(parsed["jsonrpc"], dict) else parsed

        if "method" not in request:
            return None  # 说明不是个请求（可能是响应）

        if request.get("jsonrpc") != "2.0":
            raise ValueError("无效的 JSON-RPC 请求")

        method = request["method"]
        params = request.get("params", {})
        request_id = request.get("id", None)

        handler = METHOD_REGISTRY.get(method)
        if not handler:
            return RpcResponse(
                error={"code": -32601, "message": f"未知方法: {method}"},
                id=request_id
            ).to_dict()

        # 方法调用
        if isinstance(params, dict):
            result = handler(params)
        elif isinstance(params, list):
            result = handler(*params)
        else:
            result = handler(params)

        # 判断 tool_result_wrap，控制字段检查
        tool_result_wrap = METHOD_FLAGS.get(method, {}).get("tool_result_wrap", False)

        if not tool_result_wrap:
            if not isinstance(result, dict):
                raise ValueError(f"工具函数返回值必须是 dict，当前类型: {type(result)}")
            if "content" not in result or "done" not in result:
                raise ValueError("工具函数返回的结果必须包含 'content' 和 'done' 字段")

        # 如果是通知类（无 id），则不返回响应
        if request_id is None:
            return None

        return RpcResponse(result=result, id=request_id).to_dict()

    except Exception as e:
        return RpcResponse(
            error={"code": -32000, "message": str(e)},
            id=request.get("id", None) if 'request' in locals() else None
        ).to_dict()
