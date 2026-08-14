from __future__ import annotations

from collections import Counter, defaultdict

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from auth_context import current_user_id
from models import Candidate, CandidateSkill, Job


reports_bp = Blueprint("reports", __name__)


def current_jobs() -> list[Job]:
    return Job.query.filter_by(user_id=current_user_id()).all()


@reports_bp.get("")
@jwt_required(optional=True)
def reports():
    jobs = current_jobs()
    job_ids = [job.id for job in jobs]
    candidates = Candidate.query.filter(Candidate.job_id.in_(job_ids)).all() if job_ids else []
    scores = [candidate.screening_result.overall_score for candidate in candidates if candidate.screening_result]

    distribution = {"90-100": 0, "80-89": 0, "70-79": 0, "60-69": 0, "<60": 0}
    for score in scores:
        if score >= 90:
            distribution["90-100"] += 1
        elif score >= 80:
            distribution["80-89"] += 1
        elif score >= 70:
            distribution["70-79"] += 1
        elif score >= 60:
            distribution["60-69"] += 1
        else:
            distribution["<60"] += 1

    skill_counts = Counter()
    missing_counts = Counter()
    for candidate in candidates:
        for skill in candidate.skills:
            skill_counts[skill.name] += 1
        if candidate.screening_result:
            for skill in candidate.screening_result.to_dict()["missing_required_skills"]:
                missing_counts[skill] += 1

    status_counts = Counter(candidate.status for candidate in candidates)
    job_stats = []
    for job in jobs:
        job_candidates = job.candidates
        job_scores = [
            candidate.screening_result.overall_score
            for candidate in job_candidates
            if candidate.screening_result
        ]
        job_stats.append(
            {
                "job": job.title,
                "job_id": job.id,
                "candidates": len(job_candidates),
                "average_score": round(sum(job_scores) / len(job_scores), 2) if job_scores else 0,
                "shortlisted": sum(1 for candidate in job_candidates if candidate.status == "Shortlisted"),
                "rejected": sum(1 for candidate in job_candidates if candidate.status == "Rejected"),
                "interview": sum(1 for candidate in job_candidates if candidate.status == "Interview"),
            }
        )

    recent = sorted(candidates, key=lambda item: item.created_at, reverse=True)[:8]
    return jsonify(
        {
            "summary": {
                "active_jobs": sum(1 for job in jobs if job.status == "Active"),
                "total_resumes": len(candidates),
                "total_candidates": len(candidates),
                "shortlisted": status_counts.get("Shortlisted", 0),
                "under_review": status_counts.get("Under Review", 0),
                "rejected": status_counts.get("Rejected", 0),
                "average_match_score": round(sum(scores) / len(scores), 2) if scores else 0,
            },
            "distribution": distribution,
            "common_skills": [{"skill": skill, "count": count} for skill, count in skill_counts.most_common(12)],
            "missing_skills": [{"skill": skill, "count": count} for skill, count in missing_counts.most_common(12)],
            "job_stats": job_stats,
            "recent_candidates": [candidate.to_dict() for candidate in recent],
        }
    )
