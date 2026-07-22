import streamlit as st
import requests
from utils import get_backend_url, validate_email

# Set the page configuration
st.set_page_config(
    page_title="TextMorph",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- State Management ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

# --- Login Page Logic ---
st.title("Welcome Back! 👋")

with st.container(border=True):
    st.markdown("Sign in to continue to **TextMorph**.")
    with st.form(key='login_form'):
        email = st.text_input("Email Address", placeholder="your.name@gmail.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        st.checkbox("Remember me")
        login_submitted = st.form_submit_button("Sign In", use_container_width=True)
        
        if login_submitted:
            email_clean = email.strip() if email else ""
            if not email_clean or not password:
                st.error("Please enter both email and password.", icon="⚠️")
            elif not validate_email(email_clean):
                st.error("Please enter a valid, authentic email address (e.g., user@gmail.com).", icon="🚨")
            else:
                backend_url = f"{get_backend_url()}/token"
                login_data = {'username': email_clean, 'password': password}
                try:
                    response = requests.post(backend_url, data=login_data, timeout=10)
                    if response.status_code == 200:
                        st.success("Login Successful!", icon="🎉")
                        st.session_state.logged_in = True
                        st.session_state.user_email = email_clean
                        try:
                            st.switch_page("pages/1_Profile.py") 
                        except Exception as e:
                            st.error(f"Navigation failed: {e}")
                            st.info("Please select Profile from the sidebar navigation.")
                    else:
                        st.error("Invalid email or password. Please verify your credentials.", icon="🚨")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the backend server. Please verify the backend service status.", icon="🔥")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}", icon="🚨")

st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("Create an Account", use_container_width=True):
        try:
            st.switch_page("pages/Register.py")
        except Exception as e:
            st.error(f"Failed to navigate to Register page: {e}")

with col2:
    if st.button("Forgot Password?", use_container_width=True):
        try:
            st.switch_page("pages/Forgot_Password.py")
        except Exception as e:
            st.error(f"Failed to navigate to Forgot Password page: {e}")

st.markdown(
    """
    <style>
        /* Hide sidebar navigation when not logged in */
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=not st.session_state.logged_in
)