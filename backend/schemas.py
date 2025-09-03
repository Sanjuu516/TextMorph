from pydantic import BaseModel
from typing import Optional

# Pydantic model for creating a user (what we expect in the request body)
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str

# Pydantic model for updating a user's profile
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    bio: Optional[str] = None
    summary_length: Optional[str] = None
    summary_style: Optional[str] = None

# Pydantic model for resetting a password
class PasswordReset(BaseModel):
    token: str
    new_password: str

# Pydantic model for reading a user (what we send back in the response)
# We don't want to send the password back, even if it's hashed.
class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    age: Optional[int] = None
    bio: Optional[str] = None
    summary_length: Optional[str] = "Medium"
    summary_style: Optional[str] = "Paragraph"

    class Config:
        from_attributes = True
