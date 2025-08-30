from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.crud import payment_crud
from app.schemas.payment import PaymentCreate, PaymentOut

router = APIRouter()

@router.post("/create", response_model=PaymentOut)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return payment_crud.create_payment(db, current_user, payment.amount, status="completed")

@router.get("/history", response_model=list[PaymentOut])
def payment_history(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return current_user.payments
