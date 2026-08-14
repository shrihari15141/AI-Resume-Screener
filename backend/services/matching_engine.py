from __future__ import annotations

import math
import re
from functools import lru_cache
from typing import Any

from services.skill_catalog import SKILL_GROUPS

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:  # pragma: no cover - dependency may be unavailable before installation.
    SentenceTransformer = None
    cosine_similarity = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
except Exception:  # pragma: no cover
    TfidfVectorizer = None


def normalize(value: str | None) -> str:
    return re.sub(r"[^a-z0-9+#. ]+", " ", (value or "").lower()).strip()


def score_ratio(matches: int, total: int) -> float:
    if total <= 0:
        return 100.0
    return round((matches / total) * 100, 2)


@lru_cache(maxsize=1)
def get_embedding_model():
    if SentenceTransformer is None:
        return None
    try:
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        return None


def text_similarity(text_a: str, text_b: str) -> float:
    text_a = text_a or ""
    text_b = text_b or ""
    if not text_a.strip() or not text_b.strip():
        return 0.0

    model = get_embedding_model()
    if model is not None and cosine_similarity is not None:
        vectors = model.encode([text_a[:4000], text_b[:4000]])
        return float(cosine_similarity([vectors[0]], [vectors[1]])[0][0])

    if TfidfVectorizer is None:
        shared = set(normalize(text_a).split()) & set(normalize(text_b).split())
        total = set(normalize(text_a).split()) | set(normalize(text_b).split())
        return len(shared) / len(total) if total else 0.0

    matrix = TfidfVectorizer(stop_words="english").fit_transform([text_a, text_b])
    return float((matrix[0] @ matrix[1].T).toarray()[0][0])


def skill_group(skill: str) -> str | None:
    normalized = normalize(skill)
    for group, aliases in SKILL_GROUPS.items():
        if normalized == normalize(group) or normalized in aliases:
            return group
        if any(alias in normalized or normalized in alias for alias in aliases):
            return group
    return None


def skill_matches(required_skill: str, candidate_skills: list[str], resume_text: str) -> tuple[bool, str | None]:
    req = normalize(required_skill)
    if not req:
        return True, None
    searchable_text = normalize(resume_text)
    for skill in candidate_skills:
        cand = normalize(skill)
        if req == cand or req in cand or cand in req:
            return True, skill

    req_group = skill_group(required_skill)
    for skill in candidate_skills:
        cand_group = skill_group(skill)
        if req_group and cand_group and req_group == cand_group:
            return True, skill

    if req_group:
        aliases = SKILL_GROUPS.get(req_group, set())
        if any(alias in searchable_text for alias in aliases):
            return True, req_group

    best = 0.0
    best_skill = None
    for skill in candidate_skills:
        similarity = text_similarity(required_skill, skill)
        if similarity > best:
            best = similarity
            best_skill = skill
    if best >= 0.62:
        return True, best_skill
    return False, None


def parse_years(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        match = re.search(r"(\d+(?:\.\d+)?)", str(value))
        return float(match.group(1)) if match else 0.0


def experience_score(profile: dict[str, Any], job_analysis: dict[str, Any]) -> float:
    years = parse_years(profile.get("years_experience"))
    requirement = job_analysis.get("experience", {}) or {}
    minimum = parse_years(requirement.get("minimum", 0))
    if minimum <= 0:
        return 100.0
    if years >= minimum:
        return 100.0
    return round(min(100.0, (years / minimum) * 100), 2)


def education_score(profile: dict[str, Any], job_analysis: dict[str, Any]) -> float:
    required = [normalize(item) for item in job_analysis.get("education", []) if item]
    if not required:
        return 100.0
    candidate_text = normalize(" ".join(str(item) for item in profile.get("education", [])))
    hits = sum(1 for item in required if item and item in candidate_text)
    return score_ratio(hits, len(required))


def project_score(profile: dict[str, Any], job_analysis: dict[str, Any], resume_text: str) -> float:
    projects = profile.get("projects", []) or []
    if not projects:
        return 0.0
    keywords = job_analysis.get("technical_keywords", []) or job_analysis.get("required_skills", [])
    project_text = normalize(" ".join(str(project) for project in projects))
    if not keywords:
        return 80.0
    hits = sum(1 for keyword in keywords if normalize(keyword) in project_text or normalize(keyword) in normalize(resume_text))
    return min(100.0, max(45.0, score_ratio(hits, len(keywords))))


def certification_score(profile: dict[str, Any], job_analysis: dict[str, Any]) -> float:
    required = [normalize(item) for item in job_analysis.get("certifications", []) if item]
    if not required:
        return 100.0 if profile.get("certifications") else 70.0
    candidate_text = normalize(" ".join(str(item) for item in profile.get("certifications", [])))
    hits = sum(1 for item in required if item in candidate_text)
    return score_ratio(hits, len(required))


def match_candidate(job_analysis: dict[str, Any], profile: dict[str, Any], resume_text: str) -> dict[str, Any]:
    candidate_skills = list(dict.fromkeys(profile.get("skills", []) or []))
    required = list(dict.fromkeys(job_analysis.get("required_skills", []) or []))
    preferred = list(dict.fromkeys(job_analysis.get("preferred_skills", []) or []))

    matched_required: list[str] = []
    missing_required: list[str] = []
    matched_preferred: list[str] = []
    missing_preferred: list[str] = []
    related: list[dict[str, str]] = []

    for skill in required:
        matched, source = skill_matches(skill, candidate_skills, resume_text)
        if matched:
            matched_required.append(skill)
            if source and normalize(source) != normalize(skill):
                related.append({"required": skill, "candidate_skill": source})
        else:
            missing_required.append(skill)

    for skill in preferred:
        matched, source = skill_matches(skill, candidate_skills, resume_text)
        if matched:
            matched_preferred.append(skill)
            if source and normalize(source) != normalize(skill):
                related.append({"required": skill, "candidate_skill": source})
        else:
            missing_preferred.append(skill)

    semantic = text_similarity(
        " ".join(required + preferred + [job_analysis.get("summary", "")]),
        resume_text,
    )
    semantic_score = round(max(0.0, min(1.0, semantic)) * 100, 2)
    if math.isnan(semantic_score):
        semantic_score = 0.0

    return {
        "required_skills_score": score_ratio(len(matched_required), len(required)),
        "preferred_skills_score": score_ratio(len(matched_preferred), len(preferred)),
        "experience_score": experience_score(profile, job_analysis),
        "education_score": education_score(profile, job_analysis),
        "projects_score": project_score(profile, job_analysis, resume_text),
        "certifications_score": certification_score(profile, job_analysis),
        "semantic_similarity_score": semantic_score,
        "matched_skills": matched_required + matched_preferred,
        "missing_required_skills": missing_required,
        "missing_preferred_skills": missing_preferred,
        "related_skills": related,
    }

