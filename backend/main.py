# backend/main.py

import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from . import crud, models, schemas
from .database import SessionLocal, engine

# --- Email Configuration ---
# IMPORTANT: Replace these with your own details.
# For security, use environment variables in a real application.
SENDER_EMAIL = "sanjananarni516@gmail.com"
SENDGRID_API_KEY = "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"


# This command creates the database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- Helper function to send email using SendGrid ---
def send_reset_email(recipient_email: str, reset_link: str):
    """Sends the reset email using the SendGrid API."""
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=recipient_email,
        subject='Password Reset Request',
        html_content=f'<strong>Hello,</strong><br><br>Please click the following link to reset your password: <a href="{reset_link}">Reset Password</a><br><br>If you did not request this, please ignore this email.<br><br>Thanks,<br>The Team'
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"SendGrid response status code: {response.status_code}")
        return response.status_code == 202 # 202 is the success code for SendGrid
    except Exception as e:
        print(f"Error sending email with SendGrid: {e}")
        return False

# Dependency to get a database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API endpoint to create a user
@app.post("/users/", response_model=schemas.User)
def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# API endpoint for user login
@app.post("/token")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user.username, "token_type": "bearer"}

# --- NEW ENDPOINT TO GET USER DATA ---
@app.get("/users/{email}", response_model=schemas.User)
def read_user(email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# --- NEW ENDPOINT TO UPDATE USER DATA ---
@app.put("/users/{email}", response_model=schemas.User)
def update_user(email: str, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    updated_user = crud.update_user_profile(db, email=email, user_update=user_update)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

# Endpoint to request a password reset
@app.post("/password-recovery/{email}")
def recover_password(email: str, db: Session = Depends(get_db)):
    token = crud.create_reset_token(db, email=email)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist.",
        )
    
    reset_link = f"http://localhost:8501/?page=reset_password&token={token}"
    email_sent = send_reset_email(recipient_email=email, reset_link=reset_link)
    
    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send password recovery email."
        )

    return {"message": "Password recovery email sent successfully."}

# Endpoint to set a new password using the token
@app.post("/reset-password/", response_model=schemas.User)
def reset_password_endpoint(password_reset: schemas.PasswordReset, db: Session = Depends(get_db)):
    user = crud.reset_password(db, token=password_reset.token, new_password=password_reset.new_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )
    return user
