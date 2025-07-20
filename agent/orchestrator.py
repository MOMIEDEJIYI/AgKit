import json
from agent.rpc_handler import handle_rpc_request
from rpc_registry import METHOD_FLAGS
from utils import utils
import logging
from config import PROVIDER

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self, agent):
        self.agent = agent

    # def _format_tool_response_for_history(self, response, rpc_response):
    #     """
    #     格式化助手回复和工具调用结果，用于追加到历史。
    #     兼容 Gemini 和 OpenAI，避免传原始 JSON，方便模型理解。
    #     """
    #     response = utils.process_assistant_content(response)
    #     # assistant 内容优先用 explanation，没有则用完整 response 的简化文本
    #     if isinstance(response, dict):
    #         assistant_content = response.get("explanation")
    #         if not assistant_content:
    #             # 尽量转换成字符串，避免直接json dump
    #             assistant_content = json.dumps(response, ensure_ascii=False)
    #     else:
    #         assistant_content = str(response)

    #     # 解析 rpc_response 的结果文本
    #     rpc_result_text = ""
    #     if rpc_response:
    #         if "result" in rpc_response:
    #             result = rpc_response["result"]
    #             if isinstance(result, dict) and "content" in result:
    #                 rpc_result_text = result["content"]
    #             else:
    #                 rpc_result_text = json.dumps(result, ensure_ascii=False)
    #         elif "error" in rpc_response:
    #             rpc_result_text = f"工具执行出错：{rpc_response['error']['message']}"

    #     system_content = f"工具调用已完成，结果为：{rpc_result_text}"
    #     return {"assistant": assistant_content, "system": system_content}
    def _format_tool_response_for_history(self, response, rpc_response):
        response = utils.extract_json_from_text(response)
        if isinstance(response, dict):
            assistant_content = json.dumps(response, ensure_ascii=False)
        else:
            assistant_content = str(response)

        if rpc_response:
            # 直接序列化整个 rpc_response 作为 system 内容，确保模型看到完整结构
            system_content = (
                f"{json.dumps(rpc_response, ensure_ascii=False)}"
            )
        else:
            system_content = "工具调用已完成，结果为空"

        return {"assistant": assistant_content, "system": system_content}

    def _run_task_common(self, history, ask_func, first_response=None, check_cancel=lambda: False):
        current_history = history[:]
        tool_result = None
        needs_nlg = False
        tool_result_wrap = False
        response = first_response or ask_func(current_history, check_cancel=check_cancel)

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
                    method_flags = METHOD_FLAGS.get(method_name, {})
                    print("收到 JSON-RPC 请求： %s", json.dumps(rpc_obj, ensure_ascii=False))
                    rpc_response = handle_rpc_request(json.dumps(rpc_obj))
                    if rpc_response is None:
                        break
                    needs_nlg = method_flags.get("needs_nlg", False)
                    tool_result_wrap = method_flags.get("tool_result_wrap", False)
                    if rpc_response.get("error") and "未知方法" in rpc_response["error"]["message"]:
                        print("未知方法，尝试引导模型使用合法方法")
                        response = ask_func(current_history, known_methods=self.agent.available_methods, check_cancel=check_cancel)
                        continue
                    print(f"""
                          方法 {method_name} 标记:
                          needs_nlg={needs_nlg}
                          tool_result_wrap={tool_result_wrap}
                          结果：{rpc_response}
                    """)
                    if needs_nlg:
                        tool_result = rpc_response.get('result', {})
                        formatted = self._format_tool_response_for_history(response, rpc_response)
                        if PROVIDER == "gemini":
                            current_history += [
                                {"role": "assistant", "content": formatted["assistant"]},
                                {"role": "assistant", "content": formatted["system"]}
                            ]
                        else:
                            current_history += [
                                {"role": "assistant", "content": formatted["assistant"]},
                                {"role": "assistant", "content": formatted["system"]}
                            ]
                        print("工具调用成功，当前对话记录:", current_history)
                        response = ask_func(current_history, check_cancel=check_cancel)
                        break

                    if rpc_response is None:
                        print("请求是通知类型，无需响应")
                        break

                    formatted = self._format_tool_response_for_history(response, rpc_response)
                    if PROVIDER == "gemini":
                        current_history += [
                            {"role": "assistant", "content": formatted["assistant"]},
                            {"role": "assistant", "content": formatted["system"]}
                        ]
                    else:
                        current_history += [
                            {"role": "assistant", "content": formatted["assistant"]},
                            {"role": "assistant", "content": formatted["system"]}
                        ]

                    # response = ask_func(current_history, check_cancel=check_cancel)
                    print("不需要 NLG，直接响应")
                    response = json.dumps({
                        "explanation": rpc_response.get("result", {}).get("content", "操作已完成"),
                        "jsonrpc": rpc_response
                    }, ensure_ascii=False)
                    

                    # 如果没有done字段，避免循环
                    if rpc_response.get("result") is None or rpc_response.get("result").get("done") is True:
                        break

                    continue

                print("无法识别为有效的 JSON-RPC 请求或响应，跳出")
                break

            except Exception as e:
                print(f"出现异常: {str(e)}")
                return f"出现异常：{str(e)}"

        if tool_result_wrap and tool_result is not None:
            return {
                "text": response,
                "tool_result": tool_result
            }
        return response

    def run_task_sync(self, history, first_response=None, check_cancel=lambda: False):
        return self._run_task_common(history, self.agent.ask, first_response, check_cancel)

    def run_task_stream(self, history, first_response=None, check_cancel=lambda: False):
        return self._run_task_common(history, self.agent.ask_stream, first_response, check_cancel)
