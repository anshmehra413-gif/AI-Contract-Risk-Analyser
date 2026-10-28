import io
from typing import List, Dict, Any

def extract_text_from_docx(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Extracts text from DOCX bytes, preserving paragraphs, headings and simulating pages.
    """
    pages_data = []
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = []
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                paragraphs.append(text)
        
        # Approximate 500 words or 5 paragraphs per virtual page
        PAGE_SIZE = 5
        curr_page = 1
        for i in range(0, max(1, len(paragraphs)), PAGE_SIZE):
            chunk = paragraphs[i:i+PAGE_SIZE]
            pages_data.append({
                "page": curr_page,
                "text": "\n\n".join(chunk),
                "paragraphs": chunk
            })
            curr_page += 1
            
        if not pages_data:
            pages_data.append({"page": 1, "text": "", "paragraphs": []})
    except Exception as e:
        # Fallback if docx reading fails
        text = file_bytes.decode("utf-8", errors="ignore")
        paras = [p.strip() for p in text.split("\n\n") if p.strip()]
        pages_data.append({
            "page": 1,
            "text": text,
            "paragraphs": paras
        })
        
    return pages_data
