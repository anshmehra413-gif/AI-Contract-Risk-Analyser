from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
import re
from datetime import datetime

from backend.app.preprocessing.cleaner import clean_pages, clean_text
from backend.app.screening.domain_classifier import classify_domain_and_contract_type
from backend.app.segmentation.clause_segmenter import segment_clauses
from backend.app.models.clause_classifier import classify_all_clauses
from backend.app.risk.detector import detect_risks_in_clauses
from backend.app.risk.scorer import calculate_hybrid_risk_fusion
from backend.app.llm.analyzer import generate_clause_explanation, generate_executive_summary
from backend.app.database import save_contract_record, get_contract_by_id
from backend.app.ingestion.pdf_parser import extract_text_from_pdf

router = APIRouter(prefix="/api", tags=["Analysis"])

class AnalyzeRequest(BaseModel):
    filename: str
    text: str
    pages: Optional[List[Dict[str, Any]]] = None

# ---------------------------------------------------------------------------
# Keyword-based risk patterns for clause-level risk scoring (MVP Prompt §5)
# ---------------------------------------------------------------------------
RISK_PATTERNS: Dict[str, Dict[str, List[str]]] = {
    "Termination": {
        "high_risk": [
            "without cause", "immediate termination", "sole discretion",
            "at will", "without notice", "24 hours"
        ],
        "medium_risk": [
            "30 days notice", "written notice", "30 days"
        ],
        "low_risk": [
            "90 days notice", "mutual agreement", "either party may terminate"
        ]
    },
    "Indemnification": {
        "high_risk": [
            "unlimited liability", "all damages", "sole expense",
            "any and all claims", "regardless of cause", "regardless of negligence"
        ],
        "medium_risk": [
            "reasonable costs", "direct damages"
        ],
        "low_risk": [
            "mutual indemnification", "capped liability", "proportionate"
        ]
    },
    "Payment": {
        "high_risk": [
            "net 60", "net 90", "no interest", "late fee"
        ],
        "medium_risk": [
            "net 30", "net 45"
        ],
        "low_risk": [
            "advance payment", "net 15", "upon receipt"
        ]
    },
    "Confidentiality": {
        "high_risk": [
            "perpetual", "no exceptions", "unlimited duration", "in perpetuity"
        ],
        "medium_risk": [
            "5 years", "indefinite"
        ],
        "low_risk": [
            "2 years", "3 years", "standard exceptions"
        ]
    },
    "Limitation of Liability": {
        "high_risk": [
            "no limitation", "unlimited", "consequential damages",
            "aggregate liability shall be zero"
        ],
        "medium_risk": [
            "limited to fees paid"
        ],
        "low_risk": [
            "capped at", "not exceed", "aggregate liability"
        ]
    },
    "Force Majeure": {
        "high_risk": [
            "no force majeure", "not excused by"
        ],
        "medium_risk": [
            "reasonable efforts", "best efforts"
        ],
        "low_risk": [
            "force majeure", "act of god", "beyond reasonable control"
        ]
    },
    "Governing Law": {
        "high_risk": [
            "foreign jurisdiction", "exclusive jurisdiction abroad"
        ],
        "medium_risk": [
            "governing law", "laws of"
        ],
        "low_risk": [
            "mutual jurisdiction", "agreed venue"
        ]
    },
    "Dispute Resolution": {
        "high_risk": [
            "litigation only", "no arbitration", "waive right to jury"
        ],
        "medium_risk": [
            "arbitration", "mediation"
        ],
        "low_risk": [
            "amicable settlement", "good faith negotiation", "mutual resolution"
        ]
    },
    "Penalties": {
        "high_risk": [
            "per day of delay", "forfeiture", "liquidated damages"
        ],
        "medium_risk": [
            "late payment charge", "penalty interest"
        ],
        "low_risk": [
            "reasonable penalty", "proportionate"
        ]
    },
    "Renewal": {
        "high_risk": [
            "auto-renew", "automatically renew", "without notice"
        ],
        "medium_risk": [
            "renewal", "extension"
        ],
        "low_risk": [
            "option to renew", "written consent for renewal"
        ]
    }
}

# Missing clause categories and their risk impact
CRITICAL_MISSING_CATEGORIES = {
    "Force Majeure": "HIGH",
    "Limitation of Liability": "HIGH",
    "Dispute Resolution": "MEDIUM",
    "Confidentiality": "MEDIUM",
}


def _score_clause_risk(clause_text: str, clause_label: str) -> Dict[str, Any]:
    """
    Scores clause risk based on keyword pattern matching against RISK_PATTERNS.
    Returns risk_score (0.0–1.0), risk_level, and matched risk_factors.
    """
    text_lower = clause_text.lower()
    patterns = RISK_PATTERNS.get(clause_label, {})
    risk_factors: List[str] = []
    max_tier = "low"

    for phrase in patterns.get("high_risk", []):
        if phrase in text_lower:
            risk_factors.append(phrase)
            max_tier = "high"

    for phrase in patterns.get("medium_risk", []):
        if phrase in text_lower:
            risk_factors.append(phrase)
            if max_tier != "high":
                max_tier = "medium"

    for phrase in patterns.get("low_risk", []):
        if phrase in text_lower:
            risk_factors.append(phrase)

    # Score mapping: HIGH → 0.8–1.0, MEDIUM → 0.4–0.6, LOW → 0.0–0.3
    if max_tier == "high":
        risk_score = min(1.0, 0.8 + len(risk_factors) * 0.05)
        risk_level = "HIGH"
    elif max_tier == "medium":
        risk_score = min(0.6, 0.4 + len(risk_factors) * 0.05)
        risk_level = "MEDIUM"
    else:
        risk_score = min(0.3, 0.1 + len(risk_factors) * 0.05)
        risk_level = "LOW"

    return {
        "risk_score": round(risk_score, 2),
        "risk_level": risk_level,
        "risk_factors": risk_factors,
    }


def _detect_missing_clauses(
    classified_clauses: List[Dict[str, Any]]
) -> List[Dict[str, str]]:
    """
    Checks if critical clause categories are absent from the contract.
    """
    detected_labels = {c.get("clause_type", "") for c in classified_clauses}
    missing: List[Dict[str, str]] = []
    for category, impact in CRITICAL_MISSING_CATEGORIES.items():
        if category not in detected_labels:
            missing.append({"category": category, "risk_impact": impact})
    return missing


def _build_risk_summary(
    clause_risks: List[Dict[str, Any]],
    missing_clauses: List[Dict[str, str]],
) -> Dict[str, Any]:
    """
    Builds the overall contract risk summary with score, counts, and recommendations.
    """
    high_count = sum(1 for c in clause_risks if c.get("risk_level") == "HIGH")
    med_count = sum(1 for c in clause_risks if c.get("risk_level") == "MEDIUM")
    low_count = sum(1 for c in clause_risks if c.get("risk_level") == "LOW")

    # Average clause risk + missing-clause penalty
    if clause_risks:
        avg_score = sum(c.get("risk_score", 0.0) for c in clause_risks) / len(clause_risks)
    else:
        avg_score = 0.0

    missing_penalty = sum(
        0.15 if m["risk_impact"] == "HIGH" else 0.08 for m in missing_clauses
    )
    overall_score = min(1.0, max(0.0, avg_score + missing_penalty))

    if overall_score >= 0.6:
        overall_level = "HIGH"
    elif overall_score >= 0.3:
        overall_level = "MEDIUM"
    else:
        overall_level = "LOW"

    # Generate findings and recommendations
    critical_findings: List[str] = []
    recommendations: List[str] = []

    for c in clause_risks:
        if c.get("risk_level") == "HIGH" and c.get("risk_factors"):
            critical_findings.append(
                f"{c.get('clause_type', 'Unknown')} clause contains high-risk language: "
                f"{', '.join(c['risk_factors'][:3])}"
            )
    for m in missing_clauses:
        critical_findings.append(
            f"Missing {m['category']} clause ({m['risk_impact']} risk impact)"
        )
        recommendations.append(
            f"Add a standard {m['category']} clause to protect both parties."
        )

    if high_count > 0:
        recommendations.append(
            "Have legal counsel review all HIGH-risk clauses before signing."
        )
    if med_count > 0:
        recommendations.append(
            "Negotiate clearer terms for MEDIUM-risk clauses."
        )

    return {
        "overall_risk_score": round(overall_score, 2),
        "overall_risk_level": overall_level,
        "high_risk_count": high_count,
        "medium_risk_count": med_count,
        "low_risk_count": low_count,
        "critical_findings": critical_findings,
        "missing_clauses": missing_clauses,
        "recommendations": recommendations,
    }

@router.post("/screen-domain")
async def screen_domain(payload: Dict[str, str]):
    """
    Step 4: PDF Acceptance and Domain-Screening without full pipeline execution.
    """
    text = payload.get("text", "")
    screening = classify_domain_and_contract_type(text)
    return screening

@router.post("/analyze")
async def analyze_contract(payload: AnalyzeRequest):
    """
    Complete end-to-end legal contract analysis pipeline.
    Executes Sections 4, 7, 8, 9, 10, 11, 12, and saves to database (Section 15).
    """
    contract_id = f"contract-{uuid.uuid4().hex[:8]}"
    filename = payload.filename or "Contract.pdf"
    raw_text = payload.text
    
    # 1. Structure pages
    if payload.pages and len(payload.pages) > 0:
        pages_data = clean_pages(payload.pages)
    else:
        # Generate virtual pages from text paragraphs
        cleaned = clean_text(raw_text)
        paras = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
        pages_data = [{
            "page": 1,
            "text": cleaned,
            "paragraphs": paras
        }]
        
    full_text = "\n\n".join(p["text"] for p in pages_data)
    
    # 2. Step 4: PDF Acceptance and Domain Screening
    screening = classify_domain_and_contract_type(full_text)
    
    # If the document is outright rejected (e.g. Academic Research Paper)
    if screening["status"] == "Rejected":
        contract_record = {
            "id": contract_id,
            "filename": filename,
            "contract_type": screening.get("contract_type", "Non-Legal Document"),
            "domain": screening.get("domain", "Out of Domain"),
            "upload_date": datetime.utcnow().isoformat(),
            "status": "rejected",
            "overall_score": 0.0,
            "risk_level": "None",
            "confidence": screening.get("confidence", 0.0),
            "summary": screening.get("message", "Document rejected during domain screening."),
            "rejection_reason": screening.get("message"),
            "raw_text": full_text[:4000],
            "metadata": {
                "screening": screening,
                "step_reached": "Domain Screening"
            }
        }
        save_contract_record(contract_record, [], [])
        return {
            "contract_id": contract_id,
            "status": "Rejected",
            "is_supported": False,
            "screening": screening,
            "message": screening["message"],
            "supported_domains": screening["supported_domains"]
        }

    # 3. Step 7.4: Clause Segmentation
    raw_clauses = segment_clauses(pages_data)
    
    # 4. Step 8: Clause Classification (15 CUAD categories)
    classified_clauses = classify_all_clauses(raw_clauses)
    
    # 5. Step 9 & 10: Risk Engine (Rules + Missing Clauses)
    contract_type = screening.get("contract_type", "General Commercial Contract")
    detection_result = detect_risks_in_clauses(classified_clauses, contract_type, full_text)
    raw_risks = detection_result["risks"]
    missing_analysis = detection_result["missing_analysis"]
    
    # 6. Step 11: Hybrid Risk Fusion & Scoring
    fusion_result = calculate_hybrid_risk_fusion(raw_risks, classified_clauses, missing_analysis)
    
    # 7. Step 12: LLM Explainability Layer Grounded in Evidence
    enriched_risks = []
    for r in raw_risks:
        llm_exp = generate_clause_explanation(
            clause_type=r["clause_type"],
            risk_level=r["risk_level"],
            evidence=r["evidence"],
            rule_triggered=r["rule_name"],
            contract_type=contract_type
        )
        item = dict(r)
        item["plain_explanation"] = llm_exp["what_it_says"]
        item["risk_reasoning"] = llm_exp["why_it_is_risky"]
        item["actionable_advice"] = llm_exp["what_to_review"]
        enriched_risks.append(item)
        
    # Generate overall executive summary
    exec_summary = generate_executive_summary(
        contract_type=contract_type,
        domain=screening["domain"],
        overall_score=fusion_result["overall_score"],
        risk_level=fusion_result["risk_level"],
        high_risks=fusion_result["high_risk_clause_names"],
        medium_risks=fusion_result["medium_risk_clause_names"],
        missing_clauses=fusion_result["missing_clause_names"]
    )
    
    # 8. Step 15: Save Complete Record to Database
    contract_record = {
        "id": contract_id,
        "filename": filename,
        "contract_type": contract_type,
        "domain": screening["domain"],
        "upload_date": datetime.utcnow().isoformat(),
        "status": "analyzed",
        "overall_score": fusion_result["overall_score"],
        "risk_level": fusion_result["risk_level"],
        "confidence": screening["confidence"],
        "summary": exec_summary,
        "rejection_reason": None,
        "raw_text": full_text[:10000],
        "metadata": {
            "screening": screening,
            "fusion": fusion_result,
            "missing_analysis": missing_analysis,
            "total_clauses": len(classified_clauses),
            "total_risks": len(enriched_risks)
        }
    }
    
    save_contract_record(contract_record, classified_clauses, enriched_risks)
    
    return {
        "contract_id": contract_id,
        "filename": filename,
        "status": "Analyzed",
        "is_supported": True,
        "screening": screening,
        "summary": exec_summary,
        "overall_score": fusion_result["overall_score"],
        "risk_level": fusion_result["risk_level"],
        "score_breakdown": fusion_result["score_breakdown"],
        "risk_counts": fusion_result["counts"],
        "clauses": classified_clauses,
        "risks": enriched_risks,
        "missing_analysis": missing_analysis
    }


@router.post("/analyze/detailed")
async def analyze_contract_detailed(payload: AnalyzeRequest):
    """
    Enhanced analysis endpoint with per-clause risk scoring, missing-clause
    detection, and aggregated risk summary.  Designed for the Streamlit demo UI.
    Backward-compatible: also runs the full existing pipeline internally.
    """
    contract_id = f"contract-{uuid.uuid4().hex[:8]}"
    filename = payload.filename or "Contract.pdf"
    raw_text = payload.text

    # --- Pages ----------------------------------------------------------
    if payload.pages and len(payload.pages) > 0:
        pages_data = clean_pages(payload.pages)
    else:
        cleaned = clean_text(raw_text)
        paras = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
        pages_data = [{"page": 1, "text": cleaned, "paragraphs": paras}]

    full_text = "\n\n".join(p["text"] for p in pages_data)

    # --- Domain screening -----------------------------------------------
    screening = classify_domain_and_contract_type(full_text)

    if screening["status"] == "Rejected":
        return {
            "contract_id": contract_id,
            "status": "Rejected",
            "is_supported": False,
            "screening": screening,
            "message": screening["message"],
            "supported_domains": screening["supported_domains"],
        }

    # --- Segmentation + Classification ----------------------------------
    raw_clauses = segment_clauses(pages_data)
    classified_clauses = classify_all_clauses(raw_clauses)

    # --- Clause-level risk scoring (keyword patterns) -------------------
    for clause in classified_clauses:
        risk_info = _score_clause_risk(
            clause.get("text", ""), clause.get("clause_type", "")
        )
        clause["risk_score"] = risk_info["risk_score"]
        clause["risk_level"] = risk_info["risk_level"]
        clause["risk_factors"] = risk_info["risk_factors"]

    # --- Missing clause detection ---------------------------------------
    missing_clauses = _detect_missing_clauses(classified_clauses)

    # --- Risk summary ---------------------------------------------------
    risk_summary = _build_risk_summary(classified_clauses, missing_clauses)

    # --- Full existing pipeline (for enriched risks & DB) ---------------
    contract_type = screening.get("contract_type", "General Commercial Contract")
    detection_result = detect_risks_in_clauses(classified_clauses, contract_type, full_text)
    raw_risks = detection_result["risks"]
    missing_analysis = detection_result["missing_analysis"]
    fusion_result = calculate_hybrid_risk_fusion(raw_risks, classified_clauses, missing_analysis)

    enriched_risks = []
    for r in raw_risks:
        llm_exp = generate_clause_explanation(
            clause_type=r["clause_type"],
            risk_level=r["risk_level"],
            evidence=r["evidence"],
            rule_triggered=r["rule_name"],
            contract_type=contract_type,
        )
        item = dict(r)
        item["plain_explanation"] = llm_exp["what_it_says"]
        item["risk_reasoning"] = llm_exp["why_it_is_risky"]
        item["actionable_advice"] = llm_exp["what_to_review"]
        enriched_risks.append(item)

    exec_summary = generate_executive_summary(
        contract_type=contract_type,
        domain=screening["domain"],
        overall_score=fusion_result["overall_score"],
        risk_level=fusion_result["risk_level"],
        high_risks=fusion_result["high_risk_clause_names"],
        medium_risks=fusion_result["medium_risk_clause_names"],
        missing_clauses=fusion_result["missing_clause_names"],
    )

    # Save to DB
    contract_record = {
        "id": contract_id,
        "filename": filename,
        "contract_type": contract_type,
        "domain": screening["domain"],
        "upload_date": datetime.utcnow().isoformat(),
        "status": "analyzed",
        "overall_score": fusion_result["overall_score"],
        "risk_level": fusion_result["risk_level"],
        "confidence": screening["confidence"],
        "summary": exec_summary,
        "rejection_reason": None,
        "raw_text": full_text[:10000],
        "metadata": {
            "screening": screening,
            "fusion": fusion_result,
            "missing_analysis": missing_analysis,
            "total_clauses": len(classified_clauses),
            "total_risks": len(enriched_risks),
        },
    }
    save_contract_record(contract_record, classified_clauses, enriched_risks)

    return {
        "contract_id": contract_id,
        "filename": filename,
        "status": "Analyzed",
        "is_supported": True,
        "screening": screening,
        "summary": exec_summary,
        "total_pages": len(pages_data),
        "overall_score": fusion_result["overall_score"],
        "risk_level": fusion_result["risk_level"],
        "score_breakdown": fusion_result["score_breakdown"],
        "risk_counts": fusion_result["counts"],
        "clauses": classified_clauses,
        "risks": enriched_risks,
        "risk_summary": risk_summary,
        "missing_analysis": missing_analysis,
    }


@router.post("/analyze/upload")
async def analyze_uploaded_file(file: UploadFile = File(...)):
    """
    Accepts a PDF file upload, extracts text, and runs the detailed analysis
    pipeline.  Convenience endpoint so the Streamlit UI can upload PDFs directly.
    """
    filename = file.filename or "uploaded.pdf"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ("pdf", "txt"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported by this endpoint.",
        )

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(contents) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 25 MB limit.")

    if ext == "pdf":
        pages_data = extract_text_from_pdf(contents)
        pages_data = clean_pages(pages_data)
        full_text = "\n\n".join(p["text"] for p in pages_data)
        if not full_text.strip():
            raise HTTPException(
                status_code=422,
                detail="Could not extract any text from the PDF. It may be a scanned/image-only document.",
            )
    else:
        full_text = contents.decode("utf-8", errors="ignore")
        pages_data = [
            {"page": 1, "text": full_text, "paragraphs": full_text.split("\n\n")}
        ]

    # Re-use the detailed analysis logic via internal call
    payload = AnalyzeRequest(filename=filename, text=full_text)
    return await analyze_contract_detailed(payload)

