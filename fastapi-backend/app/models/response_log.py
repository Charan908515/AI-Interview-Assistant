from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.connection import Base

class ResponseLog(Base):
    __tablename__ = "response_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query = Column(String(1000))
    ai_response = Column(String(2000))
    tokens_used = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="response_logs")
