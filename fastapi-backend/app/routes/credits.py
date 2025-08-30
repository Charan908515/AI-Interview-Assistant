from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.crud import credit_crud
from app.schemas.credit import CreditCreate, CreditOut

router = APIRouter()

@router.post("/add", response_model=CreditOut)
def add_credits(credit: CreditCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return credit_crud.add_credits(db, current_user, credit.amount)

@router.post("/deduct", response_model=CreditOut)
def deduct_credits(credit: CreditCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    result = credit_crud.deduct_credits(db, current_user, credit.amount)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient credits")
    return result

@router.get("/balance")
def get_balance(current_user=Depends(get_current_user)):
    return {"credits": current_user.credits}
