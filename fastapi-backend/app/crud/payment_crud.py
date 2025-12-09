from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.models.user import User
from typing import Union

def create_payment(db: Session, user: User, amount: Union[int, float], status="pending"):
    payment = Payment(user_id=user.id, amount=amount, status=status)
    db.add(payment)
    if status == "completed":
        credits_to_add = int(amount * 10)  # 1 USD = 10 credits (convert to int for credits)
        user.credits += credits_to_add
    
    db.commit()
    db.refresh(payment)
    db.refresh(user)
    return payment

def update_payment_status(db: Session, payment: Payment, status: str):
    payment.status = status
    db.commit()
    db.refresh(payment)
    return payment
