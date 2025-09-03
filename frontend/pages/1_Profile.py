import streamlit as st
import requests

# --- Check Login Status ---
if not st.session_state.get('logged_in', False):
    st.error("You need to log in to view this page.")
    st.stop()

# --- Helper function to get user data ---
@st.cache_data(ttl=300) # Cache data for 5 minutes
def get_user_data(email):
    backend_url = f"http://127.0.0.1:8000/users/{email}"
    try:
        response = requests.get(backend_url)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend.")
    return None

# --- Profile Page Content ---
st.title("Welcome to your Profile!")
st.write(f"You are logged in as: **{st.session_state.user_email}**")
st.divider()

# Fetch and display current user data
user_data = get_user_data(st.session_state.user_email)

if user_data:
    # --- Profile Form ---
    st.header("Your Information")
    with st.form(key="update_profile_form"):
        # Personal Info
        st.subheader("Personal Details")
        full_name = st.text_input("Full Name", value=user_data.get("full_name", ""))
        age = st.number_input("Age", min_value=1, max_value=120, value=user_data.get("age") or 25)
        bio = st.text_area("Bio", value=user_data.get("bio", ""), placeholder="Tell us a little about yourself...")
        
        st.divider()
        
        # Text Project Settings
        st.subheader("Project Settings")
        language = st.selectbox("Language Preference", ["English", "Hindi", "Français", "Deutsch"], index=["English", "Hindi", "Français", "Deutsch"].index(user_data.get("language_preference") or "English"))
        summary_length = st.select_slider("Default Summary Length", options=["Short", "Medium", "Detailed"], value=user_data.get("summary_length", "Medium"))
        summary_style = st.radio("Default Summary Style", options=["Paragraph", "Bullet Points"], index=["Paragraph", "Bullet Points"].index(user_data.get("summary_style", "Paragraph")))
        
        update_button = st.form_submit_button("Update Profile", use_container_width=True)

        if update_button:
            update_payload = {
                "full_name": full_name,
                "age": age,
                "language_preference": language,
                "bio": bio,
                "summary_length": summary_length,
                "summary_style": summary_style,
            }
            update_url = f"http://127.0.0.1:8000/users/{st.session_state.user_email}"
            try:
                response = requests.put(update_url, json=update_payload)
                if response.status_code == 200:
                    st.success("Profile updated successfully!")
                    st.cache_data.clear() # Clear cache to fetch fresh data
                else:
                    st.error(f"Failed to update profile: {response.json().get('detail')}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend.")

    # --- Usage & History Section ---
    st.divider()
    st.header("Activity")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Summaries This Month", user_data.get("api_calls_monthly", 0))
    with col2:
        if st.button("View Full History", use_container_width=True, disabled=True):
             # This can link to a new page in the future
             pass

    # --- Account Management Section ---
    st.divider()
    st.header("Account Management")
    
    if st.button("Change Password", use_container_width=True, disabled=True):
        st.info("This feature is coming soon!")

    st.subheader("Delete Account")
    st.warning("This action is permanent and cannot be undone.", icon="⚠️")
    if st.checkbox("I understand and wish to delete my account."):
        if st.button("Delete My Account Permanently", type="primary", use_container_width=True, disabled=True):
            st.error("This feature is coming soon!")

else:
    st.error("Could not fetch your profile data. Please try logging in again.")

# --- Logout Button ---
st.divider()
if st.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.info("You have been logged out.")
    try:
        st.switch_page("app.py")
    except Exception:
        st.rerun()
