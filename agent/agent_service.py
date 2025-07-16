# agent/agent_service.py
from agent.manager import ConversationManager
from agent.orchestrator import AgentOrchestrator
from agent.agent import Agent

class AgentService:
    def __init__(self, user_id="default"):
        self.manager = ConversationManager(user_id)
        self.agent = Agent()
        self.orchestrator = AgentOrchestrator(self.agent)

        if not self.manager.list_sessions():
            self.manager.create_session("你是遵守 JSON-RPC 2.0 协议的智能助手")
        else:
            self.manager.switch_session(self.manager.list_sessions()[0])

    def ask(self, user_input: str, progress_callback=None) -> str:
        if progress_callback:
            progress_callback("添加用户输入到对话历史...")
        self.manager.add_message("user", user_input)

        if progress_callback:
            progress_callback("调用模型生成回复中...")
        history = self.manager.get_history()
        first_response = self.agent.ask(history)

        if progress_callback:
            progress_callback("执行任务，调用RPC请求中...")
        final_response = self.orchestrator.run_task_sync(history, first_response)

        if progress_callback:
            progress_callback("添加助手回复到历史...")
        self.manager.add_message("assistant", final_response)

        if progress_callback:
            progress_callback("任务完成。")

        return final_response

    def ask_stream(self, user_input: str, check_cancel=lambda: False, progress_callback=None) -> str:
      if progress_callback:
          progress_callback("添加用户输入到对话历史...")
      self.manager.add_message("user", user_input)

      if progress_callback:
          progress_callback("开始流式调用模型...")

      history = self.manager.get_history()
      first_response = self.agent.ask_stream(history, check_cancel=check_cancel)

      if progress_callback:
          progress_callback("执行流式任务，处理中...")

      final_response = self.orchestrator.run_task_stream(history, first_response, check_cancel=check_cancel)

      if progress_callback:
          progress_callback("添加助手回复到历史...")

      self.manager.add_message("assistant", final_response)

      if progress_callback:
          progress_callback("流式任务完成。")

      return final_response


