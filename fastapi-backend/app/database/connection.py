from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import re

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Extract database name from DATABASE_URL
def get_db_name(database_url):
    match = re.search(r"/([a-zA-Z0-9_]+)(\?|$)", database_url)
    if match:
        return match.group(1)
    return None

db_name = get_db_name(DATABASE_URL)

# Remove database name from URL for initial connection
def get_server_url(database_url):
    return re.sub(r"/[a-zA-Z0-9_]+(\?|$)", "/", database_url, count=1)

server_url = get_server_url(DATABASE_URL)

# Create the database if it does not exist
if db_name:
    tmp_engine = create_engine(server_url, pool_pre_ping=True)
    with tmp_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
    tmp_engine.dispose()

# Now connect to the actual database
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