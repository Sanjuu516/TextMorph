# TextMorph — AI Paraphrasing, Summarization & Readability Workspace

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com/)
[![Google Gemini API](https://img.shields.io/badge/Google_Gemini_API-8E44AD?style=for-the-badge&logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![Infosys Springboard](https://img.shields.io/badge/Infosys_Springboard-6.0-007CC3?style=for-the-badge)](https://springboard.infosys.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

**TextMorph** is a full-stack, decoupled Natural Language Processing (NLP) workspace and writing intelligence platform built by **Sanjana Narni** as part of the **Infosys Springboard Virtual Internship 6.0**. 

The application combines a reactive **Streamlit** front-end dashboard with a high-performance **FastAPI** RESTful microservice backend, enabling multi-format document ingestion, quantitative readability scoring, multi-model text summarization, AI-driven paraphrasing, and automated user digest reporting.

---

## ⚡ System Architecture & Design

TextMorph uses a decoupled client-server architecture. The Streamlit frontend processes document bytes and user inputs, delegating computationally heavy NLP transformations, authentication, and database persistence to the FastAPI REST layer.

```
                           ┌─────────────────────────────────────────┐
                           │          Streamlit Web Frontend         │
                           │   (Document Upload & Visual Workspace)  │
                           └────────────────────┬────────────────────┘
                                                │
                                    HTTP REST / JSON Payload
                                                │
                                                ▼
                           ┌─────────────────────────────────────────┐
                           │          FastAPI Microservice           │
                           │     (Auth, NLP Endpoints & Routing)     │
                           └───────┬────────────┬────────────┬───────┘
                                   │            │            │
          ┌────────────────────────┘            │            └────────────────────────┐
          ▼                                     ▼                                     ▼
┌───────────────────┐                 ┌───────────────────┐                 ┌───────────────────┐
│ SQLite DB & ORM   │                 │ Google Gemini API │                 │   SendGrid API    │
│ (Users & Logs)    │                 │ (AI Paraphrasing) │                 │  (Email Services) │
└───────────────────┘                 └───────────────────┘                 └───────────────────┘
```

---

## 🛠️ Technology Stack

### **Frontend Framework & Data Parsing**
| Technology | Role & Utility |
| :--- | :--- |
| **[Streamlit](https://streamlit.io/)** | Reactive UI layout, stateful page routing, interactive controls |
| **[Plotly Express](https://plotly.com/python/)** | Interactive distribution charts for readability breakdown |
| **[textstat](https://pypi.org/project/textstat/)** | Flesch-Kincaid, Gunning Fog, and SMOG Index calculation |
| **[PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)** | High-speed PDF text and layout extraction |
| **[python-docx](https://python-docx.readthedocs.io/)** | Microsoft Word (`.docx`) document parsing |
| **[python-pptx](https://python-pptx.readthedocs.io/)** | Microsoft PowerPoint (`.pptx`) slide text extraction |

### **Backend Server & Security**
| Technology | Role & Utility |
| :--- | :--- |
| **[FastAPI](https://fastapi.tiangolo.com/)** | Asynchronous ASGI REST server with auto-generated OpenAPI docs |
| **[SQLAlchemy](https://www.sqlalchemy.org/)** | Database ORM mapping user accounts, profiles, and request history |
| **[SQLite](https://www.sqlite.org/)** | Embedded relational database storage (`sql_app.db`) |
| **[Passlib (bcrypt)](https://passlib.readthedocs.io/)** | Salted password hashing and secure token verification |
| **[SendGrid API](https://sendgrid.com/)** | Automated SMTP email dispatch for password reset and digests |
| **[Google Gemini API](https://ai.google.dev/)** | Context-aware AI text paraphrasing, summarization, and tone rewriting |

---

## ✨ Core Features & Functional Overview

### 1. 📄 **Multi-Format Document Ingestion**
* **Direct File Upload**: Drag-and-drop support for `.txt`, `.pdf`, `.docx`, and `.pptx` documents.
* **Stream Ingestion**: Extracts text contents in memory without writing temporary raw files to disk.

### 2. 📊 **Quantitative Readability Analytics**
* **Readability Metrics Engine**: Computes standardized reading grade indices:
  * **Flesch-Kincaid Grade Level**: Assesses comprehension difficulty by sentence length and syllable count.
  * **Gunning Fog Index**: Evaluates complex word density.
  * **SMOG Index**: Estimates years of formal education needed to understand the text.
* **Interactive Visual Breakdown**: Plotly charts mapping text complexity across **Beginner**, **Intermediate**, and **Advanced** reading tiers.

### 3. 🤖 **Gemini AI Paraphrasing & Summarization**
* **Context-Aware Rewriting**: Adjusts text tone (Professional, Academic, Concise, Creative) while preserving core semantic intent.
* **Abstractive Summarization**: Condenses multi-page documents into key bullet points or executive summaries.

### 4. 🔐 **User Authentication & Profile Management**
* **Secure Registration & Login**: Hashed password storage using `bcrypt`.
* **Password Recovery**: Automated verification dispatches powered by the **SendGrid API**.
* **Profile Dashboard**: User profile preferences and saved transformation logs.

---

## 📁 Repository Directory Structure

```
TextMorph/
├── README.md                 # Technical project documentation
├── LICENSE                   # MIT License
├── run.sh                    # One-command startup script
├── backend/
│   ├── main.py               # FastAPI server application & API routing
│   ├── database.py           # SQLAlchemy engine & session initialization
│   ├── models.py             # Database table schemas (User, Profile)
│   ├── schemas.py            # Pydantic data validation models
│   ├── crud.py               # Database CRUD operations
│   ├── requirements.txt      # Backend Python dependencies
│   └── sql_app.db            # SQLite database file
├── frontend/
│   ├── app.py                # Streamlit entrypoint & page router
│   ├── utils.py              # Utility helper functions
│   ├── requirements.txt      # Frontend Python dependencies
│   ├── libs/                 # Custom UI helper libraries
│   └── pages/                # Streamlit multi-page views (Dashboard, Auth, Profile)
├── database/                 # Migration scripts & schemas
└── tests/                    # Unit testing suite
```

---

## 🚀 Local Installation & Setup

### Prerequisites
* **Python**: `v3.10` or higher
* **SendGrid API Key** (for email dispatches)
* **Google Gemini API Key** (for AI features)

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/Sanjuu516/TextMorph.git
cd TextMorph
```

---

### Step 2: Set Up the Backend Server

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # On macOS/Linux
   # venv\Scripts\activate          # On Windows
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables in `backend/main.py` or `.env`:
   ```env
   SENDER_EMAIL="your-verified-email@domain.com"
   SENDGRID_API_KEY="SG.your_sendgrid_api_key"
   ```

---

### Step 3: Set Up the Frontend Application

1. Open a new terminal and navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```

2. Create and activate a separate Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # On macOS/Linux
   # venv\Scripts\activate          # On Windows
   ```

3. Install frontend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the Gemini API Key:
   Create `.streamlit/secrets.toml` inside `frontend/`:
   ```toml
   GEMINI_API_KEY = "your_google_gemini_api_key_here"
   ```

---

### Step 4: Run the Application

#### Option A: One-Command Start (macOS/Linux)
From the root directory:
```bash
chmod +x run.sh
./run.sh
```

#### Option B: Manual Terminal Launch

1. **Start the FastAPI Backend** (Terminal 1):
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
   *FastAPI server will run at `http://127.0.0.1:8000` with Swagger docs at `http://127.0.0.1:8000/docs`.*

2. **Start the Streamlit Frontend** (Terminal 2):
   ```bash
   streamlit run frontend/app.py
   ```
   *Streamlit dashboard will automatically launch at `http://localhost:8501`.*

---

## 📡 API Endpoint Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/auth/register` | User account registration |
| `POST` | `/auth/login` | Authenticates user & returns token |
| `POST` | `/auth/forgot-password` | Dispatches password reset email via SendGrid |
| `GET` | `/users/me` | Fetches authenticated user profile |
| `POST` | `/analyze` | Computes text readability metrics & grade levels |

---

## 👩‍💻 Author & Acknowledgments

**Sanjana Narni**
* **Role**: Lead Developer (Infosys Springboard Virtual Internship 6.0)
* **GitHub**: [@Sanjuu516](https://github.com/Sanjuu516)
* **LinkedIn**: [sanjananarni516](https://www.linkedin.com/in/sanjananarni516)

Developed under the guidance of **Infosys Springboard Virtual Internship Program 6.0**.

---

## 📄 License

This repository is licensed under the [MIT License](LICENSE).
