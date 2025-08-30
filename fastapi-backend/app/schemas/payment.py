from pydantic import BaseModel
from datetime import datetime
from typing import Union

class PaymentCreate(BaseModel):
    amount: Union[int, float]

class PaymentOut(BaseModel):
    id: int
    user_id: int
    amount: Union[int, float]
    status: str
    timestamp: datetime

    class Config:
        orm_mode = True
