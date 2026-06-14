from typing import List, Dict, Any, Optional
from collections import Counter
from sqlalchemy.orm import Session
from app.models.database import Candidate, JobDescription


def compute_analytics(db: Session, jd_id: Optional[int] = None) -> Dict[str, Any]:

    query = db.query(Candidate)
    if jd_id:
        query = query.filter(Candidate.job_description_id == jd_id)

    candidates = query.all()

    if not candidates:
        return {
            "total_candidates": 0,
            "average_match_score": 0,
            "top_skills": [],
            "most_missing_skills": [],
            "score_distribution": [],
            "skill_gap_analysis": [],
            "rankings": []
        }

    # Basic stats
    scores = [c.match_score for c in candidates if c.match_score is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0

    # Top skills across all candidates
    all_skills = []
    for c in candidates:
        all_skills.extend(c.extracted_skills or [])
    skill_counts = Counter(all_skills)
    top_skills = [{"skill": k, "count": v} for k, v in skill_counts.most_common(15)]

    # Most missing skills
    all_missing = []
    for c in candidates:
        all_missing.extend(c.missing_skills or [])
    missing_counts = Counter(all_missing)
    most_missing = [{"skill": k, "count": v} for k, v in missing_counts.most_common(10)]

    # Score distribution buckets
    buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    for score in scores:
        if score <= 20:
            buckets["0-20"] += 1
        elif score <= 40:
            buckets["21-40"] += 1
        elif score <= 60:
            buckets["41-60"] += 1
        elif score <= 80:
            buckets["61-80"] += 1
        else:
            buckets["81-100"] += 1
    score_distribution = [{"range": k, "count": v} for k, v in buckets.items()]

    # Skill gap: for each required skill, how many candidates have it
    if jd_id:
        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        if jd and jd.required_skills:
            gap_data = []
            for skill in jd.required_skills:
                have = sum(1 for c in candidates if skill in (c.extracted_skills or []))
                gap_data.append({
                    "skill": skill,
                    "candidates_with": have,
                    "candidates_without": len(candidates) - have,
                    "coverage_pct": round(have / len(candidates) * 100, 1)
                })
            skill_gap_analysis = sorted(gap_data, key=lambda x: x["coverage_pct"])[:12]
        else:
            skill_gap_analysis = []
    else:
        skill_gap_analysis = []

    # Rankings
    ranked = sorted(
        [c for c in candidates if c.match_score is not None],
        key=lambda x: x.match_score,
        reverse=True
    )
    rankings = [
        {
            "rank": i + 1,
            "id": c.id,
            "name": c.name,
            "score": c.match_score,
            "matched_skills": len(c.matched_skills or []),
            "missing_skills": len(c.missing_skills or []),
        }
        for i, c in enumerate(ranked)
    ]

    return {
        "total_candidates": len(candidates),
        "average_match_score": avg_score,
        "top_skills": top_skills,
        "most_missing_skills": most_missing,
        "score_distribution": score_distribution,
        "skill_gap_analysis": skill_gap_analysis,
        "rankings": rankings
    }
