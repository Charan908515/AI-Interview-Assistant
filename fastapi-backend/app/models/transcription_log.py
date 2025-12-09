from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.connection import Base

class TranscriptionLog(Base):
    __tablename__ = "transcription_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    transcript_text = Column(String(2000))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="transcription_logs")
