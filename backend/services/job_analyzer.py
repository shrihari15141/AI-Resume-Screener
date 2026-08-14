from __future__ import annotations

import re
from typing import Any

from services.skill_catalog import CANONICAL_SKILLS, DEGREES


def split_tags(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        items = value
    else:
        items = re.split(r"[,;\n]+", value)
    cleaned = [str(item).strip() for item in items if str(item).strip()]
    return list(dict.fromkeys(cleaned))


def extract_known_terms(text: str, terms: list[str]) -> list[str]:
    normalized = text.lower()
    found = []
    for term in terms:
        pattern = r"\b" + re.escape(term.lower()).replace(r"\ ", r"\s+") + r"\b"
        if re.search(pattern, normalized):
            found.append(term)
    return list(dict.fromkeys(found))


def parse_experience(value: str | int | float | None, description: str = "") -> dict[str, float | None]:
    combined = f"{value or ''} {description}"
    numbers = [float(item) for item in re.findall(r"(\d+(?:\.\d+)?)\s*(?:\+?\s*years?|yrs?)", combined, flags=re.I)]
    ranges = re.findall(r"(\d+(?:\.\d+)?)\s*[-to]+\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)", combined, flags=re.I)
    if ranges:
        minimum, maximum = ranges[0]
        return {"minimum": float(minimum), "maximum": float(maximum)}
    if numbers:
        return {"minimum": min(numbers), "maximum": max(numbers) if len(numbers) > 1 else None}
    return {"minimum": 0.0, "maximum": None}


def analyze_job_description(payload: dict[str, Any]) -> dict[str, Any]:
    description = payload.get("description", "") or ""
    required = split_tags(payload.get("required_skills"))
    preferred = split_tags(payload.get("preferred_skills"))
    education = split_tags(payload.get("education"))
    certifications = split_tags(payload.get("certifications"))

    detected_skills = extract_known_terms(description, CANONICAL_SKILLS)
    detected_degrees = extract_known_terms(description, DEGREES)

    for skill in detected_skills:
        if skill not in required and skill not in preferred:
            required.append(skill)
    for degree in detected_degrees:
        if degree not in education:
            education.append(degree)

    soft_skills = extract_known_terms(
        description,
        ["Communication", "Leadership", "Problem Solving", "Research", "Collaboration", "Critical Thinking"],
    )
    responsibilities = [
        line.strip("- ").strip()
        for line in description.splitlines()
        if line.strip() and len(line.strip()) > 24
    ][:8]

    return {
        "summary": description[:800],
        "required_skills": required,
        "preferred_skills": preferred,
        "education": education,
        "experience": parse_experience(payload.get("experience"), description),
        "technical_keywords": list(dict.fromkeys(required + preferred + detected_skills)),
        "soft_skills": soft_skills,
        "certifications": certifications,
        "responsibilities": responsibilities,
    }

