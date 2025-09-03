import streamlit as st
import requests

st.title("Forgot Your Password? 🔑")
st.markdown("Enter your email address and we'll send you a link to reset your password.")

with st.container(border=True):
    with st.form(key='forgot_password_form'):
        email = st.text_input("Email Address", placeholder="your@email.com")
        submit_button = st.form_submit_button("Send Reset Link", use_container_width=True)

        if submit_button:
            backend_url = f"http://127.0.0.1:8000/password-recovery/{email}"
            try:
                response = requests.post(backend_url)
                if response.status_code == 200:
                    st.success("Recovery email sent! Please check your console/inbox.", icon="✅")
                else:
                    # UPDATED: More robust error handling
                    try:
                        detail = response.json().get('detail', 'An unknown error occurred.')
                        st.error(f"Error: {detail}", icon="🚨")
                    except requests.exceptions.JSONDecodeError:
                        st.error("An unexpected error occurred. Please try again.", icon="🔥")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend.", icon="🔥")

if st.button("Back to Login"):
    st.switch_page("app.py")
