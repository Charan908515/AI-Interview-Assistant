import logging
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.database.connection import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.models.payment import Payment



router = APIRouter()



#  List all users
@router.get("/users", summary="List all users (Admin only)")
def list_users(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    users = db.query(User).all()
    # Return user data with usernames as identifiers
    return [
        {
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active,
            'is_admin': user.is_admin,
            'credits': user.credits
        }
        for user in users
    ]

#  Delete user
@router.delete("/users/{username}", summary="Delete a user by username (Admin only)")
async def delete_user(
    request: Request,
    username: str, 
    db: Session = Depends(get_db), 
    admin: User = Depends(get_current_admin)
):
    
    
    # Find user by username
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        error_msg = f"User with username '{username}' not found in database"
        
        all_usernames = [u.username for u in db.query(User).all()]
        
        raise HTTPException(status_code=404, detail=error_msg)
    
    
    db.delete(user)
    db.commit()
    
    return {"msg": f"User {user.username} deleted"}

#  Grant credits
@router.post("/users/{username}/grant_credits", summary="Grant credits to user (Admin only)")
async def grant_credits(
    request: Request,
    username: str, 
    amount: int, 
    db: Session = Depends(get_db), 
    admin: User = Depends(get_current_admin)
):
    
    
    # Find user by username
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        error_msg = f"User with username '{username}' not found in database"
        
        all_usernames = [u.username for u in db.query(User).all()]
        
        raise HTTPException(status_code=404, detail=error_msg)
    
    
    user.credits += amount
    db.commit()
    db.refresh(user)
    
    return {"msg": f"Granted {amount} credits to {user.username}", "new_balance": user.credits}

#    Deduct credits
@router.post("/users/{username}/deduct_credits", summary="Deduct credits from user (Admin only)")
async def deduct_credits(
    request: Request,
    username: str, 
    amount: int, 
    db: Session = Depends(get_db), 
    admin: User = Depends(get_current_admin)
):

    
    # Find user by username
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        error_msg = f"User with username '{username}' not found in database"
        
        
        
        raise HTTPException(status_code=404, detail=error_msg)
    
    
    if user.credits < amount:
        error_msg = f"Not enough credits. Current: {user.credits}, Requested: {amount}"
        
        raise HTTPException(status_code=400, detail=error_msg)
    
    
    user.credits -= amount
    db.commit()
    db.refresh(user)
        
    return {"msg": f"Deducted {amount} credits from {user.username}", "new_balance": user.credits}

#  Payment Management

#  View all payments
@router.get("/payments", summary="View all payments (Admin only)")
def view_all_payments(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return db.query(Payment).all()

#  View payments by user
@router.get("/users/{username}/payments", summary="View payments of a specific user (Admin only)")
def view_user_payments(
    username: str,
    db: Session = Depends(get_db), 
    admin: User = Depends(get_current_admin)
):
    
    
    # Find user by username
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        error_msg = f"User with username '{username}' not found in database"
    
        
        raise HTTPException(status_code=404, detail=error_msg)
    
    payments = db.query(Payment).filter(Payment.user_id == user.id).all()
    
    return payments

#  Dashboard Summary

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
