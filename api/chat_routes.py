from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from typing import Any
from fastapi.concurrency import run_in_threadpool
from agent.agent_service import AgentService
import logging

def get_chat_router(get_agent_service):
    router = APIRouter(prefix="/chat", tags=["chat"])

    class ChatRequest(BaseModel):
        user_id: str
        session_id: Optional[str] = None
        message: str
        stream: Optional[bool] = False

    class ChatResponse(BaseModel):
        success: bool
        reply: Optional[Any] = None
        session_id: Optional[str] = None
        error: Optional[str] = None

    @router.post("/", response_model=ChatResponse)
    async def chat(req: ChatRequest):
        service: AgentService = get_agent_service(req.user_id)
        session = req.session_id
        try:
            if req.session_id:
                service.manager.switch_session(req.session_id)
            else:
                print("新建会话...")
                session = service.manager.create_session("你是遵守 JSON-RPC 2.0 协议的智能助手，返回符合规范的 JSON-RPC 请求。")
            
            if req.stream:
                reply = await run_in_threadpool(service.ask_stream, req.message)
            else:
                reply = await run_in_threadpool(service.ask, req.message)

            return ChatResponse(success=True, reply=reply, session_id=session)
        except Exception as e:
            logging.error(f"Chat API 出错: {e}", exc_info=True)
            return ChatResponse(success=False, error=str(e))


    return router
