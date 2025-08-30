from sqlalchemy.orm import Session
from app.models.credit import Credit
from app.models.user import User

def add_credits(db: Session, user: User, amount: int):
    # Update user's total credits
    user.credits += amount
    db_credit = Credit(user_id=user.id, amount=amount)
    db.add(db_credit)
    db.commit()
    db.refresh(db_credit)
    return db_credit

def deduct_credits(db: Session, user: User, amount: int):
    if user.credits < amount:
        return None
    user.credits -= amount
    db_credit = Credit(user_id=user.id, amount=-amount)
    db.add(db_credit)
    db.commit()
    db.refresh(db_credit)
    return db_credit

def get_user_credits(db: Session, user: User):
    return user.credits
