from pydantic import BaseModel
from typing import Optional, List
import datetime

# --- Schemas for User & Auth ---
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    username: str
    full_name: str
    password: str

class User(UserBase):
    id: int
    username: str
    full_name: str
    age: Optional[int] = None
    bio: Optional[str] = None
    language_preference: Optional[str] = None
    summary_length: Optional[str] = None
    summary_style: Optional[str] = None

    class Config:
        from_attributes = True

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    bio: Optional[str] = None
    language_preference: Optional[str] = None
    summary_length: Optional[str] = None
    summary_style: Optional[str] = None

class PasswordReset(BaseModel):
    token: str
    new_password: str

# --- Schemas for Text Tools ---
class SummaryRequest(BaseModel):
    text: str
    model_name: str
    length: str
    user_email: Optional[str] = None

class ParaphraseRequest(BaseModel):
    text: str
    model_name: str
    creativity: float
    length: str
    style: Optional[str] = None  # MODIFIED: Made the style field optional
    user_email: Optional[str] = None

class SentimentRequest(BaseModel):
    text: str

# --- Schemas for History ---
class HistoryCreate(BaseModel):
    user_email: str
    operation_type: str
    original_text: str
    result_text: str

class History(BaseModel):
    id: int
    user_email: str
    operation_type: str
    original_text: str
    result_text: str
    timestamp: datetime.datetime

    class Config:
        from_attributes = True

