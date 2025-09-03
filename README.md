# TextMorph
TextMorph Advanced Text Summarization and Paraphrasing 
📖 Overview
TextMorph is a full-stack web application designed to be a comprehensive writing assistant. It provides users with powerful tools to analyze and improve their text, featuring a secure authentication system, detailed user profiles, and an advanced AI-powered dashboard for readability analysis.

The application is built with a modern, decoupled architecture, using Streamlit for a highly interactive Python-based frontend and FastAPI for a high-performance, asynchronous backend.

✨ Core Features
Secure User Authentication: Complete, end-to-end authentication flow including user registration, secure login, and a "Forgot Password" feature that sends real emails using the SendGrid API.

User Profile Management: A dedicated profile page where users can view and update their personal information and text-related preferences.

AI-Powered Readability Dashboard: The centerpiece of the application, featuring:

Multiple Input Methods: Analyze text by pasting it directly or by uploading files in various formats (.txt, .pdf, .docx, .pptx).

Quantitative Metrics: Instantly calculates key readability scores, including the Flesch-Kincaid Grade Level, Gunning Fog Index, and SMOG Index.

Visual Analysis: An interactive bar chart displays a nuanced breakdown of the text's composition across Beginner, Intermediate, and Advanced reading levels.

Gemini AI Integration: Leverages the Google Gemini API to provide deep, qualitative analysis and actionable suggestions for improving the text's clarity and tone.

🛠️ Tech Stack
Frontend (Streamlit)
Framework: Streamlit

Data Visualization: Plotly Express

Readability Metrics: textstat

File Parsing: PyMuPDF (for PDFs), python-docx (for Word), python-pptx (for PowerPoint)

API Communication: Requests

Backend (FastAPI)
Framework: FastAPI

Database ORM: SQLAlchemy

Database: SQLite

Password Security: Passlib with bcrypt hashing

Email Service: SendGrid API

Server: Uvicorn

🚀 Setup & Installation
To run this project locally, you will need to set up the backend and frontend separately.

1. Backend Setup
Navigate to the backend/ directory:

cd backend

Create and activate a Python virtual environment:

python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows

Install the required packages:

pip install "fastapi[all]" sqlalchemy "passlib[bcrypt]" sendgrid

Add API Credentials: Open backend/main.py and replace the placeholder values for SENDER_EMAIL and SENDGRID_API_KEY with your verified SendGrid information.

2. Frontend Setup
Navigate to the frontend/ directory from the root folder:

cd frontend

Create and activate a separate Python virtual environment:

python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows

Install the required packages:

pip install streamlit requests textstat plotly pandas pymupdf python-docx python-pptx

Add API Key:

Create a folder named .streamlit inside the frontend/ directory.

Inside .streamlit, create a file named secrets.toml.

Add your Gemini API key to this file:

GEMINI_API_KEY = "YOUR_API_KEY_HERE"

3. Running the Application
Start the Backend Server: From the root project directory, run:

uvicorn backend.main:app --reload --reload-dir backend

The backend will be running at http://127.0.0.1:8000.

Run the Frontend App: In a new terminal, from the root project directory, run:

streamlit run frontend/app.py
