from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")

    purchases = relationship("Purchase", back_populates="owner")
class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String)
    price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="purchases")