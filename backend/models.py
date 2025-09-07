from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Text
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    reset_token = Column(String, nullable=True)
    
    # Optional profile fields
    age = Column(Integer, nullable=True)
    bio = Column(Text, nullable=True)
    language_preference = Column(String, nullable=True)
    summary_length = Column(String, nullable=True)
    summary_style = Column(String, nullable=True)

class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, ForeignKey("users.email"))
    operation_type = Column(String, index=True)
    original_text = Column(Text)
    result_text = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

