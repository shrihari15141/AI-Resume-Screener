from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from auth_context import current_user_id
from extensions import db
from models import Candidate, Job


candidates_bp = Blueprint("candidates", __name__)


def user_job_ids() -> list[int]:
    return [job.id for job in Job.query.filter_by(user_id=current_user_id()).all()]


def user_candidate(candidate_id: int) -> Candidate | None:
    return Candidate.query.filter(Candidate.id == candidate_id, Candidate.job_id.in_(user_job_ids())).first()


@candidates_bp.get("")
@jwt_required(optional=True)
def list_candidates():
    query = Candidate.query.filter(Candidate.job_id.in_(user_job_ids()))
    job_id = request.args.get("job_id", type=int)
    status = request.args.get("status")
    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", "score")

    if job_id:
        query = query.filter_by(job_id=job_id)
    if status:
        query = query.filter_by(status=status)
    if search:
        like = f"%{search}%"
        query = query.filter(Candidate.name.ilike(like) | Candidate.email.ilike(like))

    candidates = query.all()
    if sort == "name":
        candidates.sort(key=lambda item: (item.name or "").lower())
    elif sort == "experience":
        candidates.sort(key=lambda item: item.years_experience or 0, reverse=True)
    elif sort == "status":
        candidates.sort(key=lambda item: item.status)
    else:
        candidates.sort(
            key=lambda item: item.screening_result.overall_score if item.screening_result else -1,
            reverse=True,
        )
    return jsonify({"candidates": [candidate.to_dict() for candidate in candidates]})


@candidates_bp.get("/<int:candidate_id>")
@jwt_required(optional=True)
def get_candidate(candidate_id: int):
    candidate = user_candidate(candidate_id)
    if not candidate:
        return jsonify({"message": "Candidate not found."}), 404
    return jsonify({"candidate": candidate.to_dict(detail=True)})


@candidates_bp.put("/<int:candidate_id>/status")
@jwt_required(optional=True)
def update_status(candidate_id: int):
    candidate = user_candidate(candidate_id)
    if not candidate:
        return jsonify({"message": "Candidate not found."}), 404
    status = (request.get_json() or {}).get("status")
    allowed = {"New", "Analyzed", "Shortlisted", "Under Review", "Rejected", "Interview", "Hired"}
    if status not in allowed:
        return jsonify({"message": "Invalid candidate status."}), 400
    candidate.status = status
    db.session.commit()
    return jsonify({"candidate": candidate.to_dict(detail=True)})


@candidates_bp.post("/compare")
@jwt_required(optional=True)
def compare_candidates():
    ids = (request.get_json() or {}).get("candidate_ids", [])
    if not isinstance(ids, list) or not 2 <= len(ids) <= 5:
        return jsonify({"message": "Select between 2 and 5 candidates."}), 400

    candidates = Candidate.query.filter(Candidate.id.in_(ids), Candidate.job_id.in_(user_job_ids())).all()
    if len(candidates) != len(set(ids)):
        return jsonify({"message": "One or more candidates were not found."}), 404

    skill_set = []
    for candidate in candidates:
        for skill in candidate.job.required_skills + candidate.job.preferred_skills:
            if skill not in skill_set:
                skill_set.append(skill)

    comparison = []
    for candidate in candidates:
        candidate_skills = {skill.name.lower() for skill in candidate.skills}
        comparison.append(
            {
                "candidate": candidate.to_dict(),
                "skills": {
                    skill: any(skill.lower() in item or item in skill.lower() for item in candidate_skills)
                    for skill in skill_set
                },
                "component_scores": candidate.screening_result.to_dict()["component_scores"]
                if candidate.screening_result
                else {},
            }
        )
    return jsonify({"skills": skill_set, "comparison": comparison})
