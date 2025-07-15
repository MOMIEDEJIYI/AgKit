# orchestrator.py
import json
from rpc_handler import handle_rpc_request
from utils import utils

class AgentOrchestrator:
    def __init__(self, agent):
        self.agent = agent

    def run_task(self, history, first_response=None):
        current_history = history[:]
        response = first_response or self.agent.ask(current_history)

        for _ in range(5):  # 最多尝试 5 次防止死循环
            try:
                json_str = utils.extract_json_from_text(response)
                parsed = json.loads(json_str)

                # ✅ 如果包含 jsonrpc 字段，说明是调用请求
                if "jsonrpc" in parsed and isinstance(parsed["jsonrpc"], dict):
                    rpc_call = parsed["jsonrpc"]
                    print("⚙️ 执行 JSON-RPC 请求:", rpc_call)
                    rpc_response = handle_rpc_request(json.dumps(rpc_call))
                    if rpc_response.get("result") and isinstance(rpc_response["result"], dict):
                        if rpc_response["result"].get("done") is True:
                            # 任务完成，结束循环
                            break

                    if rpc_response.get("error") and "未知方法" in rpc_response["error"]["message"]:
                        print("❗未知方法，尝试引导模型使用合法方法")
                        response = self.agent.ask(current_history, known_methods=self.agent.available_methods)
                        continue

                    current_history += [
                        {"role": "assistant", "content": response},
                        {"role": "system", "content": f"RPC调用结果：{json.dumps(rpc_response, ensure_ascii=False)}"}
                    ]

                    response = self.agent.ask(current_history)
                    continue

                else:
                    break  # 没有 jsonrpc 字段，模型应该已经进入“只说话”阶段

            except Exception as e:
                print("❌ 出现异常:", str(e))
                break

        # 提取 explanation（如果模型还用 JSON 返回）
        try:
            parsed = json.loads(response)
            return parsed.get("explanation", response)
        except Exception:
            return response
