import re
from typing import Dict, Any, Tuple

# Domain 1: Real Estate Law and Property Transactions
REAL_ESTATE_KEYWORDS = [
    "lease", "tenant", "landlord", "premises", "rent", "lessor", "lessee",
    "rental agreement", "sublease", "security deposit", "demised premises",
    "property purchase", "real estate", "property transfer", "deed", "conveyance",
    "easement", "title deed", "landlord and tenant", "habitable condition",
    "fixtures and fittings", "property tax", "land purchase"
]

# Domain 2: Construction Law and Contracts
CONSTRUCTION_KEYWORDS = [
    "contractor", "subcontractor", "work order", "epc", "engineering", "procurement",
    "construction", "architect", "specifications", "bill of quantities", "boq",
    "defects liability", "liquidated damages", "completion certificate", "variation order",
    "site conditions", "workmanship", "subcontract", "retention money", "milestone payment",
    "scope of work", "drawings and plans", "structural", "safety manual"
]

# Domain 3: Legal and Contract Law (General / Commercial / Corporate)
GENERAL_LEGAL_KEYWORDS = [
    "agreement", "contract", "parties", "confidentiality", "nda", "non-disclosure",
    "employment agreement", "service agreement", "consulting agreement", "vendor",
    "intellectual property", "governing law", "jurisdiction", "indemnification",
    "limitation of liability", "termination", "severability", "arbitration",
    "whereas", "in witness whereof", "covenant", "warranties", "representations",
    "partnership agreement", "sale agreement", "commercial contract", "force majeure"
]

# Non-legal patterns to trigger rejection
NON_LEGAL_INDICATORS = [
    "abstract", "introduction", "methodology", "literature review", "references", "ieee",
    "arxiv", "conclusion", "experimental results", "dataset", "neural network",
    "invoice", "billed to", "total due", "subtotal", "tax invoice", "receipt",
    "medical history", "diagnosis", "prescription", "patient", "clinical trial",
    "dear mom", "recipe", "ingredients", "tablespoon", "cooking time"
]

def classify_domain_and_contract_type(text: str) -> Dict[str, Any]:
    """
    Evaluates contract text against the 3 supported domains and contract types.
    Implements Section 4: PDF Acceptance and Domain-Screening.
    """
    text_lower = text.lower()
    total_length = len(text_lower)
    
    if total_length < 60:
        return {
            "status": "Rejected",
            "domain": "Unknown / Insufficient Text",
            "contract_type": "Unknown",
            "confidence": 0.10,
            "message": "The document contains insufficient text to determine legal validity.",
            "is_supported": False,
            "supported_domains": [
                "Legal and Contract Law",
                "Real Estate Law and Property Transactions",
                "Construction Law and Contracts"
            ]
        }

    # Count domain keyword occurrences
    re_score = sum(1 for kw in REAL_ESTATE_KEYWORDS if kw in text_lower)
    const_score = sum(1 for kw in CONSTRUCTION_KEYWORDS if kw in text_lower)
    gen_score = sum(1 for kw in GENERAL_LEGAL_KEYWORDS if kw in text_lower)
    non_legal_score = sum(2 for kw in NON_LEGAL_INDICATORS if re.search(r'\b' + re.escape(kw) + r'\b', text_lower))

    # Check for formal legal contract preamble ("This Agreement", "BY AND BETWEEN", "NOW THEREFORE")
    has_preamble = bool(re.search(r'(?i)(this\s+agreement|by\s+and\s+between|entered\s+into|now\s+therefore|witnesseth)', text_lower))
    has_clauses = bool(re.search(r'(?i)(section\s+\d+|clause\s+\d+|article\s+[ivxlc\d]+|\b1\.\d+)', text_lower))

    # Reject non-legal documents (Section 4.1 example: Academic Research Paper)
    if non_legal_score >= 4 and not has_preamble:
        detected_doc = "Academic Research Paper / Technical Article" if "abstract" in text_lower or "references" in text_lower else "Non-Legal Document"
        return {
            "status": "Rejected",
            "domain": "Non-Legal / Academic",
            "contract_type": detected_doc,
            "confidence": round(min(0.95, 0.40 + (non_legal_score * 0.1)), 2),
            "message": f"Detected document appears to be '{detected_doc}'. The system does not appear to recognize this document as belonging to the supported legal domains.",
            "is_supported": False,
            "supported_domains": [
                "Legal and Contract Law (e.g., NDA, Service, Commercial, Employment)",
                "Real Estate Law and Property Transactions (e.g., Lease, Property Sale)",
                "Construction Law and Contracts (e.g., EPC, Subcontractor, Work Orders)"
            ]
        }

    # Classify into specific contract types and domain
    domain = "Legal and Contract Law"
    contract_type = "Commercial Contract"
    confidence = 0.70

    if re_score > const_score and re_score >= 3:
        domain = "Real Estate Law and Property Transactions"
        if "lease" in text_lower or "tenant" in text_lower or "rental" in text_lower:
            contract_type = "Lease Agreement"
        elif "purchase" in text_lower or "deed" in text_lower:
            contract_type = "Property Purchase Agreement"
        else:
            contract_type = "Real Estate Agreement"
        confidence = min(0.96, 0.65 + (re_score * 0.05))
        
    elif const_score > re_score and const_score >= 3:
        domain = "Construction Law and Contracts"
        if "subcontract" in text_lower or "subcontractor" in text_lower:
            contract_type = "Subcontractor Agreement"
        elif "epc" in text_lower:
            contract_type = "EPC Construction Contract"
        else:
            contract_type = "Construction Service Contract"
        confidence = min(0.95, 0.65 + (const_score * 0.05))
        
    else:
        domain = "Legal and Contract Law"
        if "non-disclosure" in text_lower or "confidentiality" in text_lower or "nda" in text_lower:
            contract_type = "Non-Disclosure Agreement (NDA)"
        elif "employment" in text_lower or "employee" in text_lower:
            contract_type = "Employment Agreement"
        elif "service" in text_lower or "services" in text_lower:
            contract_type = "Master Services Agreement"
        elif "partnership" in text_lower:
            contract_type = "Partnership Agreement"
        else:
            contract_type = "General Commercial Contract"
        confidence = min(0.94, 0.60 + (gen_score * 0.04))

    # Adjust confidence if preamble or legal numbering missing
    if not has_preamble:
        confidence = max(0.40, confidence - 0.20)
    if not has_clauses:
        confidence = max(0.45, confidence - 0.15)

    # Determine 3-state acceptance status (Section 4.1)
    if confidence >= 0.75:
        status = "Accepted"
        message = f"Document accepted for full legal analysis under domain '{domain}' with {int(confidence*100)}% confidence."
        is_supported = True
    elif confidence >= 0.50:
        status = "Accepted with warning"
        message = f"Some uncertainty exists regarding domain classification ({int(confidence*100)}% confidence). Proceeding with general contract analysis."
        is_supported = True
    else:
        status = "Rejected"
        message = "The document does not appear to belong to the supported legal domains (Real Estate, Construction, or Contract Law)."
        is_supported = False

    return {
        "status": status,
        "domain": domain,
        "contract_type": contract_type,
        "confidence": round(confidence, 2),
        "message": message,
        "is_supported": is_supported,
        "supported_domains": [
            "Legal and Contract Law",
            "Real Estate Law and Property Transactions",
            "Construction Law and Contracts"
        ]
    }
