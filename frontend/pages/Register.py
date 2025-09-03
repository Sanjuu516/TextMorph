import streamlit as st
import requests
import time

# By not having a number, this page won't appear in the main sidebar
st.title("Create Your Account ✨")

with st.container(border=True):
    with st.form(key='register_form'):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        full_name = st.text_input("Full Name")
        register_submitted = st.form_submit_button("Create Account", use_container_width=True)

        if register_submitted:
            if not all([username, email, password, confirm_password, full_name]):
                st.error("Please fill out all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match!")
            else:
                backend_url = "http://127.0.0.1:8000/users/"
                user_data = {"username": username, "email": email, "password": password, "full_name": full_name}
                try:
                    response = requests.post(backend_url, json=user_data)
                    if response.status_code == 200:
                        st.success("Account created! Redirecting to login page...", icon="✅")
                        time.sleep(2) 
                        try:
                            st.switch_page("app.py")
                        except Exception:
                            st.rerun()
                    else:
                        try:
                            detail = response.json().get('detail', 'Unknown error.')
                            st.error(f"Failed to create account: {detail}")
                        except requests.exceptions.JSONDecodeError:
                            st.error(f"An unexpected error occurred on the server (Status: {response.status_code}). Please check the backend logs.")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the backend.")

if st.button("← Back to Login"):
    st.switch_page("app.py")
