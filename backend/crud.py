# backend/crud.py
import secrets
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- NEW FUNCTION TO UPDATE USER PROFILE ---
def update_user_profile(db: Session, email: str, user_update: schemas.UserUpdate):
    db_user = get_user_by_email(db, email=email)
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def create_reset_token(db: Session, email: str):
    user = get_user_by_email(db, email=email)
    if user:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        db.commit()
        db.refresh(user)
        return token
    return None

def reset_password(db: Session, token: str, new_password: str):
    user = db.query(models.User).filter(models.User.reset_token == token).first()
    if user:
        user.hashed_password = get_password_hash(new_password)
        user.reset_token = None
        db.commit()
        return user
    return None
