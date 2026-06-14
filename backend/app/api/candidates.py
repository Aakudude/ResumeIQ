import os
import shutil
import uuid
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models.database import get_db, Candidate
from app.models.schemas import CandidateOut
from app.services.pdf_service import extract_text_from_pdf, validate_pdf
from app.services.nlp_service import (
    extract_skills, extract_experience_years, extract_education,
    extract_contact_info, calculate_match_score, generate_recommendations
)

router = APIRouter(prefix="/candidates", tags=["candidates"])
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=List[CandidateOut])
async def upload_resumes(
    files: List[UploadFile] = File(...),
    job_description_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    results = []
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(400, f"{file.filename} is not a PDF file")

        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        if not validate_pdf(file_path):
            os.remove(file_path)
            raise HTTPException(400, f"{file.filename} is not a valid PDF")

        raw_text = extract_text_from_pdf(file_path)
        contact = extract_contact_info(raw_text)
        skills = extract_skills(raw_text)
        exp = extract_experience_years(raw_text)
        edu = extract_education(raw_text)

        candidate = Candidate(
            name=contact["name"],
            email=contact["email"],
            phone=contact["phone"],
            filename=file.filename,
            file_path=file_path,
            raw_text=raw_text,
            extracted_skills=skills,
            experience_years=exp,
            education=edu,
            job_description_id=job_description_id
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        results.append(candidate)

    return results


@router.get("/", response_model=List[CandidateOut])
def list_candidates(
    jd_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Candidate)
    if jd_id:
        q = q.filter(Candidate.job_description_id == jd_id)
    return q.order_by(Candidate.rank.asc().nullslast(), Candidate.match_score.desc().nullslast()).all()


@router.get("/{candidate_id}", response_model=CandidateOut)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(404, "Candidate not found")
    return c


@router.delete("/{candidate_id}")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(404, "Candidate not found")
    if os.path.exists(c.file_path):
        os.remove(c.file_path)
    db.delete(c)
    db.commit()
    return {"message": "Deleted"}
