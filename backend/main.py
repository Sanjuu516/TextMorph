import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated, List
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import nltk

from . import crud, models, schemas
from .database import SessionLocal, engine

# Load environment variables and create DB tables
load_dotenv()
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Securely get secrets from environment variables
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

# --- NLTK Download ---
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    print("Downloading NLTK VADER lexicon...")
    nltk.download('vader_lexicon')

# --- Model Caching ---
summarization_pipelines = {}
paraphrasing_pipelines = {}
sentiment_pipeline = None

# --- Helper Functions ---
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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- User & Profile Endpoints ---
@app.post("/users/", response_model=schemas.User)
def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token")
def login_for_access_token(
        # CORRECTED: Use the imported class directly
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

# --- Advanced Text Tool Endpoints ---
@app.post("/summarize/")
def summarize_text(summary_request: schemas.SummaryRequest):
    model_name = summary_request.model_name
    text = summary_request.text
    length = summary_request.length

    if model_name not in summarization_pipelines:
        print(f"Loading summarization model: {model_name}...")
        try:
            summarization_pipelines[model_name] = pipeline("summarization", model=model_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load model: {e}")
    
    summarizer = summarization_pipelines[model_name]
    
    length_map = {"short": 50, "medium": 100, "long": 150}
    max_len = length_map.get(length, 100)
    min_len = int(max_len * 0.5)

    try:
        summary = summarizer(text, max_length=max_len, min_length=min_len, do_sample=False)
        return {"summary": summary[0]['summary_text']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {e}")

@app.post("/paraphrase/")
def paraphrase_text(paraphrase_request: schemas.ParaphraseRequest):
    model_name = paraphrase_request.model_name
    text = paraphrase_request.text
    creativity = paraphrase_request.creativity

    if model_name not in paraphrasing_pipelines:
        print(f"Loading paraphrasing model: {model_name}...")
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            paraphrasing_pipelines[model_name] = (model, tokenizer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load model: {e}")
    
    model, tokenizer = paraphrasing_pipelines[model_name]
    
    temperature = 0.5 + creativity
    top_p = 0.85 + (creativity / 10)

    try:
        inputs = tokenizer.encode("paraphrase: " + text, return_tensors="pt", max_length=512, truncation=True)
        summary_ids = model.generate(
            inputs, max_length=150, num_return_sequences=3, num_beams=5, temperature=temperature, top_p=top_p
        )
        paraphrased_texts = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=True) for g in summary_ids]
        return {"paraphrased_options": paraphrased_texts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate paraphrase: {e}")

@app.post("/sentiment/")
def analyze_sentiment(sentiment_request: schemas.SentimentRequest):
    global sentiment_pipeline
    text = sentiment_request.text
    
    if sentiment_pipeline is None:
        print("Loading sentiment analysis model...")
        try:
            sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load sentiment model: {e}")
    
    try:
        results = sentiment_pipeline(text)
        return results[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze sentiment: {e}")

# --- History Endpoints ---
@app.post("/history/", response_model=schemas.History)
def save_history_entry(history: schemas.HistoryCreate, db: Session = Depends(get_db)):
    db_history = crud.create_history_entry(db=db, history=history)
    if db_history is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_history

@app.get("/history/{email}", response_model=List[schemas.History])
def read_user_history(email: str, db: Session = Depends(get_db)):
    history = crud.get_user_history(db, email=email)
    return history

