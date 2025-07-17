import json
from rpc_handler import handle_rpc_request
from rpc_registry import METHOD_FLAGS
from utils import utils
import logging

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self, agent):
        self.agent = agent

    def _run_task_common(self, history, ask_func, first_response=None, check_cancel=lambda: False):
        current_history = history[:]
        response = first_response or ask_func(current_history, check_cancel=check_cancel)
        print("_run_task_common response: %s", response)

        # 针对流式接口，可能返回 dict 取消标记，先判断
        if isinstance(response, dict) and response.get("cancelled"):
            print("接收到中断标志，结束任务")
            return "取消操作。"

        for _ in range(5):
            if check_cancel():
                print("操作取消，结束任务")
                return "操作取消"

            try:
                json_str = utils.extract_json_from_text(response)
                parsed = json.loads(json_str)
                rpc_obj = parsed.get("jsonrpc") if isinstance(parsed, dict) else None

                if isinstance(rpc_obj, dict) and ("result" in rpc_obj or "error" in rpc_obj):
                    print("ℹ️ 收到 JSON-RPC 响应，进入对话阶段")
                    break

                if isinstance(rpc_obj, dict) and "method" in rpc_obj:
                    method_name = rpc_obj.get("method")
                    print("✅ 收到 JSON-RPC 请求")
                    print("⚙️ 执行 JSON-RPC 请求: %s", rpc_obj)
                    rpc_response = handle_rpc_request(json.dumps(rpc_obj))

                    direct_response = METHOD_FLAGS.get(method_name, {}).get("direct_response", False)
                    if direct_response:
                        print(f"🔔 方法 {method_name} 标记为 direct_response，直接返回结果：{rpc_response}")
                        return rpc_response.get("result") or {}

                    if rpc_response is None:
                        print("ℹ️ 请求是通知类型，无需响应")
                        break

                    if rpc_response.get("error") and "未知方法" in rpc_response["error"]["message"]:
                        print("❗未知方法，尝试引导模型使用合法方法")
                        response = ask_func(current_history, known_methods=self.agent.available_methods, check_cancel=check_cancel)
                        continue

                    current_history += [
                        {"role": "assistant", "content": json.dumps(response, ensure_ascii=False)},
                        {"role": "system", "content": f"RPC调用结果：{json.dumps(rpc_response, ensure_ascii=False)}"}
                    ]
                    response = ask_func(current_history, check_cancel=check_cancel)

                    if rpc_response.get("result", {}).get("done") is True:
                        break

                    continue

                logger.warning("⚠️ 无法识别为有效的 JSON-RPC 请求或响应，跳出")
                break

            except Exception as e:
                logger.error("❌ 出现异常: %s", str(e))
                return f"❌ 出现异常：{str(e)}"

        return response

    def run_task_sync(self, history, first_response=None, check_cancel=lambda: False):
        return self._run_task_common(history, self.agent.ask, first_response, check_cancel)

    def run_task_stream(self, history, first_response=None, check_cancel=lambda: False):
        return self._run_task_common(history, self.agent.ask_stream, first_response, check_cancel)
