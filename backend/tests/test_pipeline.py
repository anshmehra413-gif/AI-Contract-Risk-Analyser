import os
import sys
from pprint import pprint

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.database import init_db, get_all_contracts, get_contract_by_id
from backend.app.sample_contracts import SAMPLE_CONTRACTS
from backend.app.screening.domain_classifier import classify_domain_and_contract_type
from backend.app.segmentation.clause_segmenter import segment_clauses
from backend.app.models.clause_classifier import classify_all_clauses
from backend.app.risk.detector import detect_risks_in_clauses
from backend.app.risk.scorer import calculate_hybrid_risk_fusion
from backend.app.llm.analyzer import generate_clause_explanation, generate_executive_summary
from backend.app.reports.generator import generate_html_report

def run_tests():
    print("=== TEST 1: Initializing Database ===")
    init_db()
    print("Database initialized successfully.")

    print("\n=== TEST 2: Domain Screening (Section 4) ===")
    for key, sample in SAMPLE_CONTRACTS.items():
        screening = classify_domain_and_contract_type(sample["text"])
        print(f"Sample: {sample['title']}")
        print(f"  -> Status: {screening['status']}")
        print(f"  -> Domain: {screening['domain']}")
        print(f"  -> Contract Type: {screening['contract_type']}")
        print(f"  -> Confidence: {int(screening['confidence']*100)}%")
        if key == "academic_paper":
            assert screening["status"] == "Rejected", "Academic Paper should be Rejected!"
            print("  [PASS] Academic paper correctly rejected!")
        else:
            assert screening["status"] in ["Accepted", "Accepted with warning"], f"{key} should be accepted"
            print("  [PASS] Legal document correctly accepted!")

    print("\n=== TEST 3: Full End-to-End Pipeline on Lease Agreement (Section 17) ===")
    lease_sample = SAMPLE_CONTRACTS["lease_agreement"]
    pages_data = [{"page": 1, "text": lease_sample["text"], "paragraphs": lease_sample["text"].split("\n\n")}]
    
    # 1. Segmentation
    clauses = segment_clauses(pages_data)
    print(f"Segmented {len(clauses)} clauses.")
    assert len(clauses) >= 5, "Should segment at least 5 clauses"

    # 2. Classification
    classified = classify_all_clauses(clauses)
    detected_categories = [c["clause_type"] for c in classified]
    print(f"Classified categories: {detected_categories}")

    # 3. Risk Engine
    detection = detect_risks_in_clauses(classified, lease_sample["contract_type"], lease_sample["text"])
    risks = detection["risks"]
    missing = detection["missing_analysis"]
    print(f"Identified {len(risks)} total risks (including missing clauses).")
    print(f"Missing checklist: {missing['summary_text']}")

    # 4. Scoring & Fusion (Section 11.3)
    fusion = calculate_hybrid_risk_fusion(risks, classified, missing)
    print(f"Overall Score: {fusion['overall_score']}/100 ({fusion['risk_level']} Risk)")
    print(f"Score Breakdown: {fusion['score_breakdown']}")
    assert fusion["overall_score"] > 50, "Lease with one-sided termination & uncapped indemnity should be High/Medium risk"

    # 5. LLM Grounded Explainability (Section 12.1)
    sample_risk = risks[0]
    llm_output = generate_clause_explanation(
        sample_risk["clause_type"],
        sample_risk["risk_level"],
        sample_risk["evidence"],
        sample_risk["rule_name"],
        lease_sample["contract_type"]
    )
    print(f"LLM What It Says: {llm_output['what_it_says']}")
    print(f"LLM Why Risky: {llm_output['why_it_is_risky'][:80]}...")
    print(f"LLM What to Review: {llm_output['what_to_review'][:80]}...")

    # 6. Report Generator
    html_report = generate_html_report({
        "contract_type": lease_sample["contract_type"],
        "domain": lease_sample["domain"],
        "overall_score": fusion["overall_score"],
        "risk_level": fusion["risk_level"],
        "filename": lease_sample["filename"],
        "summary": "Test executive summary"
    }, classified, risks)
    assert len(html_report) > 500, "HTML report should be generated"
    print("HTML Report successfully generated!")

    print("\nALL PIPELINE TESTS PASSED!")

if __name__ == "__main__":
    run_tests()
