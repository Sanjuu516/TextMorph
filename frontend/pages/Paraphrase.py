import streamlit as st
import requests
import nltk
from rouge_score import rouge_scorer
import plotly.express as px
import pandas as pd

# --- Download NLTK data for VADER (first run) ---
# CORRECTED: The exception is now LookupError, which is the modern standard.
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    st.info("Downloading resources for sentiment analysis (one-time setup)...")
    nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# --- Check Login Status ---
if not st.session_state.get('logged_in', False):
    st.error("You need to log in to view this page.")
    st.stop()

# --- Main UI ---
st.title("✍️ Advanced Paraphrasing & Analysis Tool")
st.markdown("Rewrite your text with fine-tuned control, and get detailed evaluations of the results.")

st.divider()

# --- Input Section ---
original_text = st.text_area("Enter the text you want to process:", height=200)

# --- Creativity Slider ---
creativity_level = st.slider(
    "Adjust Creativity (Low to High)", 
    min_value=0.5, 
    max_value=1.5, 
    value=1.0, 
    step=0.1,
    help="Lower values produce more direct, literal paraphrases. Higher values are more creative and may expand on the text."
)

# --- Paraphrasing Settings ---
st.subheader("Paraphrasing Settings")
model_options = {
    "T5 Paraphraser (Humarin)": "humarin/chatgpt_paraphraser_on_T5_base",
    "Pegasus (Google)": "tuner007/pegasus_paraphrase",
    "BART (Facebook)": "eugenesiow/bart-paraphrase"
}
selected_model_name = st.selectbox("Select the AI Model:", list(model_options.keys()))

# --- Main Action Button ---
if st.button("Generate & Analyze", use_container_width=True, type="primary"):
    if original_text:
        with st.spinner("The AI is working its magic... This might take a moment."):
            # --- Backend Call for Paraphrasing ---
            paraphrase_url = "http://127.0.0.1:8000/paraphrase/"
            paraphrase_payload = {
                "text": original_text,
                "model_name": model_options[selected_model_name],
                "creativity": creativity_level
            }
            try:
                response = requests.post(paraphrase_url, json=paraphrase_payload)
                if response.status_code == 200:
                    paraphrased_options = response.json().get("paraphrased_options", [])
                    st.success("Analysis Complete!")
                    
                    # --- Display Results ---
                    st.subheader("Paraphrased Results & Evaluation")

                    # Calculate ROUGE scores
                    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
                    scores_data = []

                    for i, option in enumerate(paraphrased_options, 1):
                        st.text_area(f"Option {i}", option, height=120)
                        scores = scorer.score(original_text, option)
                        scores_data.append({
                            'Option': f'Option {i}',
                            'ROUGE-1': scores['rouge1'].fmeasure,
                            'ROUGE-2': scores['rouge2'].fmeasure,
                            'ROUGE-L': scores['rougeL'].fmeasure,
                        })

                    # --- ROUGE Score Visualization ---
                    if scores_data:
                        df_scores = pd.DataFrame(scores_data)
                        df_melted = df_scores.melt(id_vars='Option', var_name='Metric', value_name='F1-Score')
                        fig = px.bar(df_melted, x='Metric', y='F1-Score', color='Option', 
                                     barmode='group', title='ROUGE Score Comparison',
                                     labels={'F1-Score': 'F1-Score (Higher is Better)'})
                        st.plotly_chart(fig, use_container_width=True)

                else:
                    st.error(f"Error from backend paraphraser: {response.json().get('detail')}")

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend.")
            
            st.divider()
            
            # --- Sentiment Analysis Section ---
            st.subheader("Sentiment Analysis of Original Text")
            
            # 1. Instant analysis with NLTK VADER
            sid = SentimentIntensityAnalyzer()
            vader_scores = sid.polarity_scores(original_text)
            st.write("**Instant Analysis (NLTK VADER):**")
            st.json(vader_scores)

            # 2. In-depth analysis with Hugging Face model via backend
            st.write("**In-Depth Analysis (Hugging Face RoBERTa):**")
            # CORRECTED: The URL now points to your local backend server
            sentiment_url = "http://127.0.0.1:8000/sentiment/" 
            sentiment_payload = {"text": original_text}
            try:
                sentiment_response = requests.post(sentiment_url, json=sentiment_payload)
                if sentiment_response.status_code == 200:
                    sentiment_result = sentiment_response.json()
                    st.json(sentiment_result)
                else:
                    st.error("Could not get in-depth sentiment analysis.")
            except:
                st.error("Connection error during sentiment analysis.")

    else:
        st.warning("Please enter some text to process.")

