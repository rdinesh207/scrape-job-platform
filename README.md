# CareerMatch Platform

CareerMatch is an AI-powered job application copilot that helps candidates discover opportunities, understand fit, and generate high-quality application assets in minutes.

## Product Vision

Most candidates waste time switching between job boards, profile updates, and manual resume tailoring. CareerMatch turns that fragmented process into one guided workflow:

1. Ingest jobs from a tracked URL list.
2. Build a structured applicant profile.
3. Match candidate and jobs with embeddings + vector search.
4. Show fit summary (requirements, strengths, gaps, match score).
5. Generate resume and cover letter drafts for selected jobs.
6. Suggest networking contacts and message drafts for outreach.

## Core Capabilities

- **Job ingestion pipeline** from `job_urls.txt` with structured extraction.
- **Applicant enrichment** from LinkedIn, GitHub, portfolio, and other links.
- **Semantic search + recommendations** using Supabase `pgvector` and RPC.
- **Fit analysis** with match score and requirement gap breakdown.
- **Application generation** for resume and cover letter drafts.
- **Networking assistant** to find relevant people and draft connection messages.

## Tech Stack

- **Backend:** FastAPI (Python)
- **Orchestration:** LangGraph / LangChain
- **Extraction:** ScrapeGraphAI (raw API integration)
- **LLM + Embeddings:** OpenAI
- **Database:** Supabase (Postgres + pgvector + RPC)
- **Frontend:** React + Vite + TypeScript + Tailwind UI

## Product Workflow

1. Sign up / log in.
2. Complete profile once.
3. Ingest jobs from tracked URLs.
4. Browse recommendations and run keyword search.
5. Open a job for fit summary + gap analysis.
6. Generate resume/cover letter.
7. Use suggested networking contacts + outreach messages.

## Demo

- **Web App Demo:** [demos/web app demo.mp4](demos/web%20app%20demo.mp4)
- **Interview Notebook Demo:** [demos/interview prep notebook.mov](demos/interview%20prep%20notebook.mov)

## Local Setup

### Backend

1. `cd backend`
2. Configure `backend/.env`
3. Start API:
   - `uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`

### Frontend

1. `cd frontend`
2. Configure `frontend/.env`
3. Install and run:
   - `npm install`
   - `npm run dev`

## API Highlights

- `POST /jobs/ingest`
- `GET /jobs/search`
- `POST /applicants`
- `GET /applicants/{id}/recommendations`
- `POST /jobs/{job_id}/fit-summary`
- `POST /jobs/{job_id}/generate-docs`
- `POST /jobs/{job_id}/networking`

## Who This Is For

- Job seekers optimizing applications at scale.
- Career coaches supporting candidate preparation.
- Talent products focused on personalized matching and application assistance.
