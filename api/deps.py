from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pki.models import Base
import os

# Create relative database path mimicking alembic.ini config
db_path = "./virtual_hsm/storage/pki.db"
os.makedirs(os.path.dirname(db_path), exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Auto-create tables (bypassing the need for manual alembic migrations locally)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DbSession = Depends(get_db)
