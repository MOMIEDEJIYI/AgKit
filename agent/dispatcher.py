# agent/dispatcher.py

import json
from typing import Any, Dict, Callable


class Dispatcher:
    def __init__(self):
        from tools import create_file, delete_file, read_file, execute_command

        self.tools: Dict[str, Callable[[Dict[str, Any]], Any]] = {
            "create_file": create_file.run,
            "delete_file": delete_file.run,
            "read_file": read_file.run,
            "execute_command": execute_command.run,
        }

    def dispatch(self, rpc_json: str) -> Any:
        """
        接收 LLM 返回的 JSON-RPC 格式字符串，并执行对应工具
        """
        try:
            request = json.loads(rpc_json)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            if method not in self.tools:
                return self._error_response("Method not found", request_id)

            result = self.tools[method](params)
            return self._success_response(result, request_id)

        except json.JSONDecodeError:
            return self._error_response("Invalid JSON format", None)
        except Exception as e:
            return self._error_response(str(e), None)

    def _success_response(self, result: Any, request_id: int) -> dict:
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }

    def _error_response(self, message: str, request_id: int) -> dict:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32600,
                "message": message
            },
            "id": request_id
        }
