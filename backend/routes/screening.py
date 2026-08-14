from __future__ import annotations

import threading
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from auth_context import current_user_id
from extensions import db
from models import (
    Candidate,
    CandidateSkill,
    Certification,
    Education,
    Experience,
    Job,
    Project,
    Resume,
    ScreeningResult,
    dumps,
)
from services.ai_service import extract_resume_information, generate_candidate_explanation
from services.ats_analyzer import score_resume_quality
from services.duplicate_detector import find_possible_duplicate
from services.job_analyzer import analyze_job_description
from services.matching_engine import match_candidate
from services.resume_parser import parse_resume
from services.scoring_engine import score_candidate
from utils.file_utils import save_upload, validate_resume_file


screening_bp = Blueprint("screening", __name__)
SCREENING_JOBS: dict[str, dict] = {}
SCREENING_LOCK = threading.Lock()


def current_user_job(job_id: int) -> Job | None:
    return Job.query.filter_by(id=job_id, user_id=current_user_id()).first()


def set_progress(batch_id: str, **updates) -> None:
    with SCREENING_LOCK:
        if batch_id in SCREENING_JOBS:
            SCREENING_JOBS[batch_id].update(updates)


def append_progress(batch_id: str, key: str, value) -> None:
    with SCREENING_LOCK:
        SCREENING_JOBS[batch_id].setdefault(key, []).append(value)


def profile_to_candidate(job_id: int, profile: dict) -> Candidate:
    return Candidate(
        job_id=job_id,
        name=profile.get("name") or "Not Found",
        email=profile.get("email"),
        phone=profile.get("phone"),
        location=profile.get("location"),
        linkedin=profile.get("linkedin"),
        github=profile.get("github"),
        portfolio=profile.get("portfolio"),
        current_role=profile.get("current_role"),
        years_experience=profile.get("years_experience") or 0,
        status="Analyzed",
        structured_json=dumps(profile),
    )


def add_profile_children(candidate: Candidate, profile: dict) -> None:
    for skill in profile.get("skills", []):
        candidate.skills.append(CandidateSkill(name=skill))
    for item in profile.get("education", []):
        candidate.education_items.append(
            Education(
                degree=item.get("degree"),
                institution=item.get("institution"),
                year=item.get("year"),
            )
        )
    for item in profile.get("experience", []):
        candidate.experience_items.append(
            Experience(
                role=item.get("role"),
                company=item.get("company"),
                duration_months=item.get("duration_months") or 0,
            )
        )
    for item in profile.get("projects", []):
        candidate.projects.append(Project(name=item.get("name", "Project"), description=item.get("description", "")))
    for certification in profile.get("certifications", []):
        candidate.certifications.append(Certification(name=certification))


def ensure_job_analysis(job: Job) -> dict:
    if job.analysis:
        return job.analysis
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
    db.session.commit()
    return analysis


def process_batch(app, batch_id: str, job_id: int, saved_files: list[dict]) -> None:
    with app.app_context():
        set_progress(batch_id, status="processing", total=len(saved_files), processed=0, stage="Parsing resumes")
        job = Job.query.get(job_id)
        if not job:
            set_progress(batch_id, status="failed", message="Job not found.")
            return
        analysis = ensure_job_analysis(job)

        success = failed = duplicates = 0
        candidate_ids = []
        for index, saved in enumerate(saved_files, start=1):
            set_progress(batch_id, processed=index - 1, stage=f"Processing {saved['original_filename']}")
            try:
                resume_text = parse_resume(saved["stored_path"])
                profile = extract_resume_information(resume_text)
                duplicate = find_possible_duplicate(job_id, profile, resume_text)

                candidate = profile_to_candidate(job_id, profile)
                add_profile_children(candidate, profile)
                db.session.add(candidate)
                db.session.flush()

                resume = Resume(
                    candidate_id=candidate.id,
                    original_filename=saved["original_filename"],
                    stored_path=saved["stored_path"],
                    file_type=saved["file_type"],
                    file_size=saved["file_size"],
                    file_hash=saved["file_hash"],
                    raw_text=resume_text,
                    parse_status="Parsed",
                )
                db.session.add(resume)

                match_result = match_candidate(analysis, profile, resume_text)
                score = score_candidate(match_result)
                ats = score_resume_quality(profile, resume_text)
                explanation = generate_candidate_explanation(job.title, profile, score, match_result, ats)
                result = ScreeningResult(
                    candidate_id=candidate.id,
                    job_id=job_id,
                    overall_score=score["overall_score"],
                    category=score["category"],
                    recommendation=score["recommendation"],
                    explanation=explanation,
                    component_scores_json=dumps(score["component_scores"]),
                    matched_skills_json=dumps(match_result["matched_skills"]),
                    missing_required_skills_json=dumps(match_result["missing_required_skills"]),
                    missing_preferred_skills_json=dumps(match_result["missing_preferred_skills"]),
                    related_skills_json=dumps(match_result["related_skills"]),
                    ats_score=ats["score"],
                    ats_feedback_json=dumps(ats["checks"] + [{"suggestions": ats["suggestions"]}]),
                    duplicate_of_id=duplicate["candidate_id"] if duplicate else None,
                    duplicate_similarity=duplicate["similarity"] if duplicate else 0,
                )
                db.session.add(result)
                db.session.commit()

                success += 1
                if duplicate:
                    duplicates += 1
                candidate_ids.append(candidate.id)
                append_progress(
                    batch_id,
                    "files",
                    {
                        "filename": saved["original_filename"],
                        "status": "processed",
                        "candidate_id": candidate.id,
                        "duplicate": duplicate,
                    },
                )
            except Exception as exc:
                db.session.rollback()
                failed += 1
                append_progress(
                    batch_id,
                    "files",
                    {"filename": saved["original_filename"], "status": "failed", "error": str(exc)},
                )
            set_progress(
                batch_id,
                processed=index,
                success=success,
                failed=failed,
                duplicates=duplicates,
                candidate_ids=candidate_ids,
            )

        set_progress(batch_id, status="complete", stage="Complete", processed=len(saved_files))


def receive_uploads():
    job_id = request.form.get("job_id", type=int)
    if not job_id:
        return jsonify({"message": "job_id is required."}), 400
    job = current_user_job(job_id)
    if not job:
        return jsonify({"message": "Job not found."}), 404

    files = request.files.getlist("resumes")
    if not files:
        return jsonify({"message": "Select at least one resume."}), 400

    batch_id = uuid4().hex
    batch_dir = Path(current_app.config["UPLOAD_FOLDER"]) / "batches" / batch_id
    saved_files = []
    rejected = []

    for file in files:
        valid, message = validate_resume_file(file, current_app.config["MAX_UPLOAD_MB"])
        if not valid:
            rejected.append({"filename": file.filename, "status": "rejected", "error": message})
            continue
        try:
            saved_files.append(save_upload(file, batch_dir))
        except Exception as exc:
            rejected.append({"filename": file.filename, "status": "failed", "error": str(exc)})

    if not saved_files:
        return jsonify({"message": "No valid resumes were uploaded.", "files": rejected}), 400

    with SCREENING_LOCK:
        SCREENING_JOBS[batch_id] = {
            "batch_id": batch_id,
            "job_id": job_id,
            "status": "queued",
            "stage": "Queued",
            "total": len(saved_files),
            "processed": 0,
            "success": 0,
            "failed": len(rejected),
            "duplicates": 0,
            "files": rejected,
            "candidate_ids": [],
        }

    app = current_app._get_current_object()
    thread = threading.Thread(target=process_batch, args=(app, batch_id, job_id, saved_files), daemon=True)
    thread.start()

    return jsonify({"batch_id": batch_id, "total": len(saved_files), "rejected": rejected}), 202


@screening_bp.post("/upload")
@jwt_required(optional=True)
def upload_resumes():
    return receive_uploads()


@screening_bp.post("/start")
@jwt_required(optional=True)
def start_screening():
    return receive_uploads()


@screening_bp.get("/<batch_id>/status")
@jwt_required(optional=True)
def screening_status(batch_id: str):
    with SCREENING_LOCK:
        data = SCREENING_JOBS.get(batch_id)
    if not data:
        return jsonify({"message": "Batch not found."}), 404
    return jsonify(data)


@screening_bp.get("/<batch_id>/results")
@jwt_required(optional=True)
def screening_results(batch_id: str):
    with SCREENING_LOCK:
        data = SCREENING_JOBS.get(batch_id)
    if not data:
        return jsonify({"message": "Batch not found."}), 404
    candidate_ids = data.get("candidate_ids", [])
    candidates = Candidate.query.filter(Candidate.id.in_(candidate_ids)).all() if candidate_ids else []
    candidates.sort(key=lambda item: item.screening_result.overall_score if item.screening_result else 0, reverse=True)
    return jsonify({"batch": data, "candidates": [candidate.to_dict() for candidate in candidates]})
