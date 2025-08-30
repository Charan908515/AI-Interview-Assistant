from pydantic import BaseModel
from datetime import datetime

class CreditCreate(BaseModel):
    amount: int

class CreditOut(BaseModel):
    id: int
    user_id: int
    amount: int
    timestamp: datetime

    class Config:
        orm_mode = True
