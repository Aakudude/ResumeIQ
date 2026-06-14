# 🧠 ResumeIQ — AI-Powered Resume Analytics Platform

A production-ready recruitment intelligence platform for analyzing resumes against job descriptions.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + TypeScript + Tailwind CSS + Recharts |
| Backend | FastAPI (Python) |
| Database | SQLite (via SQLAlchemy) |
| NLP | Regex + Keyword NLP engine (200+ skills) |
| PDF | pdfplumber |
| Reports | ReportLab (PDF) + CSV |

## Quick Start

```bash
chmod +x start.sh
./start.sh
```

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs

## Manual Start

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

## Features

- ✅ Upload 1-50 PDF resumes at once
- ✅ Create job descriptions with auto skill extraction
- ✅ AI match scoring (required skills 70%, preferred 20%, experience 10%)
- ✅ Candidate rankings with medal podium
- ✅ Skill gap analysis per candidate and across pool
- ✅ AI-generated recommendations per candidate
- ✅ CSV and PDF export reports
- ✅ Interactive analytics dashboard
- ✅ Dark glassmorphism SaaS UI

## Project Structure

```
resumeiq/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers
│   │   ├── models/       # SQLAlchemy + Pydantic schemas
│   │   └── services/     # NLP, PDF, Analytics, Reports
│   ├── main.py
│   ├── requirements.txt
│   └── uploads/          # Uploaded PDFs stored here
├── frontend/
│   └── src/
│       ├── components/   # UI + Layout components
│       ├── pages/        # 8 app pages
│       └── lib/api.ts    # Axios API client
└── start.sh
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/candidates/upload` | Upload PDF resumes |
| GET | `/api/v1/candidates/` | List all candidates |
| GET | `/api/v1/candidates/{id}` | Get candidate detail |
| POST | `/api/v1/jd/` | Create job description |
| GET | `/api/v1/jd/` | List job descriptions |
| POST | `/api/v1/match` | Run matching + ranking |
| GET | `/api/v1/analytics` | Get analytics data |
| GET | `/api/v1/reports/csv` | Export CSV report |
| GET | `/api/v1/reports/pdf` | Export PDF report |
