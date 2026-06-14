from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.models.database import get_db, Candidate, JobDescription
from app.models.schemas import MatchRequest
from app.services.nlp_service import calculate_match_score, generate_recommendations
from app.services.analytics_service import compute_analytics
from app.services.report_service import generate_csv_report, generate_pdf_report

router = APIRouter(tags=["matching"])


@router.post("/match")
def match_candidates(payload: MatchRequest, db: Session = Depends(get_db)):
    jd = db.query(JobDescription).filter(JobDescription.id == payload.job_description_id).first()
    if not jd:
        raise HTTPException(404, "Job description not found")

    results = []
    for cid in payload.candidate_ids:
        c = db.query(Candidate).filter(Candidate.id == cid).first()
        if not c:
            continue

        score, matched, missing = calculate_match_score(
            c.extracted_skills or [],
            jd.required_skills or [],
            jd.preferred_skills or [],
            c.experience_years,
            jd.experience_years
        )
        recs = generate_recommendations(c.extracted_skills or [], missing, score, c.name)

        c.job_description_id = jd.id
        c.match_score = score
        c.matched_skills = matched
        c.missing_skills = missing
        c.recommendations = recs
        db.commit()
        results.append({"id": cid, "score": score})

    # Re-rank all candidates for this JD
    all_candidates = db.query(Candidate).filter(
        Candidate.job_description_id == payload.job_description_id,
        Candidate.match_score.isnot(None)
    ).order_by(Candidate.match_score.desc()).all()

    for i, c in enumerate(all_candidates):
        c.rank = i + 1
    db.commit()

    return {"matched": len(results), "results": results}


@router.get("/analytics")
def get_analytics(jd_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    return compute_analytics(db, jd_id)


@router.get("/reports/csv")
def export_csv(jd_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    q = db.query(Candidate)
    if jd_id:
        q = q.filter(Candidate.job_description_id == jd_id)
    candidates = q.order_by(Candidate.rank).all()

    jd_title = ""
    if jd_id:
        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        if jd:
            jd_title = jd.title

    csv_bytes = generate_csv_report(candidates, jd_title)
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=resumeiq_report.csv"}
    )


@router.get("/reports/pdf")
def export_pdf(jd_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    q = db.query(Candidate)
    if jd_id:
        q = q.filter(Candidate.job_description_id == jd_id)
    candidates = q.order_by(Candidate.rank).all()

    jd_title, jd_company = "", ""
    if jd_id:
        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        if jd:
            jd_title = jd.title
            jd_company = jd.company or ""

    pdf_bytes = generate_pdf_report(candidates, jd_title, jd_company)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=resumeiq_report.pdf"}
    )
