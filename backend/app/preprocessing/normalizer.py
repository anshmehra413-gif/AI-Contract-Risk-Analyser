import re

def normalize_numbering(heading: str) -> str:
    """
    Normalizes common legal numbering patterns:
    e.g., "1.", "1.1", "Section 2", "Article III", "(a)", "(i)"
    """
    if not heading:
        return ""
        
    heading = heading.strip()
    
    # Normalize "SECTION 3.2" -> "Section 3.2"
    heading = re.sub(r'(?i)^section\s+', 'Section ', heading)
    # Normalize "ARTICLE IV" -> "Article IV"
    heading = re.sub(r'(?i)^article\s+', 'Article ', heading)
    # Normalize "CLAUSE 5" -> "Clause 5"
    heading = re.sub(r'(?i)^clause\s+', 'Clause ', heading)
    
    return heading
