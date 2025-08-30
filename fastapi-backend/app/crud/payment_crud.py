from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.models.user import User

def create_payment(db: Session, user: User, amount: int, status="pending"):
    payment = Payment(user_id=user.id, amount=amount, status=status)
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

def update_payment_status(db: Session, payment: Payment, status: str):
    payment.status = status
    db.commit()
    db.refresh(payment)
    return payment
