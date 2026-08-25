# ResearchAI — Multi-Agent Research Platform

ResearchAI is an enterprise-grade AI-powered multi-agent research platform designed for scientists, analysts, academics, and enterprises.

---

## 🏛️ Architecture Overview

The user interacts **only** with the **Mother Agent**. Behind the scenes, the Mother Agent coordinates a hidden fleet of specialized **Child Agents** searching 9+ primary academic, medical, and dataset APIs concurrently. The Mother Agent then aggregates, verifies, deduplicates, ranks, summarizes, and formats the findings into downloadable reports (PDF, DOCX, Markdown, HTML).

```
User
  │ (Chat UI / Streaming SSE)
  ▼
Mother Agent (LangGraph State Machine)
  │
  ├──► Planner (Intent Analysis & Domain Routing)
  │
  ├──► Task Manager & Parallel Dispatch
  │     ├──► Academic Agent    (OpenAlex, Crossref, Semantic Scholar, arXiv)
  │     ├──► Medical Agent     (PubMed, PMC, NCBI E-utilities)
  │     ├──► Web & News Agent  (Brave Search API + Trusted Domain Filters)
  │     ├──► Books Agent       (Google Books API, Open Library)
  │     ├──► Statistics Agent  (World Bank Data API, UN Datasets)
  │     └──► Patent & Gov      (Google Patents, Europa, Gov archives)
  │
  ├──► Aggregator
  ├──► Verifier (Confidence & Reliability Scoring)
  ├──► Deduplication (DOI & Title Canonicalization)
  ├──► Ranker (Quality & Citation-Weighted Sorting)
  ├──► Summarizer (Synthesis & Contradiction Detection)
  ├──► Citation Generator (APA 7th, MLA 9th, Chicago formats)
  └──► Report Generator (PDF, DOCX, Markdown, HTML)
```

---

## 🚀 Quick Start with Docker Compose

1. Clone or navigate to the repository directory:
   ```bash
   cd researchai
   ```

2. Configure backend environment:
   ```bash
   cp backend/.env.example backend/.env
   # Add your GOOGLE_API_KEY (Gemini) or other keys to backend/.env
   ```

3. Configure frontend environment:
   ```bash
   cp frontend/.env.example frontend/.env.local
   ```

4. Start all services (PostgreSQL, Redis, Celery Worker, FastAPI Backend, Next.js Frontend):
   ```bash
   docker-compose up --build
   ```

5. Access the applications:
   - **Frontend App:** [http://localhost:3000](http://localhost:3000)
   - **Backend API Docs (Swagger):** [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
   - **Backend Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 💻 Local Development Setup

### Backend (Python 3.12 / FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migrations and start server
uvicorn app.main:app --reload --port 8000
```

### Frontend (Next.js 14 / TypeScript)
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing

### Backend Unit & Integration Tests
```bash
cd backend
pytest tests/ -v
```

---

## 📦 Project Structure

```
researchai/
├── docker-compose.yml
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Endpoints (auth, chat, reports, workspace)
│   │   ├── agents/          # Mother Agent (LangGraph) & Child Agents
│   │   ├── integrations/    # API clients (OpenAlex, PubMed, arXiv, etc.)
│   │   ├── core/            # Config, database, security, redis, logging
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── services/        # Business logic & report generation
│   │   └── workers/         # Celery background tasks
│   ├── tests/               # Unit & integration test suites
│   ├── Dockerfile
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── app/             # Next.js App Router (dashboard, auth, chat, reports)
    │   ├── components/      # Chat, CitationCard, ReportPreview, Sidebar
    │   ├── stores/          # Zustand state management
    │   ├── lib/             # API client & utils
    │   └── styles/          # Tailwind CSS with ChatGPT minimal white aesthetic
    ├── Dockerfile
    └── package.json
```
