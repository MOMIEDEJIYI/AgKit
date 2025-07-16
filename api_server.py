from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.concurrency import run_in_threadpool
from typing import Optional
from agent.agent_service import AgentService
import logging

app = FastAPI()

_agent_services = {}

def get_agent_service(user_id: str) -> AgentService:
    if user_id not in _agent_services:
        _agent_services[user_id] = AgentService(user_id=user_id)
    return _agent_services[user_id]

class ChatRequest(BaseModel):
    user_id: str
    message: str
    stream: Optional[bool] = False

class ChatResponse(BaseModel):
    success: bool
    reply: Optional[str] = None
    error: Optional[str] = None

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    service = get_agent_service(req.user_id)

    try:
        if req.stream:
            # 流式调用（阻塞）用 run_in_threadpool 在后台线程执行
            reply = await run_in_threadpool(service.ask_stream, req.message)
        else:
            reply = await run_in_threadpool(service.ask, req.message)

        return ChatResponse(success=True, reply=reply)
    except Exception as e:
        logging.error(f"Chat API 出错: {e}", exc_info=True)
        return ChatResponse(success=False, error=str(e))
