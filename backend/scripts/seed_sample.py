from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app import create_app
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
    User,
    dumps,
)
from services.ai_service import extract_resume_information, generate_candidate_explanation
from services.ats_analyzer import score_resume_quality
from services.duplicate_detector import find_possible_duplicate
from services.job_analyzer import analyze_job_description
from services.matching_engine import match_candidate
from services.scoring_engine import score_candidate


def read_resume_files() -> list[Path]:
    return sorted((ROOT / "sample_data" / "resumes").glob("*.txt"))


def add_children(candidate: Candidate, profile: dict) -> None:
    for skill in profile.get("skills", []):
        candidate.skills.append(CandidateSkill(name=skill))
    for item in profile.get("education", []):
        candidate.education_items.append(Education(degree=item.get("degree"), institution=item.get("institution"), year=item.get("year")))
    for item in profile.get("experience", []):
        candidate.experience_items.append(Experience(role=item.get("role"), company=item.get("company"), duration_months=item.get("duration_months") or 0))
    for item in profile.get("projects", []):
        candidate.projects.append(Project(name=item.get("name", "Project"), description=item.get("description", "")))
    for certification in profile.get("certifications", []):
        candidate.certifications.append(Certification(name=certification))


def main() -> None:
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email="recruiter@example.com").first()
        if not user:
            user = User(username="Demo Recruiter", email="recruiter@example.com")
            user.set_password("Password123")
            db.session.add(user)
            db.session.commit()

        description = (ROOT / "sample_data" / "job_description.md").read_text(encoding="utf-8")
        payload = {
            "title": "Junior AI Research Associate",
            "description": description,
            "required_skills": ["Python", "Machine Learning", "NLP", "SQL", "Flask", "Git"],
            "preferred_skills": ["LLM", "RAG", "LangChain", "Docker", "React"],
            "education": ["BCA", "BSc", "MCA", "MSc", "BTech"],
            "experience": "0 to 2 years",
            "certifications": ["AI", "Machine Learning"],
            "location": "Remote / India",
            "employment_type": "Full-time",
        }
        analysis = analyze_job_description(payload)

        job = Job.query.filter_by(user_id=user.id, title=payload["title"]).first()
        if not job:
            job = Job(user_id=user.id, title=payload["title"], description=payload["description"])
            db.session.add(job)
        job.required_skills_json = dumps(analysis["required_skills"])
        job.preferred_skills_json = dumps(analysis["preferred_skills"])
        job.education_json = dumps(analysis["education"])
        job.certifications_json = dumps(analysis["certifications"])
        job.experience_min = analysis["experience"]["minimum"] or 0
        job.experience_max = analysis["experience"]["maximum"]
        job.location = payload["location"]
        job.employment_type = payload["employment_type"]
        job.analysis_json = dumps(analysis)
        db.session.commit()

        for path in read_resume_files():
            text = path.read_text(encoding="utf-8")
            profile = extract_resume_information(text)
            if Candidate.query.filter_by(job_id=job.id, email=profile.get("email")).first() and profile.get("email"):
                continue

            duplicate = find_possible_duplicate(job.id, profile, text)
            candidate = Candidate(
                job_id=job.id,
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
            add_children(candidate, profile)
            db.session.add(candidate)
            db.session.flush()

            resume = Resume(
                candidate_id=candidate.id,
                original_filename=path.name,
                stored_path=str(path),
                file_type="txt",
                file_size=path.stat().st_size,
                file_hash=path.name,
                raw_text=text,
                parse_status="Parsed",
            )
            db.session.add(resume)

            match_result = match_candidate(analysis, profile, text)
            score = score_candidate(match_result)
            ats = score_resume_quality(profile, text)
            result = ScreeningResult(
                candidate_id=candidate.id,
                job_id=job.id,
                overall_score=score["overall_score"],
                category=score["category"],
                recommendation=score["recommendation"],
                explanation=generate_candidate_explanation(job.title, profile, score, match_result, ats),
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

        print("Seeded sample recruiter, job, and resumes.")
        print("Login: recruiter@example.com / Password123")


if __name__ == "__main__":
    main()

