import os
import time
import requests

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")
TIMEOUT = 10
USE_DEMO = True  # set False when your backend is ready

class API:
    @staticmethod
    def register(username: str, email: str, full_name: str | None, password: str):
        if USE_DEMO:
            time.sleep(0.5)
            if username.lower() == "exists":
                return False, "Username already taken"
            return True, {"id": 1, "username": username, "email": email}
        try:
            r = requests.post(
                f"{API_BASE}/auth/register",
                json={"username": username, "email": email, "full_name": full_name, "password": password},
                timeout=TIMEOUT,
            )
            return (True, r.json()) if r.status_code == 201 else (False, r.json().get("detail", "Unknown error"))
        except Exception as e:
            return False, str(e)

    @staticmethod
    def login(username_or_email: str, password: str):
        if USE_DEMO:
            time.sleep(0.5)
            if password != "demo":
                return False, "Invalid credentials (demo password is 'demo')"
            return True, {"username": username_or_email, "access_token": "demo-token"}
        try:
            r = requests.post(
                f"{API_BASE}/auth/login",
                json={"username_or_email": username_or_email, "password": password},
                timeout=TIMEOUT,
            )
            return (True, r.json()) if r.status_code == 200 else (False, r.json().get("detail", "Login failed"))
        except Exception as e:
            return False, str(e)

    @staticmethod
    def summarize(text: str, style: str, max_words: int, save: bool, token: str | None):
        if USE_DEMO:
            time.sleep(0.8)
            fake = " ".join(text.split()[:max_words])
            if style == "bullets":
                fake = "• " + fake.replace(". ", "\n• ")
            return True, {"summary": fake or "(empty)"}
        try:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            r = requests.post(
                f"{API_BASE}/summarize",
                json={"text": text, "style": style, "max_words": max_words, "save": save},
                headers=headers,
                timeout=TIMEOUT,
            )
            return (True, r.json()) if r.status_code == 200 else (False, r.json().get("detail","Summarization failed"))
        except Exception as e:
            return False, str(e)

    @staticmethod
    def history(token: str | None):
        if USE_DEMO:
            time.sleep(0.4)
            return True, [
                {"id": 3, "created_at": "2025-08-20 19:32", "title": "Research notes", "words": 118, "style": "short"},
                {"id": 2, "created_at": "2025-08-19 10:11", "title": "Article draft", "words": 250, "style": "bullets"},
                {"id": 1, "created_at": "2025-08-17 08:41", "title": "Lecture transcript", "words": 320, "style": "detailed"},
            ]
        try:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            r = requests.get(f"{API_BASE}/history", headers=headers, timeout=TIMEOUT)
            return (True, r.json()) if r.status_code == 200 else (False, r.json().get("detail", "Could not fetch history"))
        except Exception as e:
            return False, str(e)
