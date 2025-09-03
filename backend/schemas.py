# backend/schemas.py
from pydantic import BaseModel
from typing import Optional

# --- NEW SCHEMA FOR UPDATING ---
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    language_preference: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str

class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    # --- ADD NEW FIELDS TO THE RESPONSE MODEL ---
    age: Optional[int] = None
    language_preference: Optional[str] = None
    bio: Optional[str] = None

    class Config:
        from_attributes = True

class PasswordReset(BaseModel):
    token: str
    new_password: str
