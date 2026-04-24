#  AI-Powered CRM — HCP Interaction Module

> A pharmaceutical field rep tool to log and manage doctor interactions using AI — built with React, FastAPI, LangGraph, and Groq.

---

## 📌 Project Overview

Pharmaceutical field representatives visit doctors (Healthcare Professionals) daily and need to record those interactions. This CRM module lets them log visits in two ways:

- **📝 Structured Form** — fill in doctor name, date, products discussed, notes, and next steps
- **🤖 AI Chat** — type naturally and the LangGraph agent extracts, saves, and manages everything automatically

---

##  Architecture

```
React Frontend (localhost:3000)
         ↕  HTTP via Axios
FastAPI Backend (localhost:8000)
         ↕
LangGraph ReAct Agent
         ↕                    ↕
Groq LLM                PostgreSQL Database
(llama-3.3-70b-versatile)   (hcps + interactions)
```

---

## 🤖 LangGraph AI Tools (5 Total)

| # | Tool | What It Does |
|---|------|-------------|
| 1 | `log_interaction` | Saves a new HCP meeting to the database |
| 2 | `edit_interaction` | Updates an existing interaction by ID |
| 3 | `get_hcp_profile` | Fetches a doctor's full profile and history |
| 4 | `summarize_interaction` | Generates an AI summary of meeting notes |
| 5 | `schedule_followup` | Sets a follow-up date for an HCP |

---

##  Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Redux Toolkit, React Router v6 |
| Backend | FastAPI, Python 3.14, Uvicorn |
| AI Agent | LangGraph 1.1.9, LangChain, Groq API |
| LLM Model | `llama-3.3-70b-versatile` via Groq |
| Database | PostgreSQL 18, SQLAlchemy ORM |
| HTTP Client | Axios |

> **Note:** The assignment specified `gemma2-9b-it` which was decommissioned by Groq. Switched to `llama-3.3-70b-versatile` as the recommended replacement.

---

## 📁 Project Structure

```
ai-crm-hcp/
├── frontend/                        # React application
│   └── src/
│       ├── components/
│       │   ├── Navbar.jsx           # Navigation bar
│       │   ├── LogInteractionForm.jsx  # Form-based logging
│       │   ├── ChatInterface.jsx    # AI chat interface
│       │   └── InteractionHistory.jsx  # Past interactions view
│       └── store/
│           ├── index.js             # Redux store
│           └── interactionSlice.js  # Redux state + API calls
│
└── backend/                         # FastAPI application
    ├── agent/
    │   ├── graph.py                 # LangGraph ReAct agent
    │   └── tools.py                 # 5 LangGraph tools
    ├── models/
    │   └── interaction.py           # SQLAlchemy DB models
    ├── routers/
    │   ├── hcps.py                  # HCP API endpoints
    │   └── interactions.py          # Interaction + Chat endpoints
    ├── database.py                  # DB connection setup
    ├── main.py                      # FastAPI entry point
    └── requirements.txt             # Python dependencies
```

---

##  Getting Started

### Prerequisites
- Node.js v18+
- Python 3.11+
- PostgreSQL 18
- Groq API Key — free at [console.groq.com](https://console.groq.com)

---

### 1. Database Setup

```sql
-- In PostgreSQL (psql)
CREATE DATABASE crm_hcp;
```

Tables are auto-created when the backend starts.

---

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` folder:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/crm_hcp
GROQ_API_KEY=your_groq_api_key_here
```

Start the backend:

```bash
uvicorn main:app --reload
```

Backend runs at **http://localhost:8000**
API docs at **http://localhost:8000/docs**

---

### 3. Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs at **http://localhost:3000**

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/hcps/` | Get all Healthcare Professionals |
| `POST` | `/hcps/` | Create a new HCP |
| `GET` | `/hcps/{id}` | Get a specific HCP |
| `GET` | `/interactions/` | Get all interactions |
| `POST` | `/interactions/` | Log new interaction via form |
| `PUT` | `/interactions/{id}` | Edit an existing interaction |
| `POST` | `/interactions/chat/message` | Send message to AI agent |

---

## 💬 Example AI Chat Prompts

```
"Get me the profile of Dr. Arjun Sharma"
"Log a visit with Dr. Priya Nair on 2026-04-24, discussed Metformin 500mg"
"Schedule a follow-up with Dr. Sharma for 2026-05-01"
"Summarize interaction number 1"
"Edit interaction 2, update next steps to send sample pack"
```

---

## 🖥️ Screenshots

### Log Interaction Form
> Structured form for field reps to manually log doctor visits

### AI Chat Interface  
> Natural language interface powered by LangGraph + Groq

### Interaction History
> View all past logged interactions in card format

---

## 🎥 Demo Video
[Link to walkthrough video — coming soon]

---

## 👤 Author

**Shashwath**
Built as part of a technical assessment for a Life Sciences Supply Chain platform.

---

## 📄 License
MIT
