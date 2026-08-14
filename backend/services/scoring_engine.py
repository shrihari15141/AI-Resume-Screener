from __future__ import annotations

from typing import Any


DEFAULT_WEIGHTS = {
    "required_skills": 0.35,
    "experience": 0.20,
    "education": 0.10,
    "projects": 0.15,
    "preferred_skills": 0.10,
    "certifications": 0.05,
    "semantic_similarity": 0.05,
}

MATCH_THRESHOLDS = {
    "Excellent Match": 90,
    "Strong Match": 80,
    "Good Match": 70,
    "Review": 60,
}


def clamp_score(value: float | int | None) -> float:
    if value is None:
        return 0.0
    return max(0.0, min(100.0, float(value)))


def categorize_score(score: float) -> str:
    if score >= MATCH_THRESHOLDS["Excellent Match"]:
        return "Excellent Match"
    if score >= MATCH_THRESHOLDS["Strong Match"]:
        return "Strong Match"
    if score >= MATCH_THRESHOLDS["Good Match"]:
        return "Good Match"
    if score >= MATCH_THRESHOLDS["Review"]:
        return "Review"
    return "Weak Match"


def recommendation_for(score: float, missing_required: list[str]) -> str:
    if score >= 80 and not missing_required:
        return "Shortlist"
    if score >= 60:
        return "Review"
    return "Reject"


def score_candidate(match_result: dict[str, Any], weights: dict[str, float] | None = None) -> dict[str, Any]:
    weights = weights or DEFAULT_WEIGHTS
    components = {
        "required_skills": clamp_score(match_result.get("required_skills_score")),
        "experience": clamp_score(match_result.get("experience_score")),
        "education": clamp_score(match_result.get("education_score")),
        "projects": clamp_score(match_result.get("projects_score")),
        "preferred_skills": clamp_score(match_result.get("preferred_skills_score")),
        "certifications": clamp_score(match_result.get("certifications_score")),
        "semantic_similarity": clamp_score(match_result.get("semantic_similarity_score")),
    }
    total = sum(components[key] * weights[key] for key in weights)
    total = round(clamp_score(total), 2)
    missing_required = match_result.get("missing_required_skills", [])
    return {
        "overall_score": total,
        "category": categorize_score(total),
        "recommendation": recommendation_for(total, missing_required),
        "component_scores": components,
        "weights": weights,
    }

