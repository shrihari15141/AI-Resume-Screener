from __future__ import annotations

import io
import time

import pytest


def auth_headers(client, email):
    response = client.post(
        "/api/auth/register",
        json={"username": "Batch Tester", "email": email, "password": "Password123"},
    )
    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_job(client, headers):
    response = client.post(
        "/api/jobs",
        json={
            "title": "Python Developer",
            "description": "Python Flask SQL Machine Learning role for resume screening.",
            "required_skills": ["Python", "Flask", "SQL"],
            "preferred_skills": ["Machine Learning"],
            "education": ["BCA", "BTech"],
            "experience": "0 to 2 years",
            "certifications": [],
            "location": "Remote",
            "employment_type": "Full-time",
        },
        headers=headers,
    )
    return response.get_json()["job"]["id"]


@pytest.mark.parametrize("count", [10, 50, 100])
def test_batch_upload_sizes(monkeypatch, tmp_path, count):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.sqlite'}")
    monkeypatch.setenv("UPLOAD_FOLDER", str(tmp_path / "uploads"))

    from app import create_app

    app = create_app()
    client = app.test_client()
    headers = auth_headers(client, f"batch{count}@example.com")
    job_id = create_job(client, headers)

    resumes = []
    for index in range(count):
        content = (
            f"Candidate {index}\n"
            f"Email: candidate{index}@example.com\n"
            "Phone: +91 90000 00000\n"
            "Skills: Python, Flask, SQL, Machine Learning\n"
            "Education\nBCA, Test College, 2026\n"
            "Experience\nPython Intern, 6 months\n"
            "Projects\nResume Screening API: Flask and SQL project."
        ).encode("utf-8")
        resumes.append((io.BytesIO(content), f"candidate_{index}.txt"))

    response = client.post(
        "/api/screening/upload",
        data={"job_id": str(job_id), "resumes": resumes},
        content_type="multipart/form-data",
        headers=headers,
    )
    assert response.status_code == 202
    batch_id = response.get_json()["batch_id"]

    status = None
    for _ in range(100):
        status_response = client.get(f"/api/screening/{batch_id}/status", headers=headers)
        status = status_response.get_json()
        if status["status"] == "complete":
            break
        time.sleep(0.05)

    assert status["status"] == "complete"
    assert status["success"] == count
    assert status["failed"] == 0
