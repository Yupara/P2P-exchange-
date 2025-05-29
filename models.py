from sqlalchemy import Column, Integer, String
from database import Base  # Убедись, что путь к Base правильный

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # дополнительные поля по желанию:
    # is_active = Column(Boolean, default=True)
