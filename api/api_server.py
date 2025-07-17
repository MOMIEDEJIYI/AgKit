from fastapi import FastAPI
from api.conversation_routes import get_conversation_router
from api.chat_routes import get_chat_router
from agent.agent_service import AgentService

_agent_services = {}

def get_agent_service(user_id: str) -> AgentService:
    if user_id not in _agent_services:
        _agent_services[user_id] = AgentService(user_id=user_id)
    return _agent_services[user_id]

def create_api_app() -> FastAPI:
    app = FastAPI()
    app.include_router(get_conversation_router(get_agent_service))
    app.include_router(get_chat_router(get_agent_service))

    return app
