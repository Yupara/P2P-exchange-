# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Для простоты используем SQLite. Файл будет храниться рядом с проектом.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Если вы хотите подключиться к PostgreSQL, MySQL и т.п., поменяйте строку подключения выше.

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Зависимость, которая выдаёт сессию при каждом запросе
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
