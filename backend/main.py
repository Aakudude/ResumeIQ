from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.database import create_tables
from app.api import candidates, jd, matching

app = FastAPI(
    title="ResumeIQ API",
    description="AI-powered Resume Analytics & Job Description Matching",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(candidates.router, prefix="/api/v1")
app.include_router(jd.router, prefix="/api/v1")
app.include_router(matching.router, prefix="/api/v1")


@app.on_event("startup")
def startup():
    create_tables()


@app.get("/health")
def health():
    return {"status": "ok", "service": "ResumeIQ API"}
