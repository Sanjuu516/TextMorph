import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from . import crud, models, schemas
from .database import SessionLocal, engine

# Load environment variables from the .env file
load_dotenv()

# Securely get secrets from environment variables
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

# This command creates the database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- Email Sending Function ---
def send_password_reset_email(recipient_email: str, reset_link: str):
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=recipient_email,
        subject='[TextMorph] Your Password Reset Link',
        html_content=f'<strong>Hello!</strong><p>You requested a password reset. Please click the link below to set a new password:</p><p><a href="{reset_link}">Reset Your Password</a></p><p>If you did not request this, please ignore this email.</p>'
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"SendGrid response status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email with SendGrid: {e}")

# --- Dependency to get a database session for each request ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---
@app.post("/users/", response_model=schemas.User)
def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

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

@app.get("/profile/{email}", response_model=schemas.User)
def get_user_profile(email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/profile/{email}", response_model=schemas.User)
def update_user_profile(email: str, profile: schemas.ProfileUpdate, db: Session = Depends(get_db)):
    db_user = crud.update_user_profile(db, email=email, profile_data=profile)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/password-recovery/{email}")
def recover_password(email: str, db: Session = Depends(get_db)):
    token = crud.create_reset_token(db, email=email)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist.",
        )
    reset_link = f"http://localhost:8501/?page=reset_password&token={token}"
    send_password_reset_email(recipient_email=email, reset_link=reset_link)
    return {"message": "Password recovery email has been sent."}

@app.post("/reset-password/", response_model=schemas.User)
def reset_password_endpoint(password_reset: schemas.PasswordReset, db: Session = Depends(get_db)):
    user = crud.reset_password(db, token=password_reset.token, new_password=password_reset.new_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )
    return user

