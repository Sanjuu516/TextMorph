import streamlit as st
import requests
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import get_backend_url

st.title("Reset Your Password 🔒")

# Retrieve token from query params or manual entry
token = ""
if hasattr(st, "query_params") and 'token' in st.query_params:
    token = st.query_params['token']

if not token:
    st.info("No password reset token was detected in the URL query parameters.")
    token = st.text_input("Enter Reset Token", placeholder="Paste token here")
    if not token:
        st.warning("Please provide a valid password reset token or request a new recovery link.")
        if st.button("← Back to Forgot Password"):
            try:
                st.switch_page("pages/Forgot_Password.py")
            except Exception:
                st.rerun()
        st.stop()

st.markdown("Enter your new password below.")
with st.form(key='reset_password_form'):
    new_password = st.text_input("New Password (min 6 chars)", type="password", placeholder="••••••••")
    confirm_password = st.text_input("Confirm New Password", type="password", placeholder="••••••••")
    submit_button = st.form_submit_button("Reset Password", use_container_width=True)

    if submit_button:
        if not all([new_password, confirm_password]):
            st.error("Please fill out both password fields.", icon="⚠️")
        elif len(new_password) < 6:
            st.error("Password must be at least 6 characters long.", icon="⚠️")
        elif new_password != confirm_password:
            st.error("Passwords do not match.", icon="❌")
        else:
            backend_url = f"{get_backend_url()}/reset-password/"
            payload = {"token": token, "new_password": new_password}
            try:
                response = requests.post(backend_url, json=payload, timeout=10)
                if response.status_code == 200:
                    st.success("Password reset successfully! Redirecting to login...", icon="✅")
                    time.sleep(1.5)
                    try:
                        st.switch_page("app.py")
                    except Exception:
                        st.rerun()
                else:
                    detail = response.json().get('detail', 'Failed to reset password.')
                    st.error(f"Error: {detail}", icon="🚨")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend server.", icon="🔥")

if st.button("← Back to Login"):
    try:
        st.switch_page("app.py")
    except Exception:
        st.rerun()
