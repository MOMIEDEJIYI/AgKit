import json
from utils import utils
from rpc_registry import METHOD_REGISTRY, METHOD_FLAGS

def handle_rpc_request(raw_text: str) -> dict | None:
    try:
        json_str = utils.extract_json_from_text(raw_text)
        parsed = json.loads(json_str)

        # 检查是否是 JSON-RPC 请求
        request = parsed["jsonrpc"] if "jsonrpc" in parsed and isinstance(parsed["jsonrpc"], dict) else parsed

        # 判断是请求还是响应
        if "method" not in request:
            return None

        if request.get("jsonrpc") != "2.0":
            raise ValueError("无效的 JSON-RPC 请求")

        method = request["method"]
        params = request.get("params", {})
        request_id = request.get("id", None)

        handler = METHOD_REGISTRY.get(method)
        if not handler:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"未知方法: {method}"},
                "id": request_id
            }

        # 调用方法
        if isinstance(params, dict):
            result = handler(params)
        elif isinstance(params, list):
            result = handler(*params)
        else:
            result = handler(params)
        
        # 判断是否是 direct_response 方法，跳过格式校验
        direct_response = False
        if method in METHOD_FLAGS:
            direct_response = METHOD_FLAGS[method].get("direct_response", False)

        if not direct_response:
            # 非 direct_response 方法，必须是 dict 且包含特定字段
            if not isinstance(result, dict):
                raise ValueError(f"工具函数返回值必须是 dict，当前类型: {type(result)}")
            if "content" not in result or "done" not in result:
                raise ValueError("工具函数返回的结果必须包含 'content' 和 'done' 字段")

        if request_id is None:
            return None  # 通知不返回响应

        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": str(e)},
            "id": request.get("id", None) if 'request' in locals() else None
        }
