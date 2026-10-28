from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
import os

from backend.app.ingestion.pdf_parser import extract_text_from_pdf
from backend.app.ingestion.docx_parser import extract_text_from_docx
from backend.app.ingestion.ocr import evaluate_document_readability
from backend.app.preprocessing.cleaner import clean_pages

router = APIRouter(prefix="/api", tags=["Upload & Ingestion"])

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Accepts PDF, DOCX, or TXT document, performs validation,
    extracts structured pages, cleans text, and verifies readability.
    Implements Section 7: Document Processing Pipeline.
    """
    filename = file.filename or "uploaded_contract"
    extension = os.path.splitext(filename)[1].lower()
    
    if extension not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file format. Please upload a PDF (.pdf), Word Document (.docx), or Text file (.txt)."
        )
        
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds maximum 25MB limit.")
        
    # Extract pages based on format
    if extension == ".pdf":
        raw_pages = extract_text_from_pdf(contents)
    elif extension == ".docx":
        raw_pages = extract_text_from_docx(contents)
    else:  # .txt
        text_str = contents.decode("utf-8", errors="ignore")
        raw_pages = [{"page": 1, "text": text_str, "paragraphs": text_str.split("\n\n")}]
        
    cleaned_pages = clean_pages(raw_pages)
    readability = evaluate_document_readability(cleaned_pages)
    full_text = "\n\n".join([p["text"] for p in cleaned_pages])
    
    return {
        "filename": filename,
        "extension": extension,
        "file_size_bytes": len(contents),
        "total_pages": len(cleaned_pages),
        "readability": readability,
        "full_text": full_text,
        "pages": cleaned_pages
    }
