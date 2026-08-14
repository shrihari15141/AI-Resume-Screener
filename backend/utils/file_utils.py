from __future__ import annotations

import hashlib
from pathlib import Path
from uuid import uuid4

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
ALLOWED_MIME_PREFIXES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "application/octet-stream",
}


def validate_resume_file(file: FileStorage, max_mb: int) -> tuple[bool, str]:
    if not file or not file.filename:
        return False, "No file selected."
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        return False, f"{extension or 'unknown'} files are not supported."
    if file.mimetype and file.mimetype not in ALLOWED_MIME_PREFIXES:
        return False, "Unsupported file MIME type."
    position = file.stream.tell()
    file.stream.seek(0, 2)
    size = file.stream.tell()
    file.stream.seek(position)
    if size > max_mb * 1024 * 1024:
        return False, f"File exceeds {max_mb} MB."
    return True, ""


def save_upload(file: FileStorage, destination: Path) -> dict[str, str | int]:
    destination.mkdir(parents=True, exist_ok=True)
    original = secure_filename(file.filename or "resume")
    extension = Path(original).suffix.lower()
    stored_name = f"{uuid4().hex}{extension}"
    stored_path = destination / stored_name
    file.save(stored_path)
    data = stored_path.read_bytes()
    return {
        "original_filename": original,
        "stored_path": str(stored_path),
        "file_type": extension.lstrip("."),
        "file_size": len(data),
        "file_hash": hashlib.sha256(data).hexdigest(),
    }

