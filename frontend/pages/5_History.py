import streamlit as st
import requests
import pandas as pd

# --- Check Login Status ---
if not st.session_state.get('logged_in', False):
    st.error("You need to log in to view this page.")
    st.stop()

st.title("📖 Your Transformation History")
st.markdown("Here is a record of your recent summarization and paraphrasing activities.")

# --- Fetch History Data ---
@st.cache_data
def fetch_history():
    email = st.session_state.user_email
    backend_url = f"http://127.0.0.1:8000/history/{email}"
    try:
        response = requests.get(backend_url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Could not fetch your history.")
            return []
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend.")
        return []

history_data = fetch_history()

if not history_data:
    st.info("You don't have any saved history yet. Use the summarizer or paraphraser to get started!")
else:
    for entry in history_data:
        with st.expander(f"**{entry['task_type']}** on {pd.to_datetime(entry['timestamp']).strftime('%B %d, %Y at %I:%M %p')}"):
            st.caption(f"Model Used: {entry['model_used']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Original Text")
                st.text_area("Original", value=entry['original_text'], height=200, disabled=True, key=f"orig_{entry['id']}")
            with col2:
                st.subheader("Transformed Text")
                st.text_area("Transformed", value=entry['transformed_text'], height=200, disabled=True, key=f"trans_{entry['id']}")

