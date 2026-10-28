from typing import List, Dict, Any

# Expected clause checklists (Section 10.2)
EXPECTED_CLAUSE_CHECKLISTS = {
    "Lease Agreement": [
        {"name": "Parties", "cuad_category": "Parties", "importance": "Critical"},
        {"name": "Property Description", "cuad_category": "Obligations", "importance": "Critical"},
        {"name": "Rent", "cuad_category": "Payment", "importance": "Critical"},
        {"name": "Security Deposit", "cuad_category": "Payment", "importance": "High"},
        {"name": "Lease Duration / Term", "cuad_category": "Effective Date", "importance": "Critical"},
        {"name": "Termination", "cuad_category": "Termination", "importance": "High"},
        {"name": "Maintenance", "cuad_category": "Obligations", "importance": "Medium"},
        {"name": "Repairs", "cuad_category": "Obligations", "importance": "Medium"},
        {"name": "Renewal", "cuad_category": "Renewal", "importance": "Medium"},
        {"name": "Notice", "cuad_category": "Notice", "importance": "Medium"},
        {"name": "Dispute Resolution", "cuad_category": "Dispute Resolution", "importance": "High"},
        {"name": "Governing Law", "cuad_category": "Governing Law", "importance": "High"}
    ],
    "Non-Disclosure Agreement (NDA)": [
        {"name": "Parties", "cuad_category": "Parties", "importance": "Critical"},
        {"name": "Definition of Confidential Information", "cuad_category": "Confidentiality", "importance": "Critical"},
        {"name": "Non-Disclosure Obligations", "cuad_category": "Confidentiality", "importance": "Critical"},
        {"name": "Exclusions from Confidentiality", "cuad_category": "Confidentiality", "importance": "High"},
        {"name": "Term and Duration", "cuad_category": "Expiration Date", "importance": "High"},
        {"name": "Return or Destruction of Materials", "cuad_category": "Obligations", "importance": "Medium"},
        {"name": "Remedies and Injunction", "cuad_category": "Penalties", "importance": "Medium"},
        {"name": "Governing Law", "cuad_category": "Governing Law", "importance": "High"},
        {"name": "Dispute Resolution", "cuad_category": "Dispute Resolution", "importance": "High"}
    ],
    "Subcontractor Agreement": [
        {"name": "Parties", "cuad_category": "Parties", "importance": "Critical"},
        {"name": "Scope of Work", "cuad_category": "Obligations", "importance": "Critical"},
        {"name": "Payment & Retention Terms", "cuad_category": "Payment", "importance": "Critical"},
        {"name": "Liquidated Damages / Penalties", "cuad_category": "Penalties", "importance": "High"},
        {"name": "Indemnification", "cuad_category": "Indemnification", "importance": "High"},
        {"name": "Limitation of Liability", "cuad_category": "Limitation of Liability", "importance": "High"},
        {"name": "Defects Liability & Warranty", "cuad_category": "Obligations", "importance": "High"},
        {"name": "Termination", "cuad_category": "Termination", "importance": "High"},
        {"name": "Dispute Resolution & Arbitration", "cuad_category": "Dispute Resolution", "importance": "High"},
        {"name": "Governing Law", "cuad_category": "Governing Law", "importance": "High"}
    ],
    "General Commercial Contract": [
        {"name": "Parties", "cuad_category": "Parties", "importance": "Critical"},
        {"name": "Effective Date", "cuad_category": "Effective Date", "importance": "Critical"},
        {"name": "Obligations / Scope", "cuad_category": "Obligations", "importance": "Critical"},
        {"name": "Payment Terms", "cuad_category": "Payment", "importance": "High"},
        {"name": "Termination", "cuad_category": "Termination", "importance": "High"},
        {"name": "Indemnification", "cuad_category": "Indemnification", "importance": "High"},
        {"name": "Limitation of Liability", "cuad_category": "Limitation of Liability", "importance": "High"},
        {"name": "Dispute Resolution", "cuad_category": "Dispute Resolution", "importance": "High"},
        {"name": "Governing Law", "cuad_category": "Governing Law", "importance": "High"}
    ]
}

def check_missing_clauses(contract_type: str, detected_clauses: List[Dict[str, Any]], full_text: str) -> Dict[str, Any]:
    """
    Compares detected clauses against the expected clause checklist for the contract type.
    Implements Section 10.2: Missing-Clause Detection.
    """
    checklist = EXPECTED_CLAUSE_CHECKLISTS.get(contract_type, EXPECTED_CLAUSE_CHECKLISTS["General Commercial Contract"])
    
    detected_categories = {c.get("clause_type") for c in detected_clauses}
    detected_titles = " ".join([c.get("title", "") + " " + c.get("text", "") for c in detected_clauses]).lower()
    full_text_lower = full_text.lower()
    
    found_items = []
    missing_items = []
    
    for item in checklist:
        name = item["name"]
        cat = item["cuad_category"]
        
        # Check if CUAD category detected or if specific keyword appears in text
        is_found = False
        if cat in detected_categories:
            is_found = True
        elif name.lower() in detected_titles or name.lower() in full_text_lower:
            is_found = True
        elif cat == "Dispute Resolution" and ("arbitration" in full_text_lower or "mediation" in full_text_lower or "dispute" in full_text_lower):
            is_found = True
        elif cat == "Governing Law" and ("governing law" in full_text_lower or "jurisdiction" in full_text_lower):
            is_found = True
        elif cat == "Renewal" and ("renew" in full_text_lower or "extension" in full_text_lower):
            is_found = True
            
        if is_found:
            found_items.append(item)
        else:
            missing_items.append(item)
            
    total = len(checklist)
    detected_count = len(found_items)
    
    # Calculate missing clause risk score (0-100)
    # Critical missing clauses have higher weight
    missing_penalty = 0
    for m in missing_items:
        if m["importance"] == "Critical":
            missing_penalty += 25
        elif m["importance"] == "High":
            missing_penalty += 15
        else:
            missing_penalty += 8
            
    missing_score = min(100.0, float(missing_penalty))
    
    # Format missing clause risks
    missing_risks = []
    for m in missing_items:
        missing_risks.append({
            "rule_name": f"Missing Clause: {m['name']}",
            "risk_type": "Missing Clause Risk",
            "risk_level": "Medium" if m["importance"] in ["High", "Critical"] else "Low",
            "reason": f"Expected clause '{m['name']}' was not identified in the contract. While not necessarily invalidating, this creates ambiguity or unallocated risk.",
            "evidence": f"Expected in standard {contract_type} checklist",
            "recommendation": f"Add a standard '{m['name']}' clause to ensure comprehensive coverage under {contract_type} norms."
        })
        
    return {
        "total_expected": total,
        "detected_count": detected_count,
        "summary_text": f"Detected {detected_count}/{total} expected clauses",
        "found_clauses": found_items,
        "missing_clauses": missing_items,
        "missing_risks": missing_risks,
        "missing_clause_score": missing_score
    }
