# orchestrator.py
import json
from rpc_handler import handle_rpc_request
from utils import utils

class AgentOrchestrator:
    def __init__(self, agent):
        self.agent = agent

    def run_task(self, history, first_response=None, check_cancel=lambda: False, use_stream=False):
        current_history = history[:]
        response = first_response or (
            self.agent.ask_stream(current_history, check_cancel=check_cancel)
            if use_stream else
            self.agent.ask(current_history)
        )
        if isinstance(response, dict) and response.get("cancelled"):
            print("🛑 接收到中断标志，结束任务")
            return "🛑 用户取消了操作。"

        for _ in range(5):  # 最多尝试 5 次防止死循环
            if check_cancel():
                return "🛑 用户取消了操作。"

            try:
                json_str = utils.extract_json_from_text(response)
                parsed = json.loads(json_str)

                # 拿到 jsonrpc 内容（支持包在 explanation 外面那种）
                rpc_obj = parsed.get("jsonrpc") if isinstance(parsed, dict) else None

                # ✅ 是响应（有 result 或 error）→ 不再处理，进入对话阶段
                if isinstance(rpc_obj, dict) and ("result" in rpc_obj or "error" in rpc_obj):
                    print("ℹ️ 收到 JSON-RPC 响应，进入对话阶段")
                    break

                # ✅ 是请求（有 method）→ 执行处理
                if isinstance(rpc_obj, dict) and "method" in rpc_obj:
                    print("✅ 收到 JSON-RPC 请求")
                    print("⚙️ 执行 JSON-RPC 请求:", rpc_obj)
                    rpc_response = handle_rpc_request(json.dumps(rpc_obj))

                    if rpc_response is None:
                        print("ℹ️ 请求是通知类型，无需响应")
                        break

                    if rpc_response.get("error") and "未知方法" in rpc_response["error"]["message"]:
                        print("❗未知方法，尝试引导模型使用合法方法")
                        response = self.agent.ask(current_history, known_methods=self.agent.available_methods)
                        continue

                    # 把当前响应加入历史，再继续提问
                    current_history += [
                        {"role": "assistant", "content": response},
                        {"role": "system", "content": f"RPC调用结果：{json.dumps(rpc_response, ensure_ascii=False)}"}
                    ]
                    response = self.agent.ask(current_history)

                    # ✅ 如果已经完成，退出循环
                    if rpc_response.get("result", {}).get("done") is True:
                        break

                    continue

                # ❌ 无法识别结构
                print("⚠️ 无法识别为有效的 JSON-RPC 请求或响应，跳出")
                break

            except Exception as e:
                print("❌ 出现异常:", str(e))
                return f"❌ 出现异常：{str(e)}"

        return response
