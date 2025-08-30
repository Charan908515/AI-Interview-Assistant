from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from passlib.hash import bcrypt
from app.core.auth import hash_password, verify_password

def create_user(db: Session, user: UserCreate):
    hashed_pw = hash_password(user.password)
    db_user = User(username=user.username, email=user.email, password=hashed_pw, is_admin=user.is_admin, credits=user.credits, is_active=user.is_active)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        return False
    return user
