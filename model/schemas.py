
from pydantic import BaseModel

class NewSessionRequest(BaseModel):
    user_id: str