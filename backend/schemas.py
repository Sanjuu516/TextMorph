from pydantic import BaseModel
from typing import Optional, List
import datetime

# --- Schemas for User & Auth ---
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

# CORRECTED: Consolidated into one class with all required fields
class ParaphraseRequest(BaseModel):
    text: str
    model_name: str
    creativity: float
    length: str
    user_email: Optional[str] = None # Added to link history for logged-in users

class SentimentRequest(BaseModel):
    text: str

# --- Schemas for History ---
class HistoryBase(BaseModel):
    operation_type: str
    original_text: str
    result_text: str

class HistoryCreate(HistoryBase):
    user_email: str

class History(HistoryBase):
    id: int
    timestamp: datetime.datetime
    user_email: str

    class Config:
        from_attributes = True
