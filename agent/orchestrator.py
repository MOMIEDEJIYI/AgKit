import json
from rpc_handler import handle_rpc_request
from utils import utils
from logging import logging

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self, agent):
        self.agent = agent

    def run_task_sync(self, history, first_response=None, check_cancel=lambda: False):
        current_history = history[:]
        response = first_response or self.agent.ask(current_history, check_cancel=check_cancel)
        logger.info("run_task_sync response", response)

        for _ in range(5):
            if check_cancel():
                print("操作取消，结束任务")
                return "操作取消"
            try:
                json_str = utils.extract_json_from_text(response)
                parsed = json.loads(json_str)
                rpc_obj = parsed.get("jsonrpc") if isinstance(parsed, dict) else None

                if isinstance(rpc_obj, dict) and ("result" in rpc_obj or "error" in rpc_obj):
                    logger.info("ℹ️ 收到 JSON-RPC 响应，进入对话阶段")
                    break

                if isinstance(rpc_obj, dict) and "method" in rpc_obj:
                    logger.info("✅ 收到 JSON-RPC 请求")
                    logger.info("⚙️ 执行 JSON-RPC 请求:", rpc_obj)
                    rpc_response = handle_rpc_request(json.dumps(rpc_obj))

                    if rpc_response is None:
                        logger.info("ℹ️ 请求是通知类型，无需响应")
                        break

                    if rpc_response.get("error") and "未知方法" in rpc_response["error"]["message"]:
                        logger.info("❗未知方法，尝试引导模型使用合法方法")
                        response = self.agent.ask(current_history, known_methods=self.agent.available_methods, check_cancel=check_cancel)
                        continue

                    current_history += [
                        {"role": "assistant", "content": response},
                        {"role": "system", "content": f"RPC调用结果：{json.dumps(rpc_response, ensure_ascii=False)}"}
                    ]
                    response = self.agent.ask(current_history, check_cancel=check_cancel)

                    if rpc_response.get("result", {}).get("done") is True:
                        break

                    continue

                logger.warning("⚠️ 无法识别为有效的 JSON-RPC 请求或响应，跳出")
                break

            except Exception as e:
                logger.error("❌ 出现异常:", str(e))
                return f"❌ 出现异常：{str(e)}"

        return response

    def run_task_stream(self, history, first_response=None, check_cancel=lambda: False):
        current_history = history[:]
        response = first_response or self.agent.ask_stream(current_history, check_cancel=check_cancel)
        print("run_task_stream response", response)

        if isinstance(response, dict) and response.get("cancelled"):
            logger.info("接收到中断标志，结束任务")
            return "取消操作。"

        for _ in range(5):
            if check_cancel():
                logger.info("操作取消，结束任务")
                return "操作取消"

            try:
                json_str = utils.extract_json_from_text(response)
                parsed = json.loads(json_str)
                rpc_obj = parsed.get("jsonrpc") if isinstance(parsed, dict) else None

                if isinstance(rpc_obj, dict) and ("result" in rpc_obj or "error" in rpc_obj):
                    logger.info("ℹ️ 收到 JSON-RPC 响应，进入对话阶段")
                    break

                if isinstance(rpc_obj, dict) and "method" in rpc_obj:
                    logger.info("✅ 收到 JSON-RPC 请求")
                    logger.info("⚙️ 执行 JSON-RPC 请求:", rpc_obj)
                    rpc_response = handle_rpc_request(json.dumps(rpc_obj))

                    if rpc_response is None:
                        logger.info("ℹ️ 请求是通知类型，无需响应")
                        break

                    if rpc_response.get("error") and "未知方法" in rpc_response["error"]["message"]:
                        logger.info("❗未知方法，尝试引导模型使用合法方法")
                        response = self.agent.ask_stream(current_history, known_methods=self.agent.available_methods, check_cancel=check_cancel)
                        continue

                    current_history += [
                        {"role": "assistant", "content": response},
                        {"role": "system", "content": f"RPC调用结果：{json.dumps(rpc_response, ensure_ascii=False)}"}
                    ]
                    response = self.agent.ask_stream(current_history, check_cancel=check_cancel)

                    if rpc_response.get("result", {}).get("done") is True:
                        break

                    continue

                logger.warning("⚠️ 无法识别为有效的 JSON-RPC 请求或响应，跳出")
                break

            except Exception as e:
                logger.error("❌ 出现异常:", str(e))
                return f"❌ 出现异常：{str(e)}"

        return response
