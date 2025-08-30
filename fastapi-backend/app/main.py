from fastapi import FastAPI
from app.routes import auth, credits, payments, transcription, ai_responses
from app.database.connection import Base, engine
from app.routes import admins
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend (Swagger, Postman, React, Angular, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to ["http://localhost:3000"] etc.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)


# Routers
app.include_router(admins.router , prefix="/admin", tags=["admin"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(credits.router, prefix="/credits", tags=["credits"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])
app.include_router(transcription.router, prefix="/transcriptions", tags=["transcriptions"])
app.include_router(ai_responses.router, prefix="/responses", tags=["ai_responses"])
