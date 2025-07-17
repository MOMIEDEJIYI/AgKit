from fastapi import APIRouter
from agent.agent_service import AgentService

def get_conversation_router(get_agent_service):
    router = APIRouter(prefix="/conversation", tags=["conversation"])

    @router.get("/sessions")
    async def list_sessions(user_id: str):
        service: AgentService = get_agent_service(user_id)
        sessions = service.manager.list_sessions()
        return {"user_id": user_id, "sessions": sessions}

    @router.get("/session_history")
    async def session_history(user_id: str, session_id: str):
        service: AgentService = get_agent_service(user_id)
        try:
            service.manager.switch_session(session_id)
            history = service.manager.get_history()
            return {"user_id": user_id, "session_id": session_id, "history": history}
        except Exception as e:
            return {"error": str(e)}

    return router
