import re
from typing import List, Dict, Any

def clean_text(text: str) -> str:
    """
    Cleans extracted legal contract text while preserving legal structure,
    clause headers, numbering, and paragraph breaks.
    """
    if not text:
        return ""
        
    # Replace non-standard whitespace/non-breaking spaces
    text = text.replace('\xa0', ' ').replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove repeated page header/footer noise patterns like "Page X of Y"
    text = re.sub(r'(?i)page\s+\d+\s+of\s+\d+', '', text)
    text = re.sub(r'(?i)---\s*page\s*\d+\s*---', '', text)
    
    # Collapse multiple inline spaces, while preserving line breaks
    lines = []
    for line in text.split('\n'):
        cleaned_line = re.sub(r'[ \t]+', ' ', line).strip()
        lines.append(cleaned_line)
        
    # Collapse 3+ consecutive newlines to 2 newlines (paragraph boundary)
    cleaned = '\n'.join(lines)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
    return cleaned

def clean_pages(pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Cleans text page by page, preserving page metadata and cleaned paragraph arrays.
    """
    cleaned_pages = []
    for p in pages_data:
        raw_text = p.get("text", "")
        cleaned = clean_text(raw_text)
        paras = [clean_text(para) for para in p.get("paragraphs", []) if clean_text(para)]
        cleaned_pages.append({
            "page": p.get("page", 1),
            "text": cleaned,
            "paragraphs": paras if paras else ([cleaned] if cleaned else [])
        })
    return cleaned_pages
