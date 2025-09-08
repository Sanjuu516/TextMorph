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
import textstat 
from nltk.tokenize import sent_tokenize

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
# Ensures all necessary resources for analysis are present
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading NLTK resources (VADER lexicon and Punkt tokenizer)...")
    nltk.download('vader_lexicon')
    nltk.download('punkt')


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

def analyze_text_complexity(text: str):
    """
    Analyzes text complexity by classifying each sentence based on the
    Flesch-Kincaid Grade Level.
    """
    sentences = sent_tokenize(text)
    if not sentences:
        return {"beginner": 0, "intermediate": 0, "advanced": 0}

    beginner_count, intermediate_count, advanced_count = 0, 0, 0

    for sentence in sentences:
        # Skip very short sentences that can skew results
        if len(sentence.split()) < 5:
            continue
        try:
            grade_level = textstat.flesch_kincaid_grade(sentence)
            if grade_level < 8:
                beginner_count += 1
            elif 8 <= grade_level <= 12:
                intermediate_count += 1
            else:
                advanced_count += 1
        except Exception:
            continue

    total_valid = beginner_count + intermediate_count + advanced_count
    if total_valid == 0:
        # If all sentences were too short, classify as beginner
        return {"beginner": 100, "intermediate": 0, "advanced": 0}

    return {
        "beginner": round((beginner_count / total_valid) * 100),
        "intermediate": round((intermediate_count / total_valid) * 100),
        "advanced": round((advanced_count / total_valid) * 100),
    }

def analyze_text_complexity(text: str):
    """Analyzes text complexity by classifying each sentence."""
    sentences = sent_tokenize(text)
    if not sentences:
        return {"beginner": 0, "intermediate": 0, "advanced": 0}
    
    counts = {"beginner": 0, "intermediate": 0, "advanced": 0}
    for sentence in sentences:
        if len(sentence.split()) < 5: continue
        try:
            grade = textstat.flesch_kincaid_grade(sentence)
            if grade < 8: counts["beginner"] += 1
            elif 8 <= grade <= 12: counts["intermediate"] += 1
            else: counts["advanced"] += 1
        except Exception:
            continue
    
    total = sum(counts.values())
    if total == 0: return {"beginner": 100, "intermediate": 0, "advanced": 0}
    
    return {level: round((count / total) * 100) for level, count in counts.items()}

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
def summarize_text(summary_request: schemas.SummaryRequest, db: Session = Depends(get_db)):
    model_name = summary_request.model_name
    text = summary_request.text
    length = summary_request.length
    user_email = summary_request.user_email

    if model_name not in summarization_pipelines:
        print(f"Loading summarization model: {model_name}...")
        try:
            summarization_pipelines[model_name] = pipeline("summarization", model=model_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load model: {e}")
    
    summarizer = summarization_pipelines[model_name]
    
    length_map = {"short": 50, "medium": 150, "long": 300}
    max_len = length_map.get(length, 150)
    min_len = int(max_len * 0.3)

    try:
        summary_result = summarizer(text, max_length=max_len, min_length=min_len, do_sample=False)
        summary_text = summary_result[0]['summary_text']

        # Save to history if user is logged in
        if user_email:
            history_entry = schemas.HistoryCreate(
                user_email=user_email,
                operation_type="Summarize",
                original_text=text,
                result_text=summary_text
            )
            crud.create_history_entry(db=db, history=history_entry)

        # Perform complexity analysis
        original_analysis = analyze_text_complexity(text)
        summary_analysis = analyze_text_complexity(summary_text)
        
        # Return the complete data structure
        return {
            "summary": summary_text,
            "original_text_analysis": original_analysis,
            "summary_text_analysis": summary_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {e}")

@app.post("/paraphrase/")
def paraphrase_text(paraphrase_request: schemas.ParaphraseRequest, db: Session = Depends(get_db)):
    """
    Paraphrases the given text and saves the result to history if a user email is provided.
    Also analyzes the text complexity of the original and paraphrased versions.
    """
    model_name = paraphrase_request.model_name
    text = paraphrase_request.text
    creativity = paraphrase_request.creativity
    length = paraphrase_request.length
    user_email = paraphrase_request.user_email

    print("Backend received this request:", paraphrase_request)

    if model_name not in paraphrasing_pipelines:
        print(f"Loading paraphrasing model: {model_name}...")
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            paraphrasing_pipelines[model_name] = (model, tokenizer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load model: {e}")
    
    model, tokenizer = paraphrasing_pipelines[model_name]
    
    original_word_count = len(text.split())
    if length == "short":
        min_len, max_len = int(original_word_count * 0.4), int(original_word_count * 0.7)
    elif length == "long":
        min_len, max_len = int(original_word_count * 1.1), int(original_word_count * 1.5)
    else:
        min_len, max_len = int(original_word_count * 0.8), int(original_word_count * 1.2)
    
    if min_len < 10: min_len = 10
    if max_len <= min_len: max_len = min_len + 20

    temperature = 0.5 + creativity
    top_p = 0.85 + (creativity / 10)

    try:
        inputs = tokenizer.encode("paraphrase: " + text, return_tensors="pt", max_length=512, truncation=True)
        summary_ids = model.generate(
          inputs,
          min_length=min_len,
          max_length=max_len,
          num_return_sequences=3,
          do_sample=True,
          temperature=temperature,
          top_p=top_p
        )
        paraphrased_texts = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=True) for g in summary_ids]

        if user_email:
            print(f"Attempting to save history for user: {user_email}")
            combined_results = "\n\n---\n\n".join(paraphrased_texts)
            history_entry = schemas.HistoryCreate(
                user_email=user_email,
                operation_type="Paraphrase",
                original_text=text,
                result_text=combined_results
            )
            crud.create_history_entry(db=db, history=history_entry)

        original_analysis = analyze_text_complexity(text)
        paraphrased_results = []
        for p_text in paraphrased_texts:
            complexity_analysis = analyze_text_complexity(p_text)
            paraphrased_results.append({
                "text": p_text,
                "complexity": complexity_analysis
            })

        return {
            "original_text_analysis": original_analysis,
            "paraphrased_results": paraphrased_results
        }

    except Exception as e:
        print(f"An error occurred during paraphrase generation: {e}")
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

