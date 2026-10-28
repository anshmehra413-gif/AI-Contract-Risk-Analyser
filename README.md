# LexiRisk AI — Legal Contract Analysis & Risk Detection System

> **Academic / Student Prototype — Mentor Review Version**  
> An AI-Assisted Framework for Contract Understanding, Clause Detection, and Explainable Risk Analysis.  
> *Note: This system provides AI-assisted contract screening and does not provide formal legal advice.*

---

## 🌟 Overview & Proposal Alignment

This working MVP implements the end-to-end architecture outlined in the **AI-Based Legal Contract Analysis and Risk Detection System** project proposal:

1. **PDF Acceptance & Domain Screening (Section 4)**: Filters documents into the 3 supported legal domains (*Legal & Contract Law*, *Real Estate Law*, *Construction Law*) and rejects out-of-domain documents (such as academic research papers or receipts).
2. **Clause Segmentation & Classification (Section 7 & 8)**: Segments contracts into discrete clauses and classifies them into the **15 candidate CUAD categories** (Termination, Liability, Indemnification, Payment, etc.).
3. **Hybrid Risk Engine (Section 9 & 10)**: Combines rule-based risk detection, missing-clause checklist audits, and contractual asymmetry checks.
4. **Hybrid Risk Fusion Scoring (Section 11.3)**:
   $$\text{Final Risk Score} = 0.40 \times \text{Rule Score} + 0.30 \times \text{ML Score} + 0.20 \times \text{LLM Assessment} + 0.10 \times \text{Missing-Clause Score}$$
5. **Evidence-Based Explainability (Section 11.1 & 12.1)**: Every risk finding is linked to an exact evidence chain:  
   $$\text{Risk} \rightarrow \text{Clause} \rightarrow \text{Exact Text Span} \rightarrow \text{Page Number} \rightarrow \text{Reason} \rightarrow \text{Suggested Area for Review}$$
6. **Database Persistence (Section 15)**: Integrated SQLite database storing `contracts`, `clauses`, and `risks` tables.
7. **Frontend Interface (Section 16)**: Dark-mode single-page application featuring the 4 core screens (Upload, Pipeline Stepper, Risk Dashboard, Detailed Clause Inspector) plus a Contract Database History browser and Export Report generator.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.11+** (Tested on Python 3.13)
- Required packages: `fastapi`, `uvicorn`, `python-multipart`, `pypdf`, `python-docx`, `scikit-learn`

### 2. Run the Web Application
Start the backend server with one command from the project root:

```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Then open your browser and navigate to:
👉 **[http://localhost:8000](http://localhost:8000)**

API interactive documentation is available at:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 🧪 Benchmark Test Samples (1-Click Demo)

The application includes 4 pre-configured test contracts directly on the upload screen:
1. **Residential Lease Agreement (Real Estate)**: Demonstrates the Section 17 walkthrough:
   - Security deposit without refund timeline
   - One-sided 24h landlord termination vs 90d tenant termination + penalty
   - Missing dispute resolution clause
   - Evaluated as **High Risk (~71/100)**
2. **Mutual Non-Disclosure Agreement (NDA) (Commercial Law)**:
   - Perpetual confidentiality covenants
   - Uncapped consequential damages
3. **Commercial Subcontractor Agreement (Construction Law)**:
   - Liquidated delay damages ($1,500/day)
   - Broad indemnity regardless of fault
4. **Academic Research Paper (Negative Test - Screening Rejection)**:
   - Triggers the **Domain Screening Rejection Modal** (Section 4.1), notifying the user that the document is out-of-domain and listing the 3 supported legal categories.

---

## 🏗️ Project Architecture & Directory Structure

```
mvpp/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint & static mounting
│   │   ├── database.py              # SQLite database (contracts, clauses, risks tables)
│   │   ├── sample_contracts.py      # Preloaded benchmark contracts
│   │   ├── api/
│   │   │   ├── upload.py            # PDF / DOCX / TXT file upload & validation
│   │   │   ├── analysis.py          # Full 12-stage analysis pipeline
│   │   │   ├── contracts.py         # Stored contracts CRUD & history
│   │   │   └── report.py            # Printable HTML & JSON report generators
│   │   ├── ingestion/
│   │   │   ├── pdf_parser.py        # PyPDF text extractor with page tracking
│   │   │   ├── docx_parser.py       # DOCX extractor
│   │   │   └── ocr.py               # Document readability & OCR validator
│   │   ├── preprocessing/
│   │   │   ├── cleaner.py           # Legal text cleaner & structure normalizer
│   │   │   └── normalizer.py        # Legal numbering normalizer
│   │   ├── screening/
│   │   │   └── domain_classifier.py # Domain screening & acceptance filter
│   │   ├── segmentation/
│   │   │   └── clause_segmenter.py  # Numbered clause & section segmenter
│   │   ├── models/
│   │   │   ├── clause_classifier.py # 15 CUAD category classifier
│   │   │   └── embeddings.py        # Vector representation & similarity
│   │   ├── risk/
│   │   │   ├── rules.py             # Rule-based risk triggers
│   │   │   ├── detector.py          # Evidence-chain risk extractor
│   │   │   ├── missing_clauses.py   # Expected clause checklists
│   │   │   └── scorer.py            # Hybrid risk fusion formula (Section 11.3)
│   │   ├── llm/
│   │   │   ├── prompts.py           # Structured prompts & legal disclaimer
│   │   │   └── analyzer.py          # Grounded plain-language explainability
│   │   ├── reports/
│   │   │   └── generator.py         # Print-ready HTML audit generator
│   │   └── static/
│   │       ├── index.html           # 4-screen Single Page Application
│   │       ├── css/style.css        # Curated dark-mode design system
│   │       └── js/app.js            # Frontend application controller
│   └── tests/
│       └── test_pipeline.py         # Automated integration test suite
└── README.md
```

---

## 📊 Database Schema (Section 15, Table 6)

The application uses SQLite (`backend/app/data/contracts.db`):
- `contracts`: id, filename, contract_type, domain, upload_date, status, overall_score, risk_level, confidence, summary, raw_text, metadata_json.
- `clauses`: id, contract_id, clause_number, clause_type, text, page_number, confidence.
- `risks`: id, contract_id, clause_id, risk_type, risk_level, reason, evidence, recommendation, score_weight.

---

## 🧑‍🏫 How to Present this to your Mentor (Section 23)

1. **Highlight the Explainability & Evidence Chain**: Rather than acting as a black-box "AI lawyer", the system links every flagged risk to an exact quote, page number, reasoning, and suggested review action.
2. **Explain the Hybrid Fusion Formula**: Emphasize how rules, ML models, contextual reasoning, and missing checklist penalties combine into an objective 0–100 score.
3. **Demonstrate Domain Screening Safeguards**: Show how uploading an academic research paper or non-contract document is gracefully detected and rejected, preserving the system's focus on legal contracts.
