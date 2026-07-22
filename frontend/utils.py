import os
import re
import hashlib
import json
import streamlit as st

DB_FILE = "users.json"

def get_backend_url() -> str:
    """
    Returns the backend API URL dynamically based on secrets, environment variables, or default local server.
    Safely handles StreamlitSecretNotFoundError when no secrets.toml file exists.
    """
    try:
        if "BACKEND_URL" in st.secrets:
            return str(st.secrets["BACKEND_URL"]).rstrip("/")
    except Exception:
        pass
    return os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

def validate_email(email: str) -> bool:
    """
    Validates if an email address is real, authentic, and properly formatted.
    Enforces standard email format (e.g. user@gmail.com, name@domain.edu).
    """
    if not email or not isinstance(email, str):
        return False
    email = email.strip()
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False
    # Disallow common fake domains or placeholder inputs
    domain = email.split('@')[-1].lower()
    if domain in ['test.com', 'example.com', 'fake.com', 'xyz.com', 'abc.com', 'test']:
        return False
    return True

def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password, age, language):
    users = load_users()
    users[username] = {"password": hash_password(password), "age": age, "language": language}
    save_users(users)

def check_user(username, password):
    users = load_users()
    if username in users and users[username]["password"] == hash_password(password):
        return True
    return False
