from sqlalchemy import Column, Integer, String, Float, Enum
from .database import Base

class Advertisement(Base):
    __tablename__ = "advertisements"
    id = Column(Integer, primary_key=True, index=True)
    crypto = Column(String, index=True)  # BTC, USDT и т.д.
    fiat = Column(String, index=True)    # USD, RUB и т.д.
    payment_method = Column(String, index=True)  # Bank Transfer, QIWI и т.п.
    price = Column(Float)
    type = Column(String)  # 'buy' или 'sell'
    available = Column(Float)  # Сколько доступно
