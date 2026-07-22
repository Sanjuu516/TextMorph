import streamlit as st
import requests
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import get_backend_url, validate_email

st.title("Forgot Your Password? 🔑")
st.markdown("Enter your registered email address and we will send you a password recovery link.")

with st.container(border=True):
    with st.form(key='forgot_password_form'):
        email = st.text_input("Email Address", placeholder="your.name@gmail.com")
        submit_button = st.form_submit_button("Send Reset Link", use_container_width=True)

        if submit_button:
            email_clean = email.strip() if email else ""
            if not email_clean:
                st.error("Please enter your email address.", icon="⚠️")
            elif not validate_email(email_clean):
                st.error("Please enter a valid, authentic email address (e.g., user@gmail.com).", icon="🚨")
            else:
                backend_url = f"{get_backend_url()}/password-recovery/{email_clean}"
                try:
                    response = requests.post(backend_url, timeout=10)
                    if response.status_code == 200:
                        st.success("Recovery email sent! Please check your inbox.", icon="✅")
                    else:
                        try:
                            detail = response.json().get('detail', 'An unknown error occurred.')
                            st.error(f"Error: {detail}", icon="🚨")
                        except Exception:
                            st.error("An unexpected error occurred. Please try again.", icon="🔥")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the backend server.", icon="🔥")

if st.button("← Back to Login"):
    try:
        st.switch_page("app.py")
    except Exception:
        st.rerun()
