from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any

from models import Candidate, Resume


def text_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return round(SequenceMatcher(None, a[:8000], b[:8000]).ratio() * 100, 2)


def find_possible_duplicate(job_id: int, profile: dict[str, Any], resume_text: str) -> dict[str, Any] | None:
    email = (profile.get("email") or "").lower()
    phone = profile.get("phone") or ""
    name = (profile.get("name") or "").lower()

    candidates = Candidate.query.filter(Candidate.job_id == job_id).all()
    best = None
    for candidate in candidates:
        score = 0.0
        reasons = []
        direct_identifier_match = False
        if email and candidate.email and email == candidate.email.lower():
            score = max(score, 100.0)
            reasons.append("email")
            direct_identifier_match = True
        if phone and candidate.phone and phone == candidate.phone:
            score = max(score, 96.0)
            reasons.append("phone")
            direct_identifier_match = True
        if name and candidate.name and name == candidate.name.lower():
            score = max(score, 85.0)
            reasons.append("name")
        if not direct_identifier_match and candidate.resume and candidate.resume.raw_text:
            similarity = text_similarity(resume_text, candidate.resume.raw_text)
            if similarity >= 88:
                score = max(score, similarity)
                reasons.append("resume_text")
        if score >= 85 and (best is None or score > best["similarity"]):
            best = {"candidate_id": candidate.id, "similarity": score, "reasons": reasons}
    return best
