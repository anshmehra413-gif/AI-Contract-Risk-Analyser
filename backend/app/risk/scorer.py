from typing import List, Dict, Any

def compute_normalized_rule_score(risks: List[Dict[str, Any]]) -> float:
    """
    Computes rule score using High=3, Medium=2, Low=1, normalized to 0-100 scale.
    """
    if not risks:
        return 10.0  # Baseline minimal ambient risk
        
    total_points = sum(r.get("score_weight", 1.0) for r in risks)
    # Assume 12 points corresponds to 100 on rule severity
    normalized = min(100.0, (total_points / 10.0) * 100.0)
    return round(normalized, 1)

def compute_ml_score(clauses: List[Dict[str, Any]], risks: List[Dict[str, Any]]) -> float:
    """
    Simulates / computes ML risk model score based on clause category risk priors
    and confidence uncertainties.
    """
    if not clauses:
        return 20.0
        
    # High-risk clause types: Indemnification, Limitation of Liability, Termination, Penalties
    high_risk_categories = {"Indemnification", "Limitation of Liability", "Termination", "Penalties"}
    high_risk_clause_count = sum(1 for c in clauses if c.get("clause_type") in high_risk_categories)
    
    # ML density score
    ratio = high_risk_clause_count / max(1, len(clauses))
    ml_score = min(100.0, max(15.0, ratio * 150.0))
    return round(ml_score, 1)

def compute_llm_assessment_score(risks: List[Dict[str, Any]], rule_score: float) -> float:
    """
    Computes LLM contextual assessment score based on qualitative severity of issues found.
    """
    high_count = sum(1 for r in risks if r.get("risk_level") == "High")
    med_count = sum(1 for r in risks if r.get("risk_level") == "Medium")
    
    if high_count >= 2:
        return round(min(95.0, 65.0 + high_count * 10.0), 1)
    elif high_count == 1:
        return round(min(75.0, 50.0 + med_count * 6.0), 1)
    elif med_count >= 2:
        return round(min(60.0, 35.0 + med_count * 7.0), 1)
    else:
        return round(max(15.0, rule_score * 0.75), 1)

def calculate_hybrid_risk_fusion(
    risks: List[Dict[str, Any]], 
    clauses: List[Dict[str, Any]], 
    missing_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Implements Section 11.3:
    Final Risk Score = 0.40 * Rule Score + 0.30 * ML Score + 0.20 * LLM Assessment + 0.10 * Missing-Clause Score
    """
    rule_score = compute_normalized_rule_score(risks)
    ml_score = compute_ml_score(clauses, risks)
    llm_assessment = compute_llm_assessment_score(risks, rule_score)
    missing_clause_score = missing_analysis.get("missing_clause_score", 15.0)

    # Formula (Section 11.3)
    final_score = (
        0.40 * rule_score +
        0.30 * ml_score +
        0.20 * llm_assessment +
        0.10 * missing_clause_score
    )
    final_score = round(min(100.0, max(0.0, final_score)), 1)

    # Categorization (Section 11.2, Table 5)
    if final_score >= 61.0:
        overall_category = "High"
    elif final_score >= 31.0:
        overall_category = "Medium"
    else:
        overall_category = "Low"

    # Count breakdown
    high_risks = [r for r in risks if r.get("risk_level") == "High"]
    med_risks = [r for r in risks if r.get("risk_level") == "Medium"]
    low_risks = [r for r in risks if r.get("risk_level") == "Low"]

    return {
        "overall_score": final_score,
        "risk_level": overall_category,
        "score_breakdown": {
            "rule_score": rule_score,
            "rule_weight": 0.40,
            "rule_contribution": round(0.40 * rule_score, 1),
            "ml_score": ml_score,
            "ml_weight": 0.30,
            "ml_contribution": round(0.30 * ml_score, 1),
            "llm_score": llm_assessment,
            "llm_weight": 0.20,
            "llm_contribution": round(0.20 * llm_assessment, 1),
            "missing_score": missing_clause_score,
            "missing_weight": 0.10,
            "missing_contribution": round(0.10 * missing_clause_score, 1)
        },
        "counts": {
            "total_risks": len(risks),
            "high": len(high_risks),
            "medium": len(med_risks),
            "low": len(low_risks)
        },
        "high_risk_clause_names": [r["clause_type"] for r in high_risks],
        "medium_risk_clause_names": [r["clause_type"] for r in med_risks],
        "missing_clause_names": [m["name"] for m in missing_analysis.get("missing_clauses", [])]
    }
