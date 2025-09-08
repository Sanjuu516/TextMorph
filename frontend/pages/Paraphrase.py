import streamlit as st
import requests
import nltk
from rouge_score import rouge_scorer
import plotly.express as px
import pandas as pd
import docx
import PyPDF2
from io import BytesIO, StringIO

# --- Page Configuration ---
st.set_page_config(
    page_title="Advanced Paraphrasing & Analysis Tool",
    page_icon="✍️",
    layout="wide",
)
# --- Authentication Check ---
# Ensure the user is logged in to access this feature.
if not st.session_state.get('logged_in', False):
    st.error("You need to log in to view this page.")
    st.warning("Please log in or create an account from the main page.")
    st.stop()
# --- Text Extraction Functions ---
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

# --- Download NLTK data for VADER (first run) ---
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    st.info("Downloading resources for sentiment analysis (one-time setup)...")
    nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# --- Main UI ---
st.title("✍️ Advanced Paraphrasing & Analysis Tool")
st.markdown("Rewrite your text with fine-tuned control, and get detailed evaluations of the results.")
st.divider()

# --- Input Section ---
st.subheader("1. Provide Your Text")

if 'original_text' not in st.session_state:
    st.session_state.original_text = ""

input_method = st.radio(
    "Choose input method:",
    ("Text Input", "File Upload"),
    horizontal=True,
    label_visibility="collapsed"
)

if input_method == "Text Input":
    original_text = st.text_area("Enter the text you want to process:", value=st.session_state.original_text, height=200, key="text_area_input")
else:
    uploaded_file = st.file_uploader(
        "Upload a .txt, .pdf, or .docx file",
        type=["txt", "pdf", "docx"]
    )
    if uploaded_file:
        file_bytes = uploaded_file.getvalue()
        if uploaded_file.type == "application/pdf":
            st.session_state.original_text = extract_text_from_pdf(file_bytes)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            st.session_state.original_text = extract_text_from_docx(file_bytes)
        else:
            st.session_state.original_text = extract_text_from_txt(file_bytes)

    original_text = st.text_area("Extracted Text (Editable)", value=st.session_state.original_text, height=150, key="file_text_input")

# --- Settings ---
st.subheader("2. Configure Settings")
col1, col2, col3 = st.columns(3)

with col1:
    creativity_level = st.slider(
        "Adjust Creativity (Low to High)",
        min_value=0.5, max_value=1.5, value=1.0, step=0.1,
        help="Lower values are more literal. Higher values are more creative."
    )

with col2:
    length_option = st.selectbox(
        "Select Desired Length:",
        ("Medium", "Short", "Long"),
        help="Choose the target length for the paraphrased text."
    )

with col3:
    model_options = {
        "T5 Paraphraser (Humarin)": "humarin/chatgpt_paraphraser_on_T5_base",
        "Pegasus (Google)": "tuner007/pegasus_paraphrase",
        "BART (Facebook)": "eugenesiow/bart-paraphrase"
    }
    selected_model_name = st.selectbox("Select the AI Model:", list(model_options.keys()))

# --- Main Action Button ---
st.subheader("3. Generate & Analyze")
if st.button("Run", use_container_width=True, type="primary"):
    if original_text:
        with st.spinner("The AI is working its magic... This might take a moment."):
            paraphrase_url = "http://127.0.0.1:8000/paraphrase/"

            paraphrase_payload = {
                "text": original_text,
                "model_name": model_options[selected_model_name],
                "creativity": creativity_level,
                "length": length_option.lower(),
                "user_email": st.session_state.get('user_email')
            }

            try:
                response = requests.post(paraphrase_url, json=paraphrase_payload)

                if response.status_code == 200:
                    st.success("Analysis Complete!")
                    st.session_state.response_data = response.json()
                else:
                    st.error(f"Error from backend paraphraser: {response.status_code} - {response.text}")
                    st.session_state.response_data = None

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend at http://127.0.0.1:8000/. Is it running?")
                st.session_state.response_data = None
    else:
        st.warning("Please enter some text or upload a file to process.")

# --- Display Results ---
if 'response_data' in st.session_state and st.session_state.response_data:
    response_data = st.session_state.response_data
    original_analysis = response_data.get("original_text_analysis")
    paraphrased_results = response_data.get("paraphrased_results")

    if paraphrased_results:
        paraphrased_texts_only = [res.get('text', '') for res in paraphrased_results]
        st.session_state.paraphrased_text = "\n\n---\n\n".join(paraphrased_texts_only)

        st.subheader("Paraphrased Options")
        for i, result in enumerate(paraphrased_results, 1):
            st.text_area(f"Option {i}", result['text'], height=120, key=f"option_{i}")

        st.divider()

        if original_analysis:
            st.subheader("Text Complexity Analysis")
            col_bar, col_line = st.columns(2)
            complexity_data = []
            
            for level, percentage in original_analysis.items():
                complexity_data.append({"Source": "Original", "Level": level.capitalize(), "Percentage": percentage})
            
            for i, result in enumerate(paraphrased_results, 1):
                for level, percentage in result.get('complexity', {}).items():
                    complexity_data.append({"Source": f"Option {i}", "Level": level.capitalize(), "Percentage": percentage})

            if complexity_data:
                df_complexity = pd.DataFrame(complexity_data)
                
                with col_bar:
                    fig_bar = px.bar(df_complexity, x="Source", y="Percentage", color="Level",
                                     title="<b>Complexity Breakdown</b>",
                                     labels={"Percentage": "% of Sentences"},
                                     color_discrete_map={'Beginner': '#636EFA', 'Intermediate': '#00CC96', 'Advanced': '#EF553B'},
                                     template='plotly_white')
                    fig_bar.update_layout(title_x=0.5)
                    st.plotly_chart(fig_bar, use_container_width=True)

                with col_line:
                    fig_line = px.line(df_complexity,
                                       x='Level',
                                       y='Percentage',
                                       color='Source',
                                       title="<b>Complexity Profile</b>",
                                       markers=True,
                                       labels={"Percentage": "% of Sentences", "Level": "Complexity Level"},
                                       category_orders={"Level": ["Beginner", "Intermediate", "Advanced"]},
                                       template='plotly_white'
                                      )
                    fig_line.update_layout(title_x=0.5)
                    st.plotly_chart(fig_line, use_container_width=True)

        st.subheader("Semantic Similarity (ROUGE Scores)")
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        scores_data = []
        for i, result in enumerate(paraphrased_results, 1):
            scores = scorer.score(original_text, result['text'])
            scores_data.append({
                'Option': f'Option {i}',
                'ROUGE-1': scores['rouge1'].fmeasure,
                'ROUGE-2': scores['rouge2'].fmeasure,
                'ROUGE-L': scores['rougeL'].fmeasure,
            })

        if scores_data:
            df_scores = pd.DataFrame(scores_data)
            df_melted = df_scores.melt(id_vars='Option', var_name='Metric', value_name='F1-Score')
            fig_rouge = px.bar(df_melted, x='Metric', y='F1-Score', color='Option',
                                barmode='group', title='<b>ROUGE Score Comparison</b>',
                                labels={'F1-Score': 'F1-Score (Higher is Better)'},
                                template='plotly_white',
                                text_auto='.2f')
            fig_rouge.update_traces(textposition='outside')
            fig_rouge.update_layout(title_x=0.5)
            st.plotly_chart(fig_rouge, use_container_width=True)

# --- Sentiment Analysis ---
if original_text:
    st.divider()
    st.subheader("Sentiment Analysis of Original Text")
    sid = SentimentIntensityAnalyzer()
    vader_scores = sid.polarity_scores(original_text)
    
    df_sentiment = pd.DataFrame({
        'Sentiment': ['Positive', 'Neutral', 'Negative'],
        'Score': [vader_scores['pos'], vader_scores['neu'], vader_scores['neg']]
    })

    fig_sentiment = px.bar(
        df_sentiment,
        x='Score',
        y='Sentiment',
        orientation='h',
        title='<b>Sentiment Breakdown</b>',
        labels={'Score': 'Score (0 to 1)', 'Sentiment': ''},
        color='Sentiment',
        color_discrete_map={'Positive': '#00CC96', 'Neutral': '#636EFA', 'Negative': '#EF553B'},
        template='plotly_white'
    )
    fig_sentiment.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'}, title_x=0.5)
    fig_sentiment.update_traces(texttemplate='%{x:.2f}', textposition='outside')
    
    col_sent_chart, col_sent_metric = st.columns([2, 1])
    with col_sent_chart:
        st.plotly_chart(fig_sentiment, use_container_width=True)
    with col_sent_metric:
        st.metric(label="Overall Sentiment (Compound Score)", value=f"{vader_scores['compound']:.3f}")
        st.caption("-1 (Very Negative) to +1 (Very Positive)")

# --- Download Button ---
if 'paraphrased_text' in st.session_state and st.session_state.paraphrased_text:
    st.download_button(
        label="📥 Download All Paraphrased Options",
        data=st.session_state.paraphrased_text.encode('utf-8'),
        file_name="paraphrased_results.txt",
        mime="text/plain",
        use_container_width=True
    )

