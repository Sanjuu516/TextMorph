import streamlit as st
import requests
import time
import sys
import os

# Include parent dir for utils import if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import get_backend_url, validate_email

st.title("Create Your Account ✨")

with st.container(border=True):
    with st.form(key='register_form'):
        username = st.text_input("Username", placeholder="johndoe")
        email = st.text_input("Email Address", placeholder="user@gmail.com")
        password = st.text_input("Password (min 6 chars)", type="password", placeholder="••••••••")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")
        full_name = st.text_input("Full Name", placeholder="John Doe")
        register_submitted = st.form_submit_button("Create Account", use_container_width=True)

        if register_submitted:
            email_clean = email.strip() if email else ""
            username_clean = username.strip() if username else ""
            full_name_clean = full_name.strip() if full_name else ""

            if not all([username_clean, email_clean, password, confirm_password, full_name_clean]):
                st.error("Please fill out all required fields.", icon="⚠️")
            elif not validate_email(email_clean):
                st.error("Please enter a valid, authentic email address (e.g., user@gmail.com).", icon="🚨")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long.", icon="⚠️")
            elif password != confirm_password:
                st.error("Passwords do not match!", icon="❌")
            else:
                backend_url = f"{get_backend_url()}/users/"
                user_data = {
                    "username": username_clean,
                    "email": email_clean,
                    "password": password,
                    "full_name": full_name_clean
                }
                try:
                    response = requests.post(backend_url, json=user_data, timeout=10)
                    if response.status_code == 200:
                        st.success("Account created successfully! Redirecting to login...", icon="✅")
                        time.sleep(1.5)
                        try:
                            st.switch_page("app.py")
                        except Exception:
                            st.rerun()
                    else:
                        try:
                            detail = response.json().get('detail', 'Registration failed.')
                            st.error(f"Failed to create account: {detail}", icon="🚨")
                        except Exception:
                            st.error(f"An unexpected error occurred on the server (Status: {response.status_code}).", icon="🔥")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the backend server. Please verify backend status.", icon="🔥")

if st.button("← Back to Login"):
    try:
        st.switch_page("app.py")
    except Exception:
        st.rerun()
