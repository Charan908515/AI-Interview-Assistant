from app.database.connection import Base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    credits = Column(Integer, default=0)

    payments = relationship("Payment", back_populates="user")
