from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db, JobDescription
from app.models.schemas import JobDescriptionCreate, JobDescriptionOut
from app.services.nlp_service import parse_jd_skills

router = APIRouter(prefix="/jd", tags=["job-descriptions"])


@router.post("/", response_model=JobDescriptionOut)
def create_jd(payload: JobDescriptionCreate, db: Session = Depends(get_db)):
    required_skills, preferred_skills, exp = parse_jd_skills(payload.content)
    jd = JobDescription(
        title=payload.title,
        company=payload.company,
        content=payload.content,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        experience_years=exp
    )
    db.add(jd)
    db.commit()
    db.refresh(jd)
    return jd


@router.get("/", response_model=List[JobDescriptionOut])
def list_jds(db: Session = Depends(get_db)):
    return db.query(JobDescription).order_by(JobDescription.created_at.desc()).all()


@router.get("/{jd_id}", response_model=JobDescriptionOut)
def get_jd(jd_id: int, db: Session = Depends(get_db)):
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
    if not jd:
        raise HTTPException(404, "Job description not found")
    return jd


@router.delete("/{jd_id}")
def delete_jd(jd_id: int, db: Session = Depends(get_db)):
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
    if not jd:
        raise HTTPException(404, "Job description not found")
    db.delete(jd)
    db.commit()
    return {"message": "Deleted"}
