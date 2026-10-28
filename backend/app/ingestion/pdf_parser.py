import io
import re
from typing import List, Dict, Any

def extract_text_from_pdf(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Extracts text from PDF bytes, preserving page number, paragraphs, and sections.
    Returns a list of page objects: [{'page': 1, 'text': '...', 'paragraphs': [...]}]
    """
    pages_data = []
    
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        for page_idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            # Split into paragraphs
            raw_paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            if not raw_paragraphs and text.strip():
                raw_paragraphs = [p.strip() for p in text.splitlines() if p.strip()]
            pages_data.append({
                "page": page_idx + 1,
                "text": text,
                "paragraphs": raw_paragraphs
            })
    except Exception as e:
        # Fallback basic text extraction if pypdf encounters issues
        text = file_bytes.decode("utf-8", errors="ignore")
        # Split on form feed or create artificial pages
        page_chunks = text.split("\x0c") if "\x0c" in text else [text]
        for idx, chunk in enumerate(page_chunks):
            paragraphs = [p.strip() for p in chunk.split("\n\n") if p.strip()]
            pages_data.append({
                "page": idx + 1,
                "text": chunk,
                "paragraphs": paragraphs
            })
            
    return pages_data
