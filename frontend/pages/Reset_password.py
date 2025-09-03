import streamlit as st
import requests
import time

st.title("Reset Your Password")

if 'token' not in st.query_params:
    st.error("No reset token found. Please use the link from your email.")
    st.stop()

token = st.query_params['token']
st.markdown("Enter your new password below.")
with st.form(key='reset_password_form'):
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")
    submit_button = st.form_submit_button("Reset Password", use_container_width=True)

    if submit_button:
        if not all([new_password, confirm_password]):
            st.error("Please fill out both password fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.", icon="❌")
        else:
            backend_url = "http://127.0.0.1:8000/reset-password/"
            payload = {"token": token, "new_password": new_password}
            try:
                response = requests.post(backend_url, json=payload)
                if response.status_code == 200:
                    st.success("Password reset successfully! Redirecting to login...", icon="✅")
                    time.sleep(2)
                    try:
                        st.switch_page("app.py")
                    except Exception:
                        st.rerun()
                else:
                    st.error(f"Error: {response.json().get('detail')}", icon="🚨")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend.", icon="🔥")

