from sqlalchemy.orm import Session
from app.models.transcription_log import TranscriptionLog

def create_transcription(db: Session, user_id: int, transcript_text: str):
    log = TranscriptionLog(user_id=user_id, transcript_text=transcript_text)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
