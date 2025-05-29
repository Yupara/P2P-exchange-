from sqlalchemy import Column, Integer, String, Float
from database import Base

class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, index=True)
    crypto = Column(String, index=True)
    fiat = Column(String, index=True)
    payment_method = Column(String)
    price = Column(Float)
    type = Column(String)
    available = Column(Float)
