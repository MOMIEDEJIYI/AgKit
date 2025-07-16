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

    def ask(self, user_input: str) -> str:
        print(f"用户输入：{user_input}")
        self.manager.add_message("user", user_input)
        history = self.manager.get_history()
        first_response = self.agent.ask(history)
        final_response = self.orchestrator.run_task_sync(history, first_response)
        self.manager.add_message("assistant", final_response)
        return final_response

    def ask_stream(self, check_cancel=lambda: False) -> str:
        history = self.manager.get_history()
        first_response = self.agent.ask_stream(history, check_cancel=check_cancel)
        final_response = self.orchestrator.run_task_stream(history, first_response, check_cancel=check_cancel)
        self.manager.add_message("assistant", final_response)
        return final_response
