import streamlit as st
import requests

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
    st.markdown("Sign in to continue.")
    with st.form(key='login_form'):
        email = st.text_input("Email Address", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        st.checkbox("Remember me")
        login_submitted = st.form_submit_button("Sign In", use_container_width=True)
        
        if login_submitted:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                backend_url = "http://127.0.0.1:8000/token"
                login_data = {'username': email, 'password': password}
                try:
                    response = requests.post(backend_url, data=login_data)
                    if response.status_code == 200:
                        st.success("Login Successful!", icon="🎉")
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        try:
                            # Navigate to the main profile page
                            st.switch_page("pages/1_Profile.py") 
                        except Exception as e:
                            st.error(f"Navigation failed: {e}")
                            st.info("Please navigate to the Profile page from the sidebar.")
                    else:
                        st.error("Invalid email or password.", icon="🚨")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the backend.", icon="🔥")

# --- Navigation buttons for non-logged-in users ---
st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("Create an Account", use_container_width=True):
        st.switch_page("pages/Register.py") # Removed number
with col2:
    if st.button("Forgot Password?", use_container_width=True):
        st.switch_page("pages/Forgot_Password.py") # Removed number

st.markdown(
    """
    <style>
        /* This CSS hides the sidebar navigation when not logged in */
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=not st.session_state.logged_in
)