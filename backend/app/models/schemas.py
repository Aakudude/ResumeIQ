from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime


class JobDescriptionCreate(BaseModel):
    title: str
    company: Optional[str] = None
    content: str


class JobDescriptionOut(BaseModel):
    id: int
    title: str
    company: Optional[str]
    content: str
    required_skills: List[str]
    preferred_skills: List[str]
    experience_years: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class CandidateOut(BaseModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    filename: str
    extracted_skills: List[str]
    experience_years: Optional[float]
    education: List[Any]
    match_score: Optional[float]
    matched_skills: List[str]
    missing_skills: List[str]
    recommendations: List[str]
    rank: Optional[int]
    job_description_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class MatchRequest(BaseModel):
    candidate_ids: List[int]
    job_description_id: int


class AnalyticsOut(BaseModel):
    total_candidates: int
    average_match_score: float
    top_skills: List[dict]
    most_missing_skills: List[dict]
    score_distribution: List[dict]
    skill_gap_analysis: List[dict]
    rankings: List[dict]
