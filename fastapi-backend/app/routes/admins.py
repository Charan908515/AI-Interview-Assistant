from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.user import User
from app.models.payment import Payment

router = APIRouter()

# -----------------------
# 👤 USER MANAGEMENT
# -----------------------

# ✅ List all users
@router.get("/users", summary="List all users (Admin only)")
def list_users(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return db.query(User).all()

# ✅ Delete a user
@router.delete("/users/{user_id}", summary="Delete a user (Admin only)")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"msg": f"User {user.username} deleted"}

# ✅ Grant credits
@router.post("/users/{user_id}/grant_credits", summary="Grant credits to user (Admin only)")
def grant_credits(user_id: int, amount: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.credits += amount
    db.commit()
    db.refresh(user)
    return {"msg": f"Granted {amount} credits to {user.username}", "new_balance": user.credits}

# ✅ Deduct credits
@router.post("/users/{user_id}/deduct_credits", summary="Deduct credits from user (Admin only)")
def deduct_credits(user_id: int, amount: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.credits < amount:
        raise HTTPException(status_code=400, detail="Not enough credits")
    user.credits -= amount
    db.commit()
    db.refresh(user)
    return {"msg": f"Deducted {amount} credits from {user.username}", "new_balance": user.credits}

# -----------------------
# 💳 PAYMENT MANAGEMENT
# -----------------------

# ✅ View all payments
@router.get("/payments", summary="View all payments (Admin only)")
def view_all_payments(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return db.query(Payment).all()

# ✅ View payments by user
@router.get("/payments/{user_id}", summary="View payments of a specific user (Admin only)")
def view_user_payments(user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(Payment).filter(Payment.user_id == user_id).all()

# -----------------------
# 📊 DASHBOARD SUMMARY
# -----------------------

@router.get("/dashboard", summary="Admin Dashboard Summary (Admin only)")
def admin_dashboard(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    # Total users
    total_users = db.query(func.count(User.id)).scalar()

    # Total credits across all users
    total_credits = db.query(func.sum(User.credits)).scalar() or 0

    # Total revenue
    total_revenue = db.query(func.sum(Payment.amount)).scalar() or 0.0

    # Total number of payments
    total_payments = db.query(func.count(Payment.id)).scalar()

    return {
        "total_users": total_users,
        "total_credits": total_credits,
        "total_revenue": total_revenue,
        "total_payments": total_payments,
    }
