import streamlit as st
import textstat
import plotly.express as px
import pandas as pd
import requests
import fitz  # PyMuPDF
import docx
from pptx import Presentation

# --- Check Login Status ---
if not st.session_state.get('logged_in', False):
    st.error("You need to log in to view this page.")
    st.stop()

# --- Gemini API Call Function ---
def get_ai_analysis(text):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except FileNotFoundError:
        st.error("Please add your Gemini API key to .streamlit/secrets.toml")
        return None, None

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    
    prompt = f"""
    Analyze the following text for readability and tone. Provide two sections in your response:
    1.  **Analysis:** A brief, one-paragraph analysis of the text's complexity, style, and overall tone.
    2.  **Suggestions:** A bulleted list of 3-4 specific, actionable suggestions to improve the text's clarity and readability.

    Here is the text:
    ---
    {text}
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            full_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            analysis_part = full_text.split("Suggestions:")[0].replace("Analysis:", "").strip()
            suggestions_part = "Suggestions:" + full_text.split("Suggestions:")[1]
            return analysis_part, suggestions_part
        else:
            st.error(f"Error calling Gemini API: {response.text}")
            return None, None
    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to Gemini API: {e}")
        return None, None

# --- Helper function for soft classification ---
def calculate_level_percentages(grade):
    """Calculates a 'soft' classification percentage for each level."""
    b_peak, i_peak, a_peak = 5.0, 10.0, 15.0
    dist_b = abs(grade - b_peak)
    dist_i = abs(grade - i_peak)
    dist_a = abs(grade - a_peak)
    inv_dist_b = 1 / (dist_b + 0.1)
    inv_dist_i = 1 / (dist_i + 0.1)
    inv_dist_a = 1 / (dist_a + 0.1)
    total_inv_dist = inv_dist_b + inv_dist_i + inv_dist_a
    percentages = {
        "Beginner": (inv_dist_b / total_inv_dist) * 100,
        "Intermediate": (inv_dist_i / total_inv_dist) * 100,
        "Advanced": (inv_dist_a / total_inv_dist) * 100,
    }
    return percentages

# --- Main Dashboard UI ---
st.title("📝 Readability Analysis Dashboard")
st.markdown("Analyze your text for readability, complexity, and get AI-powered suggestions for improvement.")

# --- Input Methods ---
st.subheader("Provide Your Text")
input_method = st.tabs(["Paste Text", "Upload File"])

text_input = ""
with input_method[0]:
    pasted_text = st.text_area("Paste your text here", height=250)
    if pasted_text:
        text_input = pasted_text

with input_method[1]:
    # UPDATED: Added new file types
    uploaded_file = st.file_uploader(
        "Upload a .txt, .pdf, .docx, or .pptx file",
        type=['txt', 'pdf', 'docx', 'pptx']
    )
    if uploaded_file is not None:
        try:
            # NEW: Logic to handle different file types
            if uploaded_file.type == "text/plain":
                text_input = uploaded_file.getvalue().decode("utf-8")
            elif uploaded_file.type == "application/pdf":
                with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                    text_input = "".join(page.get_text() for page in doc)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = docx.Document(uploaded_file)
                text_input = "\n".join([para.text for para in doc.paragraphs])
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                prs = Presentation(uploaded_file)
                text_input = ""
                for slide in prs.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            text_input += shape.text + "\n"
            
            st.text_area("Extracted Content", text_input, height=250, disabled=True)
        except Exception as e:
            st.error(f"Error reading or processing file: {e}")

# --- Analysis Section ---
if text_input:
    st.divider()
    st.subheader("Readability Scores")
    
    # Calculate scores
    fk_grade = textstat.flesch_kincaid_grade(text_input)
    gunning_fog = textstat.gunning_fog(text_input)
    smog_index = textstat.smog_index(text_input)

    # Display metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Flesch-Kincaid Grade", f"{fk_grade:.2f}")
    col2.metric("Gunning Fog Index", f"{gunning_fog:.2f}")
    col3.metric("SMOG Index", f"{smog_index:.2f}")

    # --- Bar Chart Visualization ---
    st.subheader("Text Composition Analysis")
    
    percentages = calculate_level_percentages(fk_grade)
    primary_level = max(percentages, key=percentages.get)
    st.info(f"This text most closely resembles an **{primary_level}** level.")

    chart_data = pd.DataFrame(list(percentages.items()), columns=["Level", "Percentage"])
    
    fig = px.bar(chart_data, 
                 x="Level", 
                 y="Percentage", 
                 text=chart_data['Percentage'].apply(lambda x: f'{x:.1f}%'),
                 color="Level",
                 color_discrete_map={
                     "Beginner": "#5cb85c",
                     "Intermediate": "#f0ad4e",
                     "Advanced": "#d9534f"
                 })
    fig.update_layout(title_text='Readability Level Composition', 
                      xaxis_title="Complexity Level", 
                      yaxis_title="Composition Percentage",
                      showlegend=False)
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    # --- AI Analysis ---
    st.divider()
    st.subheader("🤖 AI-Powered Analysis & Suggestions")
    
    if st.button("Get AI Analysis", use_container_width=True):
        with st.spinner("Our AI is analyzing your text..."):
            analysis, suggestions = get_ai_analysis(text_input)
            if analysis and suggestions:
                st.success("Analysis Complete!")
                st.subheader("Analysis")
                st.write(analysis)
                st.subheader("Suggestions for Improvement")
                st.markdown(suggestions)
