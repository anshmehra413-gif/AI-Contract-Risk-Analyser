import uuid
from typing import List, Dict, Any
from backend.app.risk.rules import (
    check_security_deposit_rules,
    check_termination_rules,
    check_liability_and_indemnity_rules,
    check_payment_and_penalty_rules,
    check_dispute_and_governing_law_rules,
    check_renewal_rules
)
from backend.app.risk.missing_clauses import check_missing_clauses

def detect_risks_in_clauses(
    clauses: List[Dict[str, Any]], 
    contract_type: str, 
    full_text: str
) -> Dict[str, Any]:
    """
    Executes rule engine across all clauses and identifies risks with exact evidence chains.
    Implements Section 9 (Risk Engine) and Section 11.1 (Evidence Chain).
    """
    identified_risks = []
    
    # Process each clause through rule checkers
    for clause in clauses:
        clause_id = clause.get("id")
        page_num = clause.get("page_number", 1)
        clause_num = clause.get("clause_number", "")
        
        # Rule checks
        rule_findings = []
        rule_findings.extend(check_security_deposit_rules(clause))
        rule_findings.extend(check_termination_rules(clause))
        rule_findings.extend(check_liability_and_indemnity_rules(clause))
        rule_findings.extend(check_payment_and_penalty_rules(clause))
        rule_findings.extend(check_dispute_and_governing_law_rules(clause))
        rule_findings.extend(check_renewal_rules(clause))
        
        for finding in rule_findings:
            # Map into database risk item
            risk_id = f"risk-{uuid.uuid4().hex[:8]}"
            weight = 3.0 if finding["risk_level"] == "High" else (2.0 if finding["risk_level"] == "Medium" else 1.0)
            identified_risks.append({
                "id": risk_id,
                "clause_id": clause_id,
                "clause_number": clause_num,
                "clause_type": clause.get("clause_type", "General"),
                "page_number": page_num,
                "risk_type": finding["risk_type"],
                "risk_level": finding["risk_level"],
                "reason": finding["reason"],
                "evidence": finding["evidence"],
                "recommendation": finding["recommendation"],
                "rule_name": finding["rule_name"],
                "score_weight": weight
            })

    # Missing clause detection (Section 10.2)
    missing_analysis = check_missing_clauses(contract_type, clauses, full_text)
    
    for mr in missing_analysis["missing_risks"]:
        risk_id = f"risk-{uuid.uuid4().hex[:8]}"
        identified_risks.append({
            "id": risk_id,
            "clause_id": None,
            "clause_number": "Missing Checklist Item",
            "clause_type": "Missing Clause",
            "page_number": 1,
            "risk_type": mr["risk_type"],
            "risk_level": mr["risk_level"],
            "reason": mr["reason"],
            "evidence": mr["evidence"],
            "recommendation": mr["recommendation"],
            "rule_name": mr["rule_name"],
            "score_weight": 2.0 if mr["risk_level"] == "Medium" else 1.0
        })

    return {
        "risks": identified_risks,
        "missing_analysis": missing_analysis
    }
