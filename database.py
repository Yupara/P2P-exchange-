from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Подключение к базе данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Или ваша PostgreSQL строка

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Создаем базу
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 👇 ЭТО ОЧЕНЬ ВАЖНО
Base = declarative_base()
