from fastapi import APIRouter
from agent.agent_service import AgentService
from model import schemas

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

    @router.delete("/session")
    async def delete_session(user_id: str, session_id: str):
        service: AgentService = get_agent_service(user_id)
        try:
            service.manager.delete_session(session_id)
            return {"success": True, "deleted_session": session_id}
        except Exception as e:
            return {"success": False, "error": str(e)}
        
    @router.post("/new_session")
    async def new_session(request: schemas.NewSessionRequest):
        user_id = request.user_id
        service: AgentService = get_agent_service(user_id)
        session_id = service.manager.create_session("你是遵守 JSON-RPC 2.0 协议的智能助手，返回符合规范的 JSON-RPC 请求。")
        return {"user_id": user_id, "session_id": session_id}

    return router
