from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.response_log import ResponseCreate, ResponseOut
from app.crud import response_crud
from app.core.dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/", response_model=ResponseOut)
def log_ai_response(response: ResponseCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    log = response_crud.create_response(db, current_user, response.query, response.ai_response, response.tokens_used)
    if log is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient credits")
    return log
