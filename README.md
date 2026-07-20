# AgentHive 🚀

> **Multi-Agent AI Sprint Planning Assistant**

AgentHive is a production-style SaaS platform designed to help software development teams automatically generate complete, balanced sprint plans from raw Software Requirement Specifications (SRS) documents. By coordinating a pipeline of 5 specialized CrewAI agents, AgentHive extracts modules, creates engineering tasks, maps roles and skills, groups sprints, and conducts a complete project risk analysis.

---

## Key Features

- **JWT Authentication**: Secure user registration, logins, and session persistence.
- **Project Workspaces**: Initialize isolated workspaces to track team members, technical skills, requirement specs, and task boards.
- **SRS Document Parser**: Integrated file uploader extracting text content from PDF, DOCX, and TXT requirements.
- **Collaborative Multi-Agent Flow**: Uses CrewAI to coordinate 5 distinct agents passing structured outputs sequentially:
  1. **Requirement Analysis Agent**: Business Analyst extracting modules and functional requirements.
  2. **Task Breakdown Agent**: Technical Lead generating task tickets (Frontend/Backend/Database/Testing/DevOps).
  3. **Skill Matching Agent**: Engineering Manager mapping tasks to team skills and experience levels.
  4. **Sprint Planning Agent**: Scrum Master packaging tasks into balanced Sprint columns.
  5. **Risk Analysis Agent**: Solutions Risk Auditor.
- **SRS Requirement Upload Module**: Upload and automatically extract plain text from PDF, DOCX, and TXT requirement files with metadata tracking and error validation.
- **AI Control Center**: A visual telemetry dashboard displaying status indicators, execution times, logs, and input/output JSON schemas for each active agent card.
- **Kanban Sprint Board & Charts**: Interactive sprint columns rendering assignments, integrated with Recharts widgets illustrating category divisions and developer hour workloads.

---

## Technology Stack

- **Backend**: FastAPI, Python 3.11, SQLAlchemy (declarative models), SQLite (default local DB) / PostgreSQL, JWT, Pydantic, pytest.
- **AI Orchestration**: CrewAI, LangChain, Google Gemini API (preferred free tier) / Groq API.
- **Frontend**: React, TypeScript, Tailwind CSS v4 + PostCSS, Redux Toolkit, React Router, Axios, React Hook Form, Recharts, Lucide Icons.

---

## Repository Structure

```
AgentHive/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/             # HTTP endpoints & dependencies
│   │   ├── core/            # Config, security, database session
│   │   ├── models/          # SQLAlchemy SQL models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── services/        # Business logic & parsers
│   │   ├── ai/              # CrewAI Agents and Tasks
│   │   └── main.py          # FastAPI Entrypoint
│   ├── tests/               # Pytest integration tests
│   ├── requirements.txt     # Python requirements
│   └── .env                 # Environment secrets template
├── frontend/                 # React Application
│   ├── src/
│   │   ├── components/      # Global Layout and Protected Routes
│   │   ├── features/        # Feature pages (Auth, Projects, Team, AI-Center, Dashboard)
│   │   ├── store/           # Redux state slices
│   │   ├── services/        # Axios API Client
│   │   ├── App.tsx          # Root routes aggregator
│   │   └── index.css        # Global CSS stylesheet (Tailwind v4)
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

---

## Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Either a **Google Gemini API Key** (Free) or a **Groq API Key** (Free).

### 1. Backend Setup
1. Open a terminal and navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the `.env` template or edit the existing `backend/.env` file:
   - Provide your `GEMINI_API_KEY` (from [Google AI Studio](https://aistudio.google.com/)) or `GROQ_API_KEY`.
   - Set `LLM_PROVIDER="google"` (or `"groq"`).
5. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend API will boot, automatically initialize database tables, pre-populate default developer skills, and run on [http://localhost:8000](http://localhost:8000). You can inspect the Swagger docs at [http://localhost:8000/docs](http://localhost:8000/docs).

### 2. Frontend Setup
1. In a new terminal, navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the Vite React development server:
   ```bash
   npm run dev
   ```
   The frontend will compile and start on [http://localhost:5173](http://localhost:5173).

---

## Running Automated Tests

To run the full suite of integration tests covering registration, JWT auth, and project CRUD operations:
1. In the `backend` folder, with virtual environment activated:
   ```bash
   python -m pytest
   ```
