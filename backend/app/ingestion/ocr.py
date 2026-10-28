from typing import Dict, Any, List

def evaluate_document_readability(pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Checks whether extracted text is sufficient or if OCR would be required (e.g. scanned image PDF).
    """
    total_chars = sum(len(p.get("text", "")) for p in pages_data)
    total_pages = len(pages_data)
    
    if total_pages == 0:
        return {
            "readable": False,
            "requires_ocr": True,
            "char_count": 0,
            "avg_chars_per_page": 0,
            "reason": "No pages detected in document"
        }
        
    avg_chars = total_chars / total_pages
    # Scanned documents typically have < 50 chars per page extracted natively
    if avg_chars < 50:
        return {
            "readable": False,
            "requires_ocr": True,
            "char_count": total_chars,
            "avg_chars_per_page": round(avg_chars, 1),
            "reason": "Scanned document detected. Optical Character Recognition (OCR) recommended for scanned PDF."
        }
        
    return {
        "readable": True,
        "requires_ocr": False,
        "char_count": total_chars,
        "avg_chars_per_page": round(avg_chars, 1),
        "reason": "Document has clean digital text layer"
    }
