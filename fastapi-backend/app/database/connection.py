from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import re

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_name(database_url: str):
    match = re.search(r"/([a-zA-Z0-9_]+)(\?|$)", database_url or "")
    if match:
        return match.group(1)
    return None


def should_auto_create_db(database_url: str) -> bool:
    return bool(database_url and database_url.startswith("mysql"))


def get_server_url(database_url: str):
    return re.sub(r"/[a-zA-Z0-9_]+(\?|$)", "/", database_url, count=1)


db_name = get_db_name(DATABASE_URL)

if db_name and should_auto_create_db(DATABASE_URL):
    server_url = get_server_url(DATABASE_URL)
    tmp_engine = create_engine(server_url, pool_pre_ping=True)
    with tmp_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
    tmp_engine.dispose()


if DATABASE_URL and DATABASE_URL.startswith("cockroachdb://"):
    from sqlalchemy_cockroachdb import run_transaction


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()