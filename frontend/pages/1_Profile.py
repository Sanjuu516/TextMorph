import streamlit as st
import requests

# --- Check Login Status ---
if not st.session_state.get('logged_in', False):
    st.error("You need to log in to view this page.")
    st.stop()

# --- Helper Function to Fetch Profile ---
def fetch_profile_data():
    email = st.session_state.user_email
    backend_url = f"http://127.0.0.1:8000/profile/{email}"
    try:
        response = requests.get(backend_url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.ConnectionError:
        return None

# --- Main Profile Page UI ---
st.title("👤 Your Profile")

profile_data = fetch_profile_data()

if profile_data is None:
    st.error("Could not fetch your profile data. Please try logging in again.")
else:
    st.info(f"You are logged in as: **{profile_data.get('email')}**")
    st.divider()

    with st.form(key="profile_form"):
        st.subheader("Personal Information")
        full_name = st.text_input("Full Name", value=profile_data.get('full_name', ''))
        age = st.number_input("Age", min_value=0, max_value=120, value=profile_data.get('age', 25))
        bio = st.text_area("Your Bio", value=profile_data.get('bio', ''), height=150)
        
        st.subheader("Text Project Settings")
        lang_pref_options = ["English", "Spanish", "French"]
        current_lang_pref = profile_data.get('language_preference', 'English')
        lang_pref_index = lang_pref_options.index(current_lang_pref) if current_lang_pref in lang_pref_options else 0
        lang_pref = st.selectbox("Language Preference", lang_pref_options, index=lang_pref_index)

        summary_len_options = ['Short', 'Medium', 'Detailed']
        current_summary_len = profile_data.get('summary_length', 'Medium')
        summary_len_index = summary_len_options.index(current_summary_len) if current_summary_len in summary_len_options else 1
        summary_len = st.select_slider(
            "Default Summary Length",
            options=summary_len_options,
            value=summary_len_options[summary_len_index]
        )
        
        summary_style_options = ['Paragraph', 'Bullet Points']
        current_summary_style = profile_data.get('summary_style', 'Paragraph')
        summary_style_index = 0 if current_summary_style == 'Paragraph' else 1
        summary_style = st.radio(
            "Default Summarization Style",
            summary_style_options,
            index=summary_style_index
        )

        submitted = st.form_submit_button("Update Profile")
        if submitted:
            update_payload = {
                "full_name": full_name,
                "age": age,
                "bio": bio,
                "language_preference": lang_pref,
                "summary_length": summary_len,
                "summary_style": summary_style,
            }
            update_url = f"http://127.0.0.1:8000/profile/{st.session_state.user_email}"
            try:
                response = requests.put(update_url, json=update_payload)
                if response.status_code == 200:
                    st.success("Profile updated successfully!")
                else:
                    st.error(f"Failed to update profile: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend to update profile.")

    st.divider()
    st.subheader("Account Management")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.success("You have been logged out.")
        st.switch_page("app.py")

