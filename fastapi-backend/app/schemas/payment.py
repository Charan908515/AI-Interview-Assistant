from pydantic import BaseModel
from datetime import datetime

class PaymentCreate(BaseModel):
    amount: int

class PaymentOut(BaseModel):
    id: int
    user_id: int
    amount: int
    status: str
    timestamp: datetime

    class Config:
        orm_mode = True
