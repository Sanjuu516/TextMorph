# backend/models.py
from sqlalchemy import Column, Integer, String, Text
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, index=True)
    reset_token = Column(String, unique=True, index=True, nullable=True)

    # --- NEW FIELDS FOR PROFILE ---
    age = Column(Integer, nullable=True)
    language_preference = Column(String, default="English")
    bio = Column(Text, nullable=True)
