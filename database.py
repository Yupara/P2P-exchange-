from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from contextlib import contextmanager

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Замените на вашу строку подключения если используете PostgreSQL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 👇 ДОБАВЬТЕ ЭТУ ФУНКЦИЮ
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
