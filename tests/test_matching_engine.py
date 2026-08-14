from services.matching_engine import match_candidate


JOB = {
    "required_skills": ["Python", "Machine Learning", "SQL", "API Development"],
    "preferred_skills": ["Docker"],
    "education": ["BCA"],
    "experience": {"minimum": 1, "maximum": 2},
    "technical_keywords": ["Python", "Machine Learning", "SQL", "API"],
    "certifications": [],
}


def test_exact_skill_match():
    profile = {
        "skills": ["Python", "SQL", "Flask REST API"],
        "education": [{"degree": "BCA"}],
        "experience": [{"role": "Intern"}],
        "projects": [{"name": "Flask API"}],
        "certifications": [],
        "years_experience": 1,
    }
    result = match_candidate(JOB, profile, "Python SQL Flask REST API BCA machine learning project")

    assert "Python" in result["matched_skills"]
    assert result["experience_score"] == 100


def test_semantic_skill_match_from_related_terms():
    profile = {
        "skills": ["scikit-learn", "Regression", "Classification", "MySQL", "Flask REST API"],
        "education": [{"degree": "BCA"}],
        "experience": [{"role": "ML Intern"}],
        "projects": [{"name": "Prediction API"}],
        "certifications": [],
        "years_experience": 1,
    }
    result = match_candidate(JOB, profile, "scikit-learn regression classification MySQL Flask REST API")

    assert "Machine Learning" in result["matched_skills"]
    assert "SQL" in result["matched_skills"]
    assert "API Development" in result["matched_skills"]


def test_missing_required_skill():
    profile = {
        "skills": ["Excel", "Power BI"],
        "education": [{"degree": "BCom"}],
        "experience": [],
        "projects": [],
        "certifications": [],
        "years_experience": 0,
    }
    result = match_candidate(JOB, profile, "Excel reports and dashboards")

    assert "Python" in result["missing_required_skills"]
    assert result["required_skills_score"] < 50

