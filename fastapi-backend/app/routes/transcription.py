from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.transcription_log import TranscriptionCreate, TranscriptionOut
from app.crud import transcription_crud
from app.core.dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/", response_model=TranscriptionOut)
def log_transcription(transcription: TranscriptionCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return transcription_crud.create_transcription(db, current_user.id, transcription.transcript_text)
