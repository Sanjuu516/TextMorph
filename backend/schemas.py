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

class ParaphraseRequest(BaseModel):
    text: str
    model_name: str
    creativity: float

class SentimentRequest(BaseModel):
    text: str

# --- Schemas for History ---
class HistoryBase(BaseModel):
    task_type: str
    model_used: str
    original_text: str
    transformed_text: str

class HistoryCreate(HistoryBase):
    owner_email: str

class History(HistoryBase):
    id: int
    timestamp: datetime.datetime

    class Config:
        from_attributes = True