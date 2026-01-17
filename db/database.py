from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Read DATABASE_URL from environment, fallback to SQLite for local development
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/app.db")

# SQLite requires special connect_args
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

