from __future__ import annotations

import re
from typing import Any

from services.job_analyzer import analyze_job_description
from services.skill_catalog import CANONICAL_SKILLS, DEGREES


def _find_first(pattern: str, text: str, flags: int = re.I) -> str | None:
    match = re.search(pattern, text, flags)
    return match.group(1).strip() if match else None


def _extract_name(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:8]:
        if len(line.split()) in {2, 3, 4} and not re.search(r"@|http|resume|curriculum|phone|\d", line, re.I):
            return line
    return "Not Found"


def _extract_skills(text: str) -> list[str]:
    normalized = text.lower()
    skills = []
    for skill in CANONICAL_SKILLS:
        pattern = r"\b" + re.escape(skill.lower()).replace(r"\ ", r"\s+") + r"\b"
        if re.search(pattern, normalized):
            skills.append(skill)
    return list(dict.fromkeys(skills))


def _section_lines(text: str, section_names: list[str], max_lines: int = 8) -> list[str]:
    lines = [line.strip(" -\t") for line in text.splitlines()]
    start = None
    section_pattern = re.compile(r"^(education|skills|experience|projects?|certifications?|summary|profile)\b", re.I)
    for index, line in enumerate(lines):
        if any(re.match(rf"^{re.escape(name)}\b", line, re.I) for name in section_names):
            start = index + 1
            break
    if start is None:
        return []
    result = []
    for line in lines[start : start + max_lines + 6]:
        if result and section_pattern.match(line):
            break
        if line:
            result.append(line)
        if len(result) >= max_lines:
            break
    return result


def _extract_education(text: str) -> list[dict[str, Any]]:
    lines = _section_lines(text, ["education"], 8)
    if not lines:
        lines = [line.strip() for line in text.splitlines() if any(degree.lower() in line.lower() for degree in DEGREES)]
    education = []
    for line in lines[:6]:
        degree = next((degree for degree in DEGREES if re.search(rf"\b{re.escape(degree)}\b", line, re.I)), None)
        year = _find_first(r"\b(20\d{2}|19\d{2})\b", line, flags=0)
        education.append({"degree": degree or line[:80], "institution": None, "year": year})
    return education


def _extract_projects(text: str) -> list[dict[str, str]]:
    lines = _section_lines(text, ["project", "projects"], 12)
    projects = []
    for line in lines[:8]:
        name, _, description = line.partition(":")
        projects.append({"name": name[:120], "description": description.strip() or line[:300]})
    return projects


def _extract_certifications(text: str) -> list[str]:
    lines = _section_lines(text, ["certification", "certifications"], 8)
    certs = [line for line in lines if line]
    if not certs:
        certs = re.findall(r"([A-Za-z0-9 +./-]*(?:certified|certification|certificate)[A-Za-z0-9 +./-]*)", text, re.I)
    return list(dict.fromkeys(item.strip()[:180] for item in certs if item.strip()))[:8]


def _extract_experience(text: str) -> tuple[list[dict[str, Any]], float]:
    years = [float(match) for match in re.findall(r"(\d+(?:\.\d+)?)\s*(?:\+?\s*years?|yrs?)", text, re.I)]
    months = [int(match) for match in re.findall(r"(\d+)\s*(?:months?|mos?)", text, re.I)]
    total_years = max(years) if years else 0.0
    if months:
        total_years = max(total_years, max(months) / 12)
    lines = _section_lines(text, ["experience", "work experience", "employment"], 10)
    items = []
    for line in lines[:5]:
        items.append({"role": line[:120], "company": None, "duration_months": int(total_years * 12) if total_years else 0})
    return items, round(total_years, 2)


def extract_resume_information(text: str) -> dict[str, Any]:
    email = _find_first(r"([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", text)
    phone = _find_first(r"(\+?\d[\d\s().-]{7,}\d)", text)
    linkedin = _find_first(r"(https?://(?:www\.)?linkedin\.com/[^\s)]+)", text)
    github = _find_first(r"(https?://(?:www\.)?github\.com/[^\s)]+)", text)
    urls = re.findall(r"(https?://[^\s)]+)", text)
    portfolio = next((url for url in urls if "linkedin.com" not in url and "github.com" not in url), None)
    experience, years = _extract_experience(text)

    profile = {
        "name": _extract_name(text),
        "email": email,
        "phone": phone,
        "education": _extract_education(text),
        "skills": _extract_skills(text),
        "experience": experience,
        "projects": _extract_projects(text),
        "certifications": _extract_certifications(text),
        "location": _find_first(r"(?:Location|Address)\s*[:\-]\s*([A-Za-z ,.-]+)", text),
        "linkedin": linkedin,
        "github": github,
        "portfolio": portfolio,
        "current_role": _find_first(r"(?:Current Role|Role|Title)\s*[:\-]\s*([A-Za-z0-9 +./-]+)", text),
        "companies": [],
        "years_experience": years,
    }
    return profile


def generate_candidate_explanation(
    job_title: str,
    profile: dict[str, Any],
    score: dict[str, Any],
    match_result: dict[str, Any],
    ats: dict[str, Any] | None = None,
) -> str:
    name = profile.get("name") or "Candidate"
    matched = match_result.get("matched_skills", [])
    missing_required = match_result.get("missing_required_skills", [])
    missing_preferred = match_result.get("missing_preferred_skills", [])
    recommendation = score.get("recommendation", "Review")
    lines = [
        f"{name} scored {score['overall_score']}% for {job_title}, classified as {score['category']}.",
        f"Recommendation: {recommendation}.",
    ]
    if matched:
        lines.append("Matched skills: " + ", ".join(matched[:12]) + ".")
    if missing_required:
        lines.append("Missing required skills: " + ", ".join(missing_required[:10]) + ".")
    if missing_preferred:
        lines.append("Missing preferred skills: " + ", ".join(missing_preferred[:10]) + ".")
    if profile.get("projects"):
        project_names = [project.get("name", "") for project in profile["projects"] if project.get("name")]
        if project_names:
            lines.append("Relevant projects found: " + ", ".join(project_names[:5]) + ".")
    if ats:
        lines.append(f"ATS resume quality score: {ats.get('score', 0)}.")
    lines.append("This explanation uses only the parsed resume data and the job requirements.")
    return "\n".join(lines)

