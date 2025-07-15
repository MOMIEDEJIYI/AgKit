import json
from utils import utils
from tools.rpc_registry import METHOD_REGISTRY  # 导入注册表

def handle_rpc_request(raw_text: str) -> dict | None:
    try:
        json_str = utils.extract_json_from_text(raw_text)
        request = json.loads(json_str)

        if request.get("jsonrpc") != "2.0" or "method" not in request:
            raise ValueError("无效的 JSON-RPC 请求")

        method = request["method"]
        params = request.get("params", {})
        request_id = request.get("id", None)

        handler = METHOD_REGISTRY.get(method)
        if not handler:
            if request_id is None:
                return None
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"未知方法: {method}"},
                "id": request_id
            }

        # 调用工具函数
        if isinstance(params, dict):
            result = handler(params)
        elif isinstance(params, list):
            result = handler(*params)
        else:
            result = handler(params)

        # 强制校验返回值必须是 dict，且包含 content 和 done
        if not isinstance(result, dict):
            raise ValueError(f"工具函数返回值必须是 dict，当前类型: {type(result)}")
        if "content" not in result or "done" not in result:
            raise ValueError("工具函数返回的结果必须包含 'content' 和 'done' 字段")

        if request_id is None:
            return None  # 通知类型不返回响应

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
