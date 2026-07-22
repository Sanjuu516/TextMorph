import streamlit as st
import requests
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import get_backend_url

# --- Check Login Status ---
if not st.session_state.get('logged_in', False):
    st.error("You need to log in to view this page.")
    st.stop()

st.title("📖 Your Transformation History")
st.markdown("Here is a record of your recent paraphrasing and summarization activities.")

# --- Fetch History Data ---
def fetch_history(email):
    """Fetches user history from the backend API."""
    backend_url = f"{get_backend_url()}/history/{email}"
    try:
        response = requests.get(backend_url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Could not fetch your history (Error: {response.status_code}).")
            return []
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend server.")
        return []

history_data = fetch_history(st.session_state.user_email)

if not history_data:
    st.info("You don't have any saved history yet. Use the paraphraser or summarizer to get started!")
else:
    for entry in reversed(history_data):
        timestamp = pd.to_datetime(entry['timestamp']).strftime('%B %d, %Y at %I:%M %p')

        with st.expander(f"**{entry['operation_type']}** on {timestamp}"):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Original Text")
                st.text_area(
                    "Original",
                    value=entry['original_text'],
                    height=200,
                    disabled=True,
                    key=f"orig_{entry['id']}"
                )
            with col2:
                st.subheader("Result")
                st.text_area(
                    "Result",
                    value=entry['result_text'],
                    height=200,
                    disabled=True,
                    key=f"trans_{entry['id']}"
                )
