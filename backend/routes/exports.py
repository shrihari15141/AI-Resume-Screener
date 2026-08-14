from __future__ import annotations

import csv
import io

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import jwt_required

from auth_context import current_user_id
from models import Candidate, Job


exports_bp = Blueprint("exports", __name__)


def export_candidates() -> list[Candidate]:
    job_ids = [job.id for job in Job.query.filter_by(user_id=current_user_id()).all()]
    query = Candidate.query.filter(Candidate.job_id.in_(job_ids))
    job_id = request.args.get("job_id", type=int)
    if job_id:
        query = query.filter_by(job_id=job_id)
    candidates = query.all()
    candidates.sort(key=lambda item: item.screening_result.overall_score if item.screening_result else 0, reverse=True)
    return candidates


@exports_bp.get("/csv")
@jwt_required(optional=True)
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Rank",
            "Candidate Name",
            "Email",
            "Phone",
            "Overall Score",
            "Required Skills Score",
            "Experience Score",
            "Education Score",
            "Projects Score",
            "Preferred Skills Score",
            "Certification Score",
            "Semantic Score",
            "Status",
            "Recommendation",
        ]
    )
    for rank, candidate in enumerate(export_candidates(), start=1):
        result = candidate.screening_result
        components = result.to_dict()["component_scores"] if result else {}
        writer.writerow(
            [
                rank,
                candidate.name,
                candidate.email,
                candidate.phone,
                result.overall_score if result else "",
                components.get("required_skills", ""),
                components.get("experience", ""),
                components.get("education", ""),
                components.get("projects", ""),
                components.get("preferred_skills", ""),
                components.get("certifications", ""),
                components.get("semantic_similarity", ""),
                candidate.status,
                result.recommendation if result else "",
            ]
        )
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=resume_screening_results.csv"},
    )


@exports_bp.get("/json")
@jwt_required(optional=True)
def export_json():
    return jsonify({"candidates": [candidate.to_dict(detail=True) for candidate in export_candidates()]})
