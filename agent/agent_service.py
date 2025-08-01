# agent/agent_service.py
from agent.manager import ConversationManager
from agent.orchestrator import AgentOrchestrator
from agent.agent import Agent
from utils import utils
from config_service import ConfigService
import logging

logger = logging.getLogger(__name__)
class AgentService:
    def __init__(self, user_id="default"):
        self._cancel_flag = False
        config = ConfigService()
        conversation_cfg = config.get_section("conversation") or {}

        user_id = conversation_cfg.get("user_id", user_id)

        history_dir_config = conversation_cfg.get("history_dir", f"conversation/history/{user_id}")
        # 转成绝对路径
        history_dir = utils.get_abs_path_from_config_path(history_dir_config)

        print(f"AgentService: 初始化会话管理器，user_id={user_id}, history_dir={history_dir}")
        self.manager = ConversationManager(user_id=user_id, history_dir=history_dir)

        current_model = config.get_current_model()
        agent_config = config.get_model_config(current_model)
        self.agent = Agent(agent_config)
        self.orchestrator = AgentOrchestrator(self.agent)

        if not self.manager.list_sessions():
            self.manager.create_session("你是遵守 JSON-RPC 2.0 协议的智能助手")
        else:
            self.manager.switch_session(self.manager.list_sessions()[0])

    def stop(self):
        logger.info("AgentService: 设置取消标志")
        self._cancel_flag = True

    def is_cancelled(self):
        return self._cancel_flag

    def reset_cancel(self):
        self._cancel_flag = False

    def ask(self, user_input: str, check_cancel=None, progress_callback=None) -> str:
        self.reset_cancel()
        if check_cancel is None:
            check_cancel = self.is_cancelled

        if progress_callback:
            progress_callback("添加用户输入到对话历史...")
        self.manager.add_message("user", user_input)

        if check_cancel():
            return "已取消"

        if progress_callback:
            progress_callback("调用模型生成回复中...")
        history = self.manager.get_history()
        first_response = self.agent.ask(history, known_methods=self.agent._available_methods, extra_prompt=None)

        if check_cancel():
            return "已取消"

        if progress_callback:
            progress_callback("执行任务，调用RPC请求中...")
        final_response = self.orchestrator.run_task_sync(history, first_response)
        print("final_response:", final_response)

        if check_cancel():
            return "已取消"

        if progress_callback:
            progress_callback("添加助手回复到历史...")
        if isinstance(final_response, dict):
            clean_text = utils.process_assistant_content(final_response.get("text", ""))
            self.manager.add_message("assistant", clean_text)
        else:
            self.manager.add_message("assistant", final_response)

        if progress_callback:
            progress_callback("任务完成。")

        return final_response

    def ask_stream(self, user_input: str, check_cancel=None, progress_callback=None) -> str:
        self.reset_cancel()
        if check_cancel is None:
            check_cancel = self.is_cancelled

        if progress_callback:
            progress_callback("添加用户输入到对话历史...")
        self.manager.add_message("user", user_input)

        if check_cancel():
            return "已取消"

        if progress_callback:
            progress_callback("开始流式调用模型...")

        history = self.manager.get_history()
        first_response = self.agent.ask_stream(history, known_methods=self.agent._available_methods, extra_prompt=None, check_cancel=check_cancel)
        print("first_response:", first_response)
        if check_cancel():
            return "已取消"

        if progress_callback:
            progress_callback("执行流式任务，处理中...")

        final_response = self.orchestrator.run_task_stream(history, first_response, check_cancel=check_cancel)
        print("final_response:", final_response)

        if check_cancel():
            return "已取消"

        if progress_callback:
            progress_callback("添加助手回复到历史...")

        if isinstance(final_response, dict):
            clean_text = utils.process_assistant_content(final_response.get("text", ""))
            self.manager.add_message("assistant", clean_text)
        else:
            self.manager.add_message("assistant", final_response)

        if progress_callback:
            progress_callback("流式任务完成。")

        return final_response

    def delete_session(self, file_name: str):
        logger.info(f"AgentService: 删除会话 {file_name}")
        self.manager.delete_session(file_name)
        if not self.manager.current_session:
            sessions = self.manager.list_sessions()
            if sessions:
                self.manager.switch_session(sessions[0])
            else:
                new_session = self.manager.create_session("你是遵守 JSON-RPC 2.0 协议的智能助手")
                self.manager.switch_session(new_session)

    def switch_model(self, model_name: str):
        """切换当前模型并重载 agent 实例"""
        config = ConfigService()
        config.set_current_model(model_name)
        agent_config = config.get_model_config(model_name)
        self.agent = Agent(agent_config)
        self.orchestrator = AgentOrchestrator(self.agent)