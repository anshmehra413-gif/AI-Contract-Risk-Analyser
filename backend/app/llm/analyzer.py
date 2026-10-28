import os
import re
from typing import Dict, Any, List
from backend.app.llm.prompts import LEGAL_DISCLAIMER

def generate_clause_explanation(
    clause_type: str,
    risk_level: str,
    evidence: str,
    rule_triggered: str,
    contract_type: str
) -> Dict[str, str]:
    """
    Generates structured plain-language explanation, risk reasoning, and recommended action.
    Implements Section 12.1.
    """
    clean_ev = evidence.strip().replace("...", "").strip()
    
    # Contextual synthesis grounded in legal taxonomy
    if "termination" in clause_type.lower() or "termination" in rule_triggered.lower():
        what_it_says = "This section specifies how and under what conditions the agreement can be ended by either party."
        if risk_level == "High":
            why_risky = (
                f"The provision contains asymmetric cancellation mechanisms (Trigger: '{rule_triggered}'). "
                "One party retains the power to terminate without adequate advance warning or without requiring fault, "
                "which exposes the other party to sudden operational and financial disruption."
            )
            what_to_review = (
                "Request a mandatory bilateral notice period of at least 30 calendar days for convenience, "
                "and stipulate that early termination requires written cure notice and reimbursement of accrued commitments."
            )
        else:
            why_risky = "The termination trigger is somewhat ambiguous regarding default notice and time to cure."
            what_to_review = "Clarify exact number of business days allowed to cure alleged defaults before termination takes effect."
            
    elif "deposit" in rule_triggered.lower() or "security deposit" in clause_type.lower():
        what_it_says = "This clause defines the security deposit sum and conditions under which deductions can be taken."
        why_risky = (
            f"The clause leaves refund timing or deduction standards unspecified (Trigger: '{rule_triggered}'). "
            "Without an explicit statutory or contractual timeline, deposit funds can be withheld indefinitely."
        )
        what_to_review = (
            "Require return of deposit within 14–30 business days following vacancy, supported by itemized repair receipts."
        )
        
    elif "liability" in clause_type.lower() or "liability" in rule_triggered.lower():
        what_it_says = "This clause allocates legal responsibility and financial exposure for contractual breaches or damages."
        if risk_level == "High":
            why_risky = (
                f"The language establishes uncapped or asymmetric liability (Trigger: '{rule_triggered}'). "
                "Without a monetary liability cap, exposure could extend to indirect, consequential, or catastrophic damages."
            )
            what_to_review = (
                "Insert an express monetary cap on total cumulative liability (e.g. 100% of fees paid under this agreement) "
                "and exclude indirect, special, or consequential damages for both parties."
            )
        else:
            why_risky = "The liability scope lacks standard commercial exclusions."
            what_to_review = "Verify whether exclusions for lost profits and third-party claims are mutually applicable."

    elif "indemnif" in clause_type.lower() or "indemnif" in rule_triggered.lower():
        what_it_says = "This clause requires one party to defend and pay for legal claims or losses suffered by the other party."
        why_risky = (
            f"Broad indemnification obligations (Trigger: '{rule_triggered}') create open-ended indemnity exposure "
            "that may force you to cover losses even where you are not primarily or solely at fault."
        )
        what_to_review = (
            "Carve out claims arising from the counterparty's own gross negligence, willful misconduct, or material breach."
        )
        
    elif "penalty" in clause_type.lower() or "penalt" in rule_triggered.lower() or "interest" in rule_triggered.lower():
        what_it_says = "This clause stipulates late payment penalties, default interest rates, or liquidated damages for delays."
        why_risky = (
            f"The penalty structure appears disproportionate or punitive (Trigger: '{rule_triggered}'), "
            "potentially exceeding statutory caps or creating punitive compound interest liabilities."
        )
        what_to_review = (
            "Benchmark late interest against statutory commercial limits (e.g., 1% to 1.5% per month simple interest) "
            "and ensure liquidated damages are accompanied by a reasonable grace period."
        )
        
    elif "missing" in rule_triggered.lower() or "missing" in clause_type.lower():
        what_it_says = f"The contract does not include an explicit clause covering {rule_triggered.replace('Missing Clause: ', '')}."
        why_risky = (
            "Absence of this standard provision creates legal ambiguity and leaves dispute handling or statutory defaults undefined."
        )
        what_to_review = (
            f"Draft and insert a standard industry-recognized clause for {rule_triggered.replace('Missing Clause: ', '')}."
        )
        
    else:
        what_it_says = f"This clause defines key legal rights and covenants regarding {clause_type}."
        why_risky = f"Potential contractual imbalance identified under rule '{rule_triggered}' requiring legal scrutiny."
        what_to_review = "Have legal counsel review the clause wording to ensure balanced, mutual rights."

    return {
        "what_it_says": what_it_says,
        "why_it_is_risky": why_risky,
        "what_to_review": what_to_review,
        "disclaimer": LEGAL_DISCLAIMER
    }

def generate_executive_summary(
    contract_type: str,
    domain: str,
    overall_score: float,
    risk_level: str,
    high_risks: List[str],
    medium_risks: List[str],
    missing_clauses: List[str]
) -> str:
    """
    Generates a concise plain-language executive summary of the entire contract risk profile.
    """
    high_summary = f"{len(high_risks)} High-Risk findings ({', '.join(high_risks[:3])})" if high_risks else "Zero critical high-risk clauses"
    med_summary = f"{len(medium_risks)} Medium-Risk findings" if medium_risks else "no medium-risk findings"
    missing_summary = f"Identified {len(missing_clauses)} missing standard clauses ({', '.join(missing_clauses[:2])})" if missing_clauses else "All expected standard clauses detected"
    
    return (
        f"This document was classified as a {contract_type} under the {domain} domain. "
        f"The system calculated an overall hybrid risk score of {overall_score}/100, placing it in the {risk_level.upper()} RISK tier. "
        f"Key observations include {high_summary}, {med_summary}, and {missing_summary}. "
        f"Prior to signature or execution, targeted negotiation is strongly advised on the flagged one-sided terms."
    )
