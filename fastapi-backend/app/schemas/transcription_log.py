from pydantic import BaseModel
from datetime import datetime

class TranscriptionCreate(BaseModel):
    transcript_text: str

class TranscriptionOut(BaseModel):
    id: int
    user_id: int
    transcript_text: str
    timestamp: datetime

    class Config:
        orm_mode = True
