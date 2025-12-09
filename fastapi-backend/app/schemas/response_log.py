from pydantic import BaseModel
from datetime import datetime

class ResponseCreate(BaseModel):
    query: str
    ai_response: str
    tokens_used: int

class ResponseOut(BaseModel):
    id: int
    user_id: int
    query: str
    ai_response: str
    tokens_used: int
    timestamp: datetime

    class Config:
        orm_mode = True
