from services.scoring_engine import categorize_score, score_candidate


def test_weighted_score_known_input():
    result = score_candidate(
        {
            "required_skills_score": 90,
            "experience_score": 75,
            "education_score": 100,
            "projects_score": 85,
            "preferred_skills_score": 80,
            "certifications_score": 70,
            "semantic_similarity_score": 92,
            "missing_required_skills": [],
        }
    )

    assert result["overall_score"] == 85.35
    assert result["category"] == "Strong Match"
    assert result["recommendation"] == "Shortlist"


def test_score_categories():
    assert categorize_score(95) == "Excellent Match"
    assert categorize_score(84) == "Strong Match"
    assert categorize_score(73) == "Good Match"
    assert categorize_score(63) == "Review"
    assert categorize_score(45) == "Weak Match"

