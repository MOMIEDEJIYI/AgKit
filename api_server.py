from fastapi import FastAPI, Request
from pydantic import BaseModel
from agent.agent import agent

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        reply = agent.ask(req.message, user_id=req.user_id)
        return {"reply": reply}
    except Exception as e:
        return {"error": str(e)}
