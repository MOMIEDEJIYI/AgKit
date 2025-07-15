from PyQt5.QtCore import QThread, pyqtSignal
from agent.agent import Agent
from orchestrator import AgentOrchestrator

class WorkerThread(QThread):
    finished = pyqtSignal(str)        # 最终消息内容
    thinking = pyqtSignal(str)        # 中途提示，例如“正在思考...”
    error = pyqtSignal(str)           # 异常情况

    def __init__(self, history: list[dict]):
        super().__init__()
        self.history = history
        self.cancelled = False                 # 是否被取消
        self.agent = Agent()
        self.orchestrator = AgentOrchestrator(self.agent)

    def agent_methods(self):
        from tools.rpc_registry import METHOD_REGISTRY
        return sorted(METHOD_REGISTRY.keys())

    def run(self):
        try:
            self.thinking.emit("🤔 正在思考中，请稍等...")

            known_methods = self.agent_methods()
            first_response = self.agent.ask(self.history, known_methods=known_methods)
            if self.cancelled:
                self.finished.emit({"cancelled": True})
                return

            final_response = self.orchestrator.run_task(
                self.history,
                first_response,
                check_cancel=self.is_cancelled,
                use_stream=True  # 流式输出-参数
            )
            if self.cancelled:
                self.finished.emit({"cancelled": True})
                return

            self.finished.emit(final_response)

        except Exception as e:
            self.error.emit(f"❌ 执行出错：{str(e)}")


    def stop(self):
        print("🛑 stop() 被调用，取消任务")
        self.cancelled = True

    def is_cancelled(self):
        print("🔍 正在检查取消状态:", self.cancelled)
        return self.cancelled
