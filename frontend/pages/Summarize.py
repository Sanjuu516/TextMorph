import streamlit as st
import requests
import docx
import PyPDF2
import re
from io import BytesIO, StringIO
import pandas as pd
import plotly.express as px
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# --- Page Configuration ---
st.set_page_config(
    page_title="Advanced Summarization Tool",
    page_icon="📚",
    layout="wide",
)

# --- Authentication Check ---
# Ensure the user is logged in to access this feature.
if not st.session_state.get('logged_in', False):
    st.error("You need to log in to view this page.")
    st.warning("Please log in or create an account from the main page.")
    st.stop()

# --- Helper Functions ---
def extract_text_from_pdf(file_bytes):
    """Extracts text from a PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
        return text
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return ""

def extract_text_from_docx(file_bytes):
    """Extracts text from a DOCX file."""
    try:
        doc = docx.Document(BytesIO(file_bytes))
        text = "\n".join(para.text for para in doc.paragraphs)
        return text
    except Exception as e:
        st.error(f"Error reading DOCX file: {e}")
        return ""

def extract_text_from_txt(file_bytes):
    """Extracts text from a TXT file."""
    try:
        return StringIO(file_bytes.decode('utf-8')).read()
    except Exception as e:
        st.error(f"Error reading TXT file: {e}")
        return ""

def word_count(text: str) -> int:
    """Counts the number of words in a string."""
    return len(re.findall(r'\b\w+\b', text))

# --- Main UI ---
st.title("📚 Advanced Summarization Tool")
st.markdown("Condense long articles, reports, or documents into concise summaries.")

with st.expander("✨ Key Features & Instructions"):
    st.markdown("""
    - **How to Use:**
        1.  Choose your input method: paste text directly or upload a file.
        2.  Select an AI model and the desired summary length.
        3.  Click "Generate Summary" to process the text.
    - **🤖 Multiple AI Models:** Choose from a selection of modern, efficient AI models to get the best summary for your text.
    - **📄 File Upload:** Directly upload your `.txt`, `.pdf`, and `.docx` files.
    - **📏 Adjustable Length:** Control the output by selecting a short, medium, or long summary.
    - **📊 Side-by-Side Comparison:** View the original text and the generated summary together, with word counts and a compression ratio metric.
    - **📈 Complexity Analysis:** Visualize the linguistic complexity of the original text versus the summary.
    """)

st.divider()

# --- Session State Initialization ---
if 'summary_original_text' not in st.session_state:
    st.session_state.summary_original_text = ""
if 'summary_original_for_display' not in st.session_state:
    st.session_state.summary_original_for_display = ""
if 'summary_result_data' not in st.session_state:
    st.session_state.summary_result_data = None

# --- Input & Settings in Columns ---
col_input, col_settings = st.columns(2)

with col_input:
    st.subheader("1. Provide Your Text")
    input_method = st.radio(
        "Choose input method:",
        ("Text Input", "File Upload"),
        horizontal=True,
        label_visibility="collapsed"
    )

    original_text = ""
    if input_method == "Text Input":
        original_text = st.text_area("Enter the text to summarize:", height=250, key="summary_text_area")
    else:
        uploaded_file = st.file_uploader(
            "Upload a .txt, .pdf, or .docx file",
            type=["txt", "pdf", "docx"],
            key="summary_file_uploader"
        )
        if uploaded_file:
            with st.spinner("Extracting text from file..."):
                file_bytes = uploaded_file.getvalue()
                if uploaded_file.type == "application/pdf":
                    original_text = extract_text_from_pdf(file_bytes)
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    original_text = extract_text_from_docx(file_bytes)
                else:
                    original_text = extract_text_from_txt(file_bytes)
            st.text_area("Extracted Text (Editable)", value=original_text, height=170, key="summary_text_area_from_file")
            original_text = st.session_state.summary_text_area_from_file

with col_settings:
    st.subheader("2. Configure Settings")
    model_options = {
        "T5 Paraphraser (Humarin)": "humarin/chatgpt_paraphraser_on_T5_base",
        "Pegasus (Google)": "tuner007/pegasus_paraphrase",
        "BART (Facebook)": "eugenesiow/bart-paraphrase"
    }
    selected_model_name = st.selectbox("Select the AI Model:", list(model_options.keys()))

    length_option = st.selectbox(
        "Select Desired Summary Length:",
        ("Medium", "Short", "Long"),
        index=0,
        help="Choose the target length for the summary."
    )
    
    st.subheader("3. Generate Summary")
    if st.button("Generate Summary", use_container_width=True, type="primary"):
        if original_text and original_text.strip():
            with st.spinner("The AI is condensing the text... Please wait."):
                summarize_url = "http://127.0.0.1:8000/summarize/"
                summarize_payload = {
                    "text": original_text,
                    "model_name": model_options[selected_model_name],
                    "length": length_option.lower(),
                    "user_email": st.session_state.get('user_email')
                }

                try:
                    response = requests.post(summarize_url, json=summarize_payload)
                    if response.status_code == 200:
                        st.success("Summary Generated!")
                        st.session_state.summary_result_data = response.json()
                        st.session_state.summary_original_for_display = original_text
                    else:
                        st.error(f"Error from backend: {response.status_code} - {response.text}")
                        st.session_state.summary_result_data = None
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the backend. Is it running?")
                    st.session_state.summary_result_data = None
        else:
            st.warning("Please provide text or upload a file to summarize.")

# --- Display Results ---
if st.session_state.summary_result_data:
    st.divider()
    st.subheader("Results")

    # Extract data from the session state
    summary_data = st.session_state.summary_result_data
    original_to_display = st.session_state.summary_original_for_display
    summary_to_display = summary_data.get("summary")
    original_analysis = summary_data.get("original_text_analysis")
    summary_analysis = summary_data.get("summary_text_analysis")

    wc_orig = word_count(original_to_display)
    wc_sum = word_count(summary_to_display)
    compression = (1 - (wc_sum / wc_orig)) * 100 if wc_orig > 0 else 0

    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.markdown("#### Original Text")
        st.caption(f"Word Count: {wc_orig}")
        st.text_area("Original Text View", value=original_to_display, height=300, disabled=True, key="orig_summary_view")

    with res_col2:
        st.markdown("#### Generated Summary")
        st.caption(f"Word Count: {wc_sum}")
        st.text_area("Summary View", value=summary_to_display, height=300, key="summary_view")

    st.metric(label="Compression Rate", value=f"{compression:.1f} %", help="The percentage reduction in word count from the original text to the summary.")
    
    # --- NEW: Text Complexity Analysis Graph ---
    if original_analysis and summary_analysis:
        st.divider()
        st.subheader("Text Complexity Analysis")
        complexity_data = []
        
        for level, percentage in original_analysis.items():
            complexity_data.append({"Source": "Original", "Level": level.capitalize(), "Percentage": percentage})
        
        for level, percentage in summary_analysis.items():
            complexity_data.append({"Source": "Summary", "Level": level.capitalize(), "Percentage": percentage})

        if complexity_data:
            df_complexity = pd.DataFrame(complexity_data)
            fig_line = px.line(
                df_complexity,
                x='Level',
                y='Percentage',
                color='Source',
                title="<b>Complexity Profile Comparison</b>",
                markers=True,
                labels={"Percentage": "% of Sentences", "Level": "Complexity Level"},
                category_orders={"Level": ["Beginner", "Intermediate", "Advanced"]},
                template='plotly_white'
            )
            fig_line.update_layout(title_x=0.5)
            st.plotly_chart(fig_line, use_container_width=True)

    st.download_button(
        label="📥 Download Summary",
        data=summary_to_display.encode('utf-8'),
        file_name="summary_result.txt",
        mime="text/plain",
        use_container_width=True
    )

