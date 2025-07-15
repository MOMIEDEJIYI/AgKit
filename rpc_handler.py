import json
from utils import utils
from tools.rpc_registry import METHOD_REGISTRY  # 导入注册表

def handle_rpc_request(raw_text: str) -> dict | None:
    # print("RPC 请求文本:", raw_text)
    try:
        json_str = utils.extract_json_from_text(raw_text)
        request = json.loads(json_str)

        # JSON-RPC 基本字段校验
        if request.get("jsonrpc") != "2.0" or "method" not in request:
            raise ValueError("无效的 JSON-RPC 请求")

        method = request["method"]
        params = request.get("params", {})
        request_id = request.get("id", None)

        handler = METHOD_REGISTRY.get(method)
        if not handler:
            if request_id is None:
                return None  # 是通知就不响应
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"未知方法: {method}"},
                "id": request_id
            }

        # 调用方法（支持 params 为 dict 或 list）
        if isinstance(params, dict):
            result = handler(params)
        elif isinstance(params, list):
            result = handler(*params)
        else:
            result = handler(params)

        # 你在这里给结果加一个状态字段，标示任务完成
        if isinstance(result, dict):
            # 你可以根据具体逻辑设置done，比如只读文件时表示已经完成
            result["done"] = True
        else:
            # 如果是字符串或其他类型，可以包裹成dict
            result = {"content": result, "done": True}

        # 是通知，不返回响应
        if request_id is None:
            return None

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
