from sqlalchemy.orm import Session
from app.models.response_log import ResponseLog
from app.models.user import User
from app.crud.credit_crud import deduct_credits

def create_response(db: Session, user: User, query: str, ai_response: str, tokens_used: int):
    # Deduct credits for AI usage
    if deduct_credits(db, user, tokens_used) is None:
        return None  # Not enough credits
    
    log = ResponseLog(user_id=user.id, query=query, ai_response=ai_response, tokens_used=tokens_used)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
