import json
from utils import utils
from tools.rpc_registry import METHOD_REGISTRY  # 导入注册表

def handle_rpc_request(raw_text: str) -> dict | None:
    try:
        json_str = utils.extract_json_from_text(raw_text)
        parsed = json.loads(json_str)

        # 提取 jsonrpc 内容
        request = parsed["jsonrpc"] if "jsonrpc" in parsed and isinstance(parsed["jsonrpc"], dict) else parsed

        # ✅ 忽略响应结构
        if "method" not in request:
            return None

        if request.get("jsonrpc") != "2.0":
            raise ValueError("无效的 JSON-RPC 请求")

        method = request["method"]
        params = request.get("params", {})
        request_id = request.get("id", None)

        from tools.rpc_registry import METHOD_REGISTRY
        handler = METHOD_REGISTRY.get(method)
        if not handler:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"未知方法: {method}"},
                "id": request_id
            }

        # 执行方法
        if isinstance(params, dict):
            result = handler(params)
        elif isinstance(params, list):
            result = handler(*params)
        else:
            result = handler(params)

        # 校验结果
        if not isinstance(result, dict):
            raise ValueError(f"工具函数返回值必须是 dict，当前类型: {type(result)}")
        if "content" not in result or "done" not in result:
            raise ValueError("工具函数返回的结果必须包含 'content' 和 'done' 字段")

        if request_id is None:
            return None  # 通知类调用，无返回

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
