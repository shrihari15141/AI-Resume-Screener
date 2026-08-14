from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


def dumps(value: Any) -> str:
    return json.dumps(value or [], ensure_ascii=False)


def loads(value: str | None, default: Any = None) -> Any:
    if not value:
        return [] if default is None else default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return [] if default is None else default


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    jobs = db.relationship("Job", backref="user", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills_json = db.Column(db.Text, default="[]")
    preferred_skills_json = db.Column(db.Text, default="[]")
    education_json = db.Column(db.Text, default="[]")
    experience_min = db.Column(db.Float, default=0)
    experience_max = db.Column(db.Float, nullable=True)
    certifications_json = db.Column(db.Text, default="[]")
    location = db.Column(db.String(255), default="")
    employment_type = db.Column(db.String(80), default="")
    status = db.Column(db.String(50), default="Active", nullable=False)
    analysis_json = db.Column(db.Text, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidates = db.relationship("Candidate", backref="job", lazy=True, cascade="all, delete-orphan")

    @property
    def required_skills(self) -> list[str]:
        return loads(self.required_skills_json)

    @property
    def preferred_skills(self) -> list[str]:
        return loads(self.preferred_skills_json)

    @property
    def education(self) -> list[str]:
        return loads(self.education_json)

    @property
    def certifications(self) -> list[str]:
        return loads(self.certifications_json)

    @property
    def analysis(self) -> dict[str, Any]:
        return loads(self.analysis_json, {})

    def to_dict(self, include_counts: bool = True) -> dict[str, Any]:
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "required_skills": self.required_skills,
            "preferred_skills": self.preferred_skills,
            "education": self.education,
            "experience_min": self.experience_min,
            "experience_max": self.experience_max,
            "certifications": self.certifications,
            "location": self.location,
            "employment_type": self.employment_type,
            "status": self.status,
            "analysis": self.analysis,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_counts:
            candidates = self.candidates
            data["candidate_count"] = len(candidates)
            data["shortlisted_count"] = sum(1 for c in candidates if c.status == "Shortlisted")
            data["under_review_count"] = sum(1 for c in candidates if c.status == "Under Review")
            data["rejected_count"] = sum(1 for c in candidates if c.status == "Rejected")
        return data


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False, index=True)
    name = db.Column(db.String(255), default="Not Found")
    email = db.Column(db.String(255), index=True)
    phone = db.Column(db.String(80), index=True)
    location = db.Column(db.String(255))
    linkedin = db.Column(db.String(500))
    github = db.Column(db.String(500))
    portfolio = db.Column(db.String(500))
    current_role = db.Column(db.String(255))
    years_experience = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default="New", nullable=False)
    structured_json = db.Column(db.Text, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    resume = db.relationship("Resume", backref="candidate", uselist=False, cascade="all, delete-orphan")
    screening_result = db.relationship(
        "ScreeningResult",
        backref="candidate",
        uselist=False,
        cascade="all, delete-orphan",
    )
    skills = db.relationship("CandidateSkill", backref="candidate", lazy=True, cascade="all, delete-orphan")
    education_items = db.relationship("Education", backref="candidate", lazy=True, cascade="all, delete-orphan")
    experience_items = db.relationship("Experience", backref="candidate", lazy=True, cascade="all, delete-orphan")
    projects = db.relationship("Project", backref="candidate", lazy=True, cascade="all, delete-orphan")
    certifications = db.relationship("Certification", backref="candidate", lazy=True, cascade="all, delete-orphan")

    @property
    def structured(self) -> dict[str, Any]:
        return loads(self.structured_json, {})

    def to_dict(self, detail: bool = False) -> dict[str, Any]:
        result = self.screening_result
        data = {
            "id": self.id,
            "job_id": self.job_id,
            "job_title": self.job.title if self.job else None,
            "name": self.name or "Not Found",
            "email": self.email,
            "phone": self.phone,
            "location": self.location,
            "linkedin": self.linkedin,
            "github": self.github,
            "portfolio": self.portfolio,
            "current_role": self.current_role,
            "years_experience": self.years_experience or 0,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "overall_score": result.overall_score if result else None,
            "match_category": result.category if result else None,
            "recommendation": result.recommendation if result else None,
        }
        if detail:
            data.update(
                {
                    "structured": self.structured,
                    "skills": [skill.name for skill in self.skills],
                    "education": [item.to_dict() for item in self.education_items],
                    "experience": [item.to_dict() for item in self.experience_items],
                    "projects": [item.to_dict() for item in self.projects],
                    "certifications": [item.name for item in self.certifications],
                    "resume": self.resume.to_dict() if self.resume else None,
                    "screening_result": result.to_dict() if result else None,
                }
            )
        return data


class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidate.id"), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_path = db.Column(db.String(1000), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)
    file_size = db.Column(db.Integer, default=0)
    file_hash = db.Column(db.String(128), index=True)
    raw_text = db.Column(db.Text, default="")
    parse_status = db.Column(db.String(50), default="Pending")
    error = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "file_hash": self.file_hash,
            "parse_status": self.parse_status,
            "error": self.error,
            "uploaded_at": self.uploaded_at.isoformat(),
        }


class CandidateSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidate.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False, index=True)
    source = db.Column(db.String(80), default="resume")


class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidate.id"), nullable=False)
    degree = db.Column(db.String(255))
    institution = db.Column(db.String(255))
    year = db.Column(db.String(20))

    def to_dict(self) -> dict[str, Any]:
        return {"degree": self.degree, "institution": self.institution, "year": self.year}


class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidate.id"), nullable=False)
    role = db.Column(db.String(255))
    company = db.Column(db.String(255))
    duration_months = db.Column(db.Integer, default=0)

    def to_dict(self) -> dict[str, Any]:
        return {"role": self.role, "company": self.company, "duration_months": self.duration_months}


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidate.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, default="")

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description}


class Certification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidate.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)


class ScreeningResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidate.id"), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False, index=True)
    overall_score = db.Column(db.Float, default=0, nullable=False)
    category = db.Column(db.String(80), default="Weak Match")
    recommendation = db.Column(db.String(80), default="Review")
    explanation = db.Column(db.Text, default="")
    component_scores_json = db.Column(db.Text, default="{}")
    matched_skills_json = db.Column(db.Text, default="[]")
    missing_required_skills_json = db.Column(db.Text, default="[]")
    missing_preferred_skills_json = db.Column(db.Text, default="[]")
    related_skills_json = db.Column(db.Text, default="[]")
    ats_score = db.Column(db.Float, default=0)
    ats_feedback_json = db.Column(db.Text, default="[]")
    duplicate_of_id = db.Column(db.Integer, nullable=True)
    duplicate_similarity = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "overall_score": round(self.overall_score or 0, 2),
            "category": self.category,
            "recommendation": self.recommendation,
            "explanation": self.explanation,
            "component_scores": loads(self.component_scores_json, {}),
            "matched_skills": loads(self.matched_skills_json),
            "missing_required_skills": loads(self.missing_required_skills_json),
            "missing_preferred_skills": loads(self.missing_preferred_skills_json),
            "related_skills": loads(self.related_skills_json),
            "ats_score": round(self.ats_score or 0, 2),
            "ats_feedback": loads(self.ats_feedback_json),
            "duplicate_of_id": self.duplicate_of_id,
            "duplicate_similarity": round(self.duplicate_similarity or 0, 2),
            "created_at": self.created_at.isoformat(),
        }

