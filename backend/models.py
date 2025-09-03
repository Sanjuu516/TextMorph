from sqlalchemy import Column, Integer, String
from .database import Base

# Define the User model, which corresponds to the "users" table in the database.
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # User Profile Fields
    full_name = Column(String, index=True, nullable=True)
    age = Column(Integer, nullable=True)
    bio = Column(String, nullable=True)
    
    # Text Project Specific Fields
    summary_length = Column(String, default="Medium")
    summary_style = Column(String, default="Paragraph")

    # Password Reset
    reset_token = Column(String, unique=True, index=True, nullable=True)
