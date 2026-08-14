from pathlib import Path

import pytest

from services.resume_parser import ResumeParseError, parse_resume


def test_parse_txt_resume(tmp_path: Path):
    resume = tmp_path / "resume.txt"
    resume.write_text("Rahul Kumar\nEmail: rahul@example.com\nSkills: Python, SQL", encoding="utf-8")

    assert "Rahul Kumar" in parse_resume(resume)


def test_empty_document_raises(tmp_path: Path):
    resume = tmp_path / "empty.txt"
    resume.write_text("", encoding="utf-8")

    with pytest.raises(ResumeParseError):
        parse_resume(resume)


def test_valid_pdf(tmp_path: Path):
    fitz = pytest.importorskip("fitz")
    pdf_path = tmp_path / "resume.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "PDF Candidate\nSkills: Python")
    doc.save(pdf_path)
    doc.close()

    assert "PDF Candidate" in parse_resume(pdf_path)


def test_corrupted_pdf(tmp_path: Path):
    pytest.importorskip("fitz")
    pdf_path = tmp_path / "broken.pdf"
    pdf_path.write_bytes(b"not a real pdf")

    with pytest.raises(ResumeParseError):
        parse_resume(pdf_path)


def test_valid_docx(tmp_path: Path):
    docx = pytest.importorskip("docx")
    docx_path = tmp_path / "resume.docx"
    document = docx.Document()
    document.add_paragraph("DOCX Candidate")
    document.add_paragraph("Skills: Python, NLP")
    document.save(docx_path)

    assert "DOCX Candidate" in parse_resume(docx_path)

