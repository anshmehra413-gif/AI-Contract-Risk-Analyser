import re
from typing import List, Dict, Any, Optional

def extract_evidence_span(text: str, match_pattern: str, max_words: int = 35) -> str:
    """
    Extracts a focused contextual text span around the triggering pattern.
    """
    m = re.search(match_pattern, text, re.IGNORECASE)
    if not m:
        # Return first sentence
        first_period = text.find('.')
        return text[:first_period+1] if first_period > 0 else text[:120]
        
    start_pos = max(0, m.start() - 60)
    end_pos = min(len(text), m.end() + 80)
    snippet = text[start_pos:end_pos].strip()
    return f"...{snippet}..." if start_pos > 0 else f"{snippet}..."

# Rule definitions implementing Section 9.1 and Section 10.1
def check_security_deposit_rules(clause: Dict[str, Any]) -> List[Dict[str, Any]]:
    risks = []
    text = clause.get("text", "")
    text_lower = text.lower()
    
    if "deposit" in text_lower or "security deposit" in text_lower:
        # Check if refund deadline is mentioned (e.g. "within 15 days", "within 30 days")
        has_refund_timeline = bool(re.search(r'(?i)(within\s+\d+\s+days?|refund(ed)?\s+within|returned\s+within)', text_lower))
        has_deduction_clause = bool(re.search(r'(?i)(deduct(ion)?|damages|unpaid\s+rent|forfeit)', text_lower))
        
        if not has_refund_timeline:
            risks.append({
                "rule_name": "Missing Refund Deadline for Security Deposit",
                "risk_type": "Security Deposit Risk",
                "risk_level": "Medium",
                "reason": "Security deposit clause does not specify an explicit deadline or timeline for refunding the deposit upon lease termination.",
                "evidence": extract_evidence_span(text, r'deposit'),
                "recommendation": "Insert a clear refund window (e.g., 'Deposit shall be refunded within 14 to 30 days following vacant possession, subject to itemized deductions')."
            })
            
        # Check for unilateral or undefined deduction powers
        if re.search(r'(?i)(sole\s+discretion|at\s+the\s+landlord[\'’]?s\s+discretion|unconditional\s+forfeiture)', text_lower):
            risks.append({
                "rule_name": "Unilateral Deposit Forfeiture",
                "risk_type": "Financial Risk",
                "risk_level": "High",
                "reason": "The clause grants sole discretion to forfeit or deduct from the security deposit without requiring receipts or mutual inspection.",
                "evidence": extract_evidence_span(text, r'(sole\s+discretion|unconditional\s+forfeiture)'),
                "recommendation": "Require itemized receipts and a joint move-out inspection prior to any deposit deductions."
            })
    return risks

def check_termination_rules(clause: Dict[str, Any]) -> List[Dict[str, Any]]:
    risks = []
    text = clause.get("text", "")
    text_lower = text.lower()
    
    # 1. Immediate termination without cause
    if re.search(r'(?i)(terminate\s+immediately\s+without\s+cause|terminate\s+at\s+any\s+time\s+without\s+notice)', text_lower):
        risks.append({
            "rule_name": "Immediate Termination Without Cause",
            "risk_type": "One-Sided Termination",
            "risk_level": "High",
            "reason": "The clause permits termination immediately without cause, creating severe contractual imbalance and business disruption risk.",
            "evidence": extract_evidence_span(text, r'terminate\s+immediately\s+without\s+cause|terminate\s+at\s+any\s+time\s+without\s+notice'),
            "recommendation": "Require a minimum notice period (e.g. 30 to 60 days) and specify that termination without cause requires compensation."
        })
        
    # 2. One-sided termination right
    if re.search(r'(?i)(landlord\s+may\s+terminate|company\s+may\s+terminate|client\s+may\s+terminate)', text_lower) and not re.search(r'(?i)(tenant\s+may\s+terminate|either\s+party\s+may\s+terminate|contractor\s+may\s+terminate)', text_lower):
        if "terminate" in text_lower and ("sole discretion" in text_lower or "without notice" in text_lower or "at will" in text_lower):
            risks.append({
                "rule_name": "Unilateral Termination Rights",
                "risk_type": "One-Sided Termination",
                "risk_level": "High",
                "reason": "The agreement confers broad termination rights upon one party without equivalent termination protections for the counterparty.",
                "evidence": extract_evidence_span(text, r'(landlord|company|client)\s+may\s+terminate'),
                "recommendation": "Introduce bilateral termination rights and parity in notice periods and cure opportunities."
            })

    # 3. Missing or very short cure period for breach
    if "cure" not in text_lower and re.search(r'(?i)(default|breach|immediate\s+forfeiture)', text_lower):
        if "terminate" in text_lower:
            risks.append({
                "rule_name": "Absence of Cure Period for Breach",
                "risk_type": "Termination Risk",
                "risk_level": "Medium",
                "reason": "No notice-and-cure period is specified prior to termination for default or breach, exposing parties to immediate cancellation.",
                "evidence": extract_evidence_span(text, r'(default|breach)'),
                "recommendation": "Insert a 15-day or 30-day written notice and right to cure before any termination for default becomes effective."
            })
            
    return risks

def check_liability_and_indemnity_rules(clause: Dict[str, Any]) -> List[Dict[str, Any]]:
    risks = []
    text = clause.get("text", "")
    text_lower = text.lower()
    
    # 1. Unlimited liability or absence of monetary liability cap
    if "liable" in text_lower or "liability" in text_lower:
        if re.search(r'(?i)(unlimited\s+liability|without\s+limitation|no\s+limitation\s+of\s+liability)', text_lower):
            risks.append({
                "rule_name": "Unlimited Liability Exposure",
                "risk_type": "Unlimited Liability",
                "risk_level": "High",
                "reason": "The clause explicitly establishes unlimited liability, exposing the party to unbounded financial and consequential claims.",
                "evidence": extract_evidence_span(text, r'(unlimited\s+liability|without\s+limitation)'),
                "recommendation": "Cap aggregate contractual liability to a fixed amount (e.g. fees paid in the past 12 months or total contract value)."
            })
        elif "aggregate liability shall not exceed" not in text_lower and "cap on liability" not in text_lower and len(text) > 150:
            # Check if broad liability is imposed without reciprocal cap
            if re.search(r'(?i)(liable\s+for\s+all\s+damages|responsible\s+for\s+any\s+and\s+all\s+losses)', text_lower):
                risks.append({
                    "rule_name": "Uncapped Consequential Damages",
                    "risk_type": "Liability Risk",
                    "risk_level": "High",
                    "reason": "Broad liability for all damages without standard exclusion of indirect, consequential, or punitive damages.",
                    "evidence": extract_evidence_span(text, r'liable\s+for\s+all\s+damages|responsible\s+for\s+any\s+and\s+all\s+losses'),
                    "recommendation": "Add mutual disclaimer excluding special, incidental, punitive, and consequential damages."
                })

    # 2. Broad or one-sided indemnification
    if "indemnif" in text_lower or "hold harmless" in text_lower:
        if re.search(r'(?i)(sole\s+negligence|gross\s+negligence|any\s+and\s+all\s+claims|regardless\s+of\s+cause)', text_lower):
            risks.append({
                "rule_name": "Broad One-Sided Indemnification",
                "risk_type": "Broad Indemnification",
                "risk_level": "High",
                "reason": "Extremely broad indemnity requiring protection against 'any and all claims' regardless of contributory fault or negligence.",
                "evidence": extract_evidence_span(text, r'(any\s+and\s+all\s+claims|regardless\s+of\s+cause|indemnify)'),
                "recommendation": "Carve out gross negligence, willful misconduct, and breach by the indemnified party."
            })
            
    return risks

def check_payment_and_penalty_rules(clause: Dict[str, Any]) -> List[Dict[str, Any]]:
    risks = []
    text = clause.get("text", "")
    text_lower = text.lower()
    
    # Exorbitant late fee or interest rate (e.g. > 18% or > 2% per month)
    m_interest = re.search(r'(\d+(\.\d+)?)\s*%\s*(per\s+(month|annum|year))?', text_lower)
    if m_interest:
        rate = float(m_interest.group(1))
        period = m_interest.group(4) or ""
        if (period == "month" and rate >= 2.0) or (period in ["annum", "year"] and rate >= 24.0) or rate >= 30.0:
            risks.append({
                "rule_name": "Excessive Interest / Late Penalty",
                "risk_type": "Financial Penalties",
                "risk_level": "High",
                "reason": f"Interest/penalty rate of {rate}% appears punitive and may exceed statutory interest rate ceilings.",
                "evidence": extract_evidence_span(text, r'\d+\s*%\s*(per\s+(month|annum|year))?'),
                "recommendation": "Limit default interest to statutory standard commercial rates (e.g., 1% per month or 12% per annum simple interest)."
            })

    # Liquidated damages without reasonableness qualification
    if "liquidated damages" in text_lower:
        if re.search(r'(?i)(penalty|forfeiture|non-refundable)', text_lower):
            risks.append({
                "rule_name": "Disproportionate Liquidated Damages",
                "risk_type": "Financial Penalties",
                "risk_level": "Medium",
                "reason": "Liquidated damages are phrased as a punitive forfeiture rather than a genuine pre-estimate of actual loss.",
                "evidence": extract_evidence_span(text, r'liquidated\s+damages'),
                "recommendation": "Confirm that liquidated damages represent an agreed genuine pre-estimate of probable loss to ensure enforceability."
            })
            
    return risks

def check_dispute_and_governing_law_rules(clause: Dict[str, Any]) -> List[Dict[str, Any]]:
    risks = []
    text = clause.get("text", "")
    text_lower = text.lower()
    
    # Unclear or ambiguous dispute forum
    if "dispute" in text_lower or "governing law" in text_lower or "jurisdiction" in text_lower:
        # Check if jurisdiction is blank or ambiguous
        if re.search(r'\[.*?\]|_{3,}|\binsert\b|\btbd\b', text_lower):
            risks.append({
                "rule_name": "Unspecified Jurisdiction / Governing Law",
                "risk_type": "Dispute Resolution Risk",
                "risk_level": "Medium",
                "reason": "Jurisdiction or governing law clause contains placeholders, brackets, or unspecified location.",
                "evidence": extract_evidence_span(text, r'\[.*?\]|_{3,}'),
                "recommendation": "Explicitly identify the designated city, state, or court forum with exclusive jurisdiction."
            })
            
    return risks

def check_renewal_rules(clause: Dict[str, Any]) -> List[Dict[str, Any]]:
    risks = []
    text = clause.get("text", "")
    text_lower = text.lower()
    
    if "automatically renew" in text_lower or "auto-renew" in text_lower:
        if not re.search(r'(?i)(written\s+notice|at\s+least\s+\d+\s+days)', text_lower):
            risks.append({
                "rule_name": "Silent Automatic Renewal",
                "risk_type": "Renewal Risk",
                "risk_level": "Medium",
                "reason": "Contract renews automatically without defining a mandatory written opt-out notice window.",
                "evidence": extract_evidence_span(text, r'automatically\s+renew|auto-renew'),
                "recommendation": "Specify that automatic renewal requires 30 to 60 days advance written notice prior to the expiration date."
            })
            
    return risks
