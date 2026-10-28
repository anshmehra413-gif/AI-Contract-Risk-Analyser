import re
from typing import Dict, Any, List, Tuple

# 15 Target CUAD Categories (Section 6, Table 3)
CUAD_CATEGORIES = [
    "Parties",
    "Effective Date",
    "Expiration Date",
    "Termination",
    "Notice",
    "Renewal",
    "Payment",
    "Penalties",
    "Indemnification",
    "Limitation of Liability",
    "Governing Law",
    "Dispute Resolution",
    "Assignment",
    "Obligations",
    "Confidentiality"
]

CATEGORY_SIGNATURES = {
    "Parties": {
        "keywords": ["party", "parties", "by and between", "landlord", "tenant", "contractor", "subcontractor", "employer", "employee", "client", "vendor", "lessor", "lessee"],
        "patterns": [r'(?i)between\s+[A-Z\s,]+and\s+[A-Z\s,]+', r'(?i)parties\s+agree', r'(?i)hereinafter\s+referred\s+to\s+as']
    },
    "Effective Date": {
        "keywords": ["effective date", "commencement date", "dated as of", "entered into on", "start date", "made on this", "day of"],
        "patterns": [r'(?i)effective\s+(as\s+of|date)', r'(?i)commencing\s+on', r'(?i)dated\s+(as\s+of|this)']
    },
    "Expiration Date": {
        "keywords": ["expiration", "expire", "expiry date", "term end", "valid until", "conclusion date", "terminates on"],
        "patterns": [r'(?i)expire(s|d)?\s+on', r'(?i)term\s+shall\s+end', r'(?i)valid\s+until']
    },
    "Termination": {
        "keywords": ["terminate", "termination", "cancel", "cancellation", "default", "breach", "without cause", "immediate termination", "cure period", "material breach"],
        "patterns": [r'(?i)right\s+to\s+terminate', r'(?i)termination\s+for\s+cause', r'(?i)terminate\s+this\s+agreement', r'(?i)upon\s+\d+\s+days?\s+written\s+notice']
    },
    "Notice": {
        "keywords": ["notice", "notices", "written notice", "certified mail", "email notice", "registered post", "receipt requested", "addressed to"],
        "patterns": [r'(?i)notices?\s+under\s+this\s+agreement', r'(?i)shall\s+be\s+given\s+in\s+writing', r'(?i)delivered\s+by\s+hand']
    },
    "Renewal": {
        "keywords": ["renewal", "renew", "automatic renewal", "extension", "renewed for successive", "auto-renew", "written notice of non-renewal"],
        "patterns": [r'(?i)automatically\s+renew', r'(?i)renewal\s+term', r'(?i)extend(ed)?\s+for\s+a\s+period']
    },
    "Payment": {
        "keywords": ["payment", "fee", "rent", "installment", "monthly rent", "invoicing", "payable", "amount", "due date", "consideration", "deposit", "security deposit"],
        "patterns": [r'(?i)shall\s+pay', r'(?i)monthly\s+rent\s+of', r'(?i)payment\s+terms', r'(?i)due\s+on\s+the\s+\d+']
    },
    "Penalties": {
        "keywords": ["penalty", "penalties", "late fee", "interest rate", "liquidated damages", "per day of delay", "late payment charge", "forfeiture"],
        "patterns": [r'(?i)late\s+(fee|charge|penalty)', r'(?i)liquidated\s+damages', r'(?i)interest\s+at\s+the\s+rate\s+of', r'(?i)per\s+day\s+of\s+delay']
    },
    "Indemnification": {
        "keywords": ["indemnify", "indemnification", "hold harmless", "defend", "damages", "losses", "liabilities", "third party claims", "save harmless"],
        "patterns": [r'(?i)indemnify(,\s*defend)?\s+and\s+hold\s+harmless', r'(?i)against\s+any\s+and\s+all\s+claims', r'(?i)indemnifying\s+party']
    },
    "Limitation of Liability": {
        "keywords": ["limitation of liability", "consequential damages", "indirect damages", "cap on liability", "aggregate liability", "in no event shall", "punitive damages", "maximum liability"],
        "patterns": [r'(?i)limitation\s+of\s+liability', r'(?i)in\s+no\s+event\s+shall\s+either\s+party\s+be\s+liable', r'(?i)aggregate\s+liability\s+shall\s+not\s+exceed']
    },
    "Governing Law": {
        "keywords": ["governing law", "laws of", "jurisdiction", "construed in accordance with", "courts of", "venue", "legal proceedings"],
        "patterns": [r'(?i)governed\s+by\s+and\s+construed\s+in\s+accordance\s+with', r'(?i)laws\s+of\s+(the\s+state\s+of|the\s+country\s+of|india)', r'(?i)exclusive\s+jurisdiction\s+of\s+the\s+courts']
    },
    "Dispute Resolution": {
        "keywords": ["dispute resolution", "arbitration", "arbitrator", "mediation", "tribunal", "amicable settlement", "dispute", "conciliation"],
        "patterns": [r'(?i)disputes?\s+arising\s+out\s+of', r'(?i)referred\s+to\s+arbitration', r'(?i)rules\s+of\s+arbitration', r'(?i)amicable\s+resolution']
    },
    "Assignment": {
        "keywords": ["assignment", "assign", "delegate", "transfer rights", "successors", "permitted assigns", "without prior written consent"],
        "patterns": [r'(?i)neither\s+party\s+shall\s+assign', r'(?i)without\s+(the\s+)?prior\s+written\s+consent', r'(?i)binding\s+upon\s+and\s+inure\s+to']
    },
    "Obligations": {
        "keywords": ["obligations", "duties", "scope of work", "maintenance", "repairs", "compliance", "shall ensure", "tenant obligations", "contractor duties", "deliverables"],
        "patterns": [r'(?i)shall\s+be\s+responsible\s+for', r'(?i)covenants\s+and\s+agrees', r'(?i)duties\s+and\s+responsibilities', r'(?i)maintenance\s+and\s+repairs']
    },
    "Confidentiality": {
        "keywords": ["confidential", "confidentiality", "proprietary information", "trade secrets", "non-disclosure", "disclose", "recipient", "disclosing party"],
        "patterns": [r'(?i)confidential\s+information', r'(?i)shall\s+not\s+disclose', r'(?i)proprietary\s+information', r'(?i)obligation\s+of\s+confidentiality']
    }
}

def classify_clause(clause_text: str, clause_title: str = "") -> Tuple[str, float]:
    """
    Classifies a clause into one of the 15 CUAD categories with a confidence score.
    Combines heading signals, keyword frequencies, and legal regex patterns.
    """
    text_combined = f"{clause_title} {clause_text}".lower()
    
    best_category = "Obligations"
    best_score = 0.0
    
    for category, config in CATEGORY_SIGNATURES.items():
        score = 0.0
        # Title match has high weight
        title_lower = clause_title.lower()
        if category.lower() in title_lower:
            score += 3.5
            
        # Keyword matches
        for kw in config["keywords"]:
            if kw in text_combined:
                score += 1.0
                
        # Regex patterns
        for pat in config["patterns"]:
            if re.search(pat, text_combined):
                score += 2.5
                
        if score > best_score:
            best_score = score
            best_category = category
            
    # Calculate normalized confidence
    if best_score >= 5.0:
        confidence = min(0.98, 0.85 + (best_score * 0.02))
    elif best_score >= 2.0:
        confidence = min(0.85, 0.70 + (best_score * 0.05))
    elif best_score >= 1.0:
        confidence = 0.65
    else:
        confidence = 0.50
        best_category = "Obligations"  # General fallback
        
    return best_category, round(confidence, 2)

def classify_all_clauses(clauses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Applies clause classification to a list of segmented clauses.
    """
    classified = []
    for c in clauses:
        cat, conf = classify_clause(c.get("text", ""), c.get("title", ""))
        item = dict(c)
        item["clause_type"] = cat
        item["confidence"] = conf
        classified.append(item)
    return classified
