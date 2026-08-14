from __future__ import annotations

from typing import Any


def score_resume_quality(profile: dict[str, Any], resume_text: str) -> dict[str, Any]:
    checks = []

    def add(label: str, passed: bool, points: int, suggestion: str | None = None) -> int:
        checks.append({"label": label, "passed": passed, "suggestion": suggestion})
        return points if passed else 0

    score = 0
    score += add("Contact information", bool(profile.get("email") and profile.get("phone")), 20, "Add email and phone number.")
    score += add("Skills section", bool(profile.get("skills")), 20, "Add a clear skills section with role-relevant keywords.")
    score += add("Experience section", bool(profile.get("experience")), 15, "Summarize internships, roles, or hands-on work.")
    score += add("Projects", bool(profile.get("projects")), 15, "Include projects with measurable outcomes.")
    score += add("Education", bool(profile.get("education")), 15, "Add degree, institution, and graduation year.")
    score += add("Certifications", bool(profile.get("certifications")), 5, "List relevant certifications if available.")
    score += add("Readable length", len(resume_text.split()) >= 120, 10, "Add more detail while keeping the resume concise.")

    suggestions = [item["suggestion"] for item in checks if not item["passed"] and item.get("suggestion")]
    return {"score": min(100, score), "checks": checks, "suggestions": suggestions}

