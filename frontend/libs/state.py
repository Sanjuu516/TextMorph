import streamlit as st

def ensure_state(key: str, default_value=None):
    """
    Ensures that a key exists in Streamlit session_state.
    If not, it initializes it with default_value.
    """
    if key not in st.session_state:
        st.session_state[key] = default_value
    return st.session_state[key]
