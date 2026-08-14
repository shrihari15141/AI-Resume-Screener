from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from auth_context import current_user_id
from extensions import db
from models import Job, dumps
from services.job_analyzer import analyze_job_description, parse_experience
from utils.validators import JobPayload


jobs_bp = Blueprint("jobs", __name__)


def get_user_job(job_id: int) -> Job | None:
    return Job.query.filter_by(id=job_id, user_id=current_user_id()).first()


def apply_job_payload(job: Job, payload: dict) -> None:
    analysis = analyze_job_description(payload)
    experience = analysis["experience"]
    job.title = payload["title"]
    job.description = payload["description"]
    job.required_skills_json = dumps(analysis["required_skills"])
    job.preferred_skills_json = dumps(analysis["preferred_skills"])
    job.education_json = dumps(analysis["education"])
    job.experience_min = experience.get("minimum") or 0
    job.experience_max = experience.get("maximum")
    job.certifications_json = dumps(analysis["certifications"])
    job.location = payload.get("location", "")
    job.employment_type = payload.get("employment_type", "")
    job.analysis_json = dumps(analysis)


@jobs_bp.get("")
@jwt_required(optional=True)
def list_jobs():
    jobs = Job.query.filter_by(user_id=current_user_id()).order_by(Job.created_at.desc()).all()
    return jsonify({"jobs": [job.to_dict() for job in jobs]})


@jobs_bp.post("")
@jwt_required(optional=True)
def create_job():
    try:
        payload = JobPayload.model_validate(request.get_json() or {}).model_dump()
    except ValidationError as exc:
        return jsonify({"message": "Invalid job details.", "errors": exc.errors()}), 400

    job = Job(user_id=current_user_id(), title=payload["title"], description=payload["description"])
    apply_job_payload(job, payload)
    db.session.add(job)
    db.session.commit()
    return jsonify({"job": job.to_dict()}), 201


@jobs_bp.get("/<int:job_id>")
@jwt_required(optional=True)
def get_job(job_id: int):
    job = get_user_job(job_id)
    if not job:
        return jsonify({"message": "Job not found."}), 404
    return jsonify({"job": job.to_dict(), "candidates": [c.to_dict() for c in job.candidates]})


@jobs_bp.put("/<int:job_id>")
@jwt_required(optional=True)
def update_job(job_id: int):
    job = get_user_job(job_id)
    if not job:
        return jsonify({"message": "Job not found."}), 404
    existing = job.to_dict(include_counts=False)
    incoming = request.get_json() or {}
    merged = {**existing, **incoming}
    if "experience" not in merged:
        merged["experience"] = f"{job.experience_min or 0}-{job.experience_max or job.experience_min or 0} years"
    try:
        payload = JobPayload.model_validate(merged).model_dump()
    except ValidationError as exc:
        return jsonify({"message": "Invalid job details.", "errors": exc.errors()}), 400
    apply_job_payload(job, payload)
    db.session.commit()
    return jsonify({"job": job.to_dict()})


@jobs_bp.delete("/<int:job_id>")
@jwt_required(optional=True)
def delete_job(job_id: int):
    job = get_user_job(job_id)
    if not job:
        return jsonify({"message": "Job not found."}), 404
    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Job deleted."})


@jobs_bp.post("/<int:job_id>/close")
@jwt_required(optional=True)
def close_job(job_id: int):
    job = get_user_job(job_id)
    if not job:
        return jsonify({"message": "Job not found."}), 404
    job.status = "Closed"
    db.session.commit()
    return jsonify({"job": job.to_dict()})


@jobs_bp.post("/<int:job_id>/analyze")
@jwt_required(optional=True)
def analyze_job(job_id: int):
    job = get_user_job(job_id)
    if not job:
        return jsonify({"message": "Job not found."}), 404
    payload = {
        "title": job.title,
        "description": job.description,
        "required_skills": job.required_skills,
        "preferred_skills": job.preferred_skills,
        "education": job.education,
        "experience": f"{job.experience_min or 0}-{job.experience_max or ''} years",
        "certifications": job.certifications,
        "location": job.location,
        "employment_type": job.employment_type,
    }
    analysis = analyze_job_description(payload)
    job.analysis_json = dumps(analysis)
    parsed_experience = parse_experience(payload["experience"], job.description)
    job.experience_min = parsed_experience.get("minimum") or 0
    job.experience_max = parsed_experience.get("maximum")
    db.session.commit()
    return jsonify({"analysis": analysis, "job": job.to_dict()})
