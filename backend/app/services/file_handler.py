import os
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status

# Local directory where uploads are stored
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")


def validate_pdf(file: UploadFile) -> None:
    """
    Validates that the uploaded file is a valid non-empty PDF document.
    Raises HTTPException(400) if:
    - No file or filename is provided
    - The file extension is not '.pdf'
    - The content-type is not 'application/pdf' or 'application/x-pdf'
    - The file is empty (0 bytes)
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded or file name is missing."
        )

    # 1. Extension check
    filename = file.filename.strip()
    ext = os.path.splitext(filename)[1].lower()
    if ext != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension '{ext}'. Only PDF documents (.pdf) are accepted."
        )

    # 2. Content-type check
    content_type = (file.content_type or "").lower().strip()
    if content_type and content_type not in ["application/pdf", "application/x-pdf", "binary/octet-stream"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid content type '{file.content_type}'. Expected 'application/pdf'."
        )

    # 3. Check for empty file
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    if size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded PDF file is empty (0 bytes)."
        )


def save_temp_file(file: UploadFile) -> str:
    """
    Saves the file to a local uploads/ directory (creates it if missing)
    and returns the saved absolute path.
    No text extraction or OCR — just saves the file.
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    original_filename = Path(file.filename or "uploaded.pdf").name
    # Generate unique filename to avoid overwrites
    safe_filename = f"{uuid.uuid4().hex[:12]}_{original_filename}"
    saved_path = os.path.join(UPLOAD_DIR, safe_filename)

    file.file.seek(0)
    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file.file.seek(0)
    return os.path.abspath(saved_path)
