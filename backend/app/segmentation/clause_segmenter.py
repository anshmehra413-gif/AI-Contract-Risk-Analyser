import re
import uuid
from typing import List, Dict, Any

# Pattern matching legal section headings
HEADING_PATTERNS = [
    # "Section 1. Definitions" or "Section 1 - Definitions" or "Section 1: Definitions"
    r'(?i)^(section\s+\d+(\.\d+)*\s*[:\.\-–]?\s*[A-Za-z\s]+)',
    # "Article II. Termination"
    r'(?i)^(article\s+[ivxlc\d]+(\.\d+)*\s*[:\.\-–]?\s*[A-Za-z\s]+)',
    # "Clause 3. Rent"
    r'(?i)^(clause\s+\d+(\.\d+)*\s*[:\.\-–]?\s*[A-Za-z\s]+)',
    # "1. Term and Termination" or "1.1 Rent and Deposit"
    r'^(\d+(\.\d+)+\s+[\w\s]{2,40})',
    r'^(\d+\.\s+[\w\s]{2,40})',
]

def segment_clauses(pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Segments document text into discrete legal clauses with page number and clause numbering.
    Implements Section 7.4: Clause Segmentation.
    """
    clauses = []
    current_clause = None
    clause_idx = 1
    
    for p_info in pages_data:
        page_num = p_info.get("page", 1)
        paragraphs = p_info.get("paragraphs", [])
        
        for para in paragraphs:
            para_clean = para.strip()
            if not para_clean:
                continue
                
            # Check if this paragraph starts with or is a clause heading
            is_heading = False
            heading_title = ""
            matched_num = f"Clause {clause_idx}"
            
            for pat in HEADING_PATTERNS:
                m = re.match(pat, para_clean)
                if m:
                    is_heading = True
                    heading_title = m.group(1).strip()
                    matched_num = heading_title
                    break
                    
            # Check for standard uppercase short title like "TERMINATION OF LEASE" or "GOVERNING LAW"
            if not is_heading and len(para_clean) < 60 and (para_clean.isupper() or para_clean.istitle()) and not para_clean.endswith('.'):
                is_heading = True
                heading_title = para_clean
                matched_num = f"Section {clause_idx} - {heading_title}"

            if is_heading:
                # Save previous clause if present
                if current_clause and current_clause["text"].strip():
                    clauses.append(current_clause)
                    clause_idx += 1
                    
                # Extract any remaining body text in this paragraph after heading
                body_text = para_clean
                current_clause = {
                    "id": f"clause-{uuid.uuid4().hex[:8]}",
                    "clause_number": matched_num,
                    "title": heading_title,
                    "text": body_text,
                    "page_number": page_num,
                    "confidence": 0.90,
                    "start_char": 0,
                    "end_char": len(body_text)
                }
            else:
                if current_clause is None:
                    # Initial clause or preamble
                    current_clause = {
                        "id": f"clause-{uuid.uuid4().hex[:8]}",
                        "clause_number": f"Preamble / Recitals" if clause_idx == 1 else f"Clause {clause_idx}",
                        "title": "Preliminary / General Terms",
                        "text": para_clean,
                        "page_number": page_num,
                        "confidence": 0.85,
                        "start_char": 0,
                        "end_char": len(para_clean)
                    }
                else:
                    # Append paragraph to current clause if related or start a new clause if very long
                    if len(current_clause["text"]) > 1200:
                        clauses.append(current_clause)
                        clause_idx += 1
                        current_clause = {
                            "id": f"clause-{uuid.uuid4().hex[:8]}",
                            "clause_number": f"Clause {clause_idx}",
                            "title": f"Clause {clause_idx}",
                            "text": para_clean,
                            "page_number": page_num,
                            "confidence": 0.85,
                            "start_char": 0,
                            "end_char": len(para_clean)
                        }
                    else:
                        current_clause["text"] += "\n\n" + para_clean
                        current_clause["end_char"] = len(current_clause["text"])
                        
    if current_clause and current_clause["text"].strip():
        clauses.append(current_clause)
        
    return clauses
