# Legal Contract Risk Analyzer — Upgraded MVP

Build an upgraded MVP of a Legal Contract Risk Analyzer. I already have a working backend; upgrade the modules and add a Streamlit UI so I can demo it to my college mentors.

## Existing project

A FastAPI Python project with this pipeline:

**PDF upload → extract text (PyMuPDF) → clean text (regex) → screen domain (zero-shot BART-MNLI) → classify contract type → segment clauses (regex) → classify clauses (zero-shot, 10 labels)**

**Technology:** FastAPI, PyMuPDF, Hugging Face Transformers (`facebook/bart-large-mnli`), Python 3.10+

**Model loading:** Singleton pattern via `get_classifier()` in `domain_screening.py`, reused across all classification tasks.

### Current structure

- `app/extraction.py` — `extract_text_from_pdf(bytes) → list of page dicts`
- `app/preprocessing.py` — `clean_text(str) → str` (7-step regex pipeline)
- `app/domain_screening.py` — `screen_domain()`, `classify_contract_type()`, `get_classifier()`
  - 3 domains, 14 contract subtypes, 0.35 threshold
- `app/segmentation.py` — `segment_clauses(text) → flat list of clause dicts`
- `app/classification.py` — `classify_clauses(clauses) → clauses + label + confidence`
  - 10 labels
- `main.py` — FastAPI app, `POST /analyze` endpoint
- `requirements.txt` — FastAPI, Uvicorn, multipart, PyMuPDF, Transformers, Torch, scikit-learn

## Deliverables

Generate these **8 complete, ready-to-run files**:

1. `app/extraction.py` — light upgrade
2. `app/preprocessing.py` — light upgrade
3. `app/domain_screening.py` — light upgrade
4. `app/segmentation.py` — light upgrade
5. `app/classification.py` — moderate upgrade, including risk scoring
6. `main.py` — updated API with a new endpoint
7. `streamlit_app.py` — new Streamlit web UI
8. `requirements.txt` — updated dependencies

Every file must be complete. Do not use placeholders or `# TODO` stubs.

---

## 1. `app/extraction.py` — Light upgrade

Keep the current PDF extraction approach and add:

- Extract PDF metadata from `doc.metadata`, including `title`, `author`, and `creation_date`.
- Calculate page-level statistics:
  - `word_count`
  - `char_count`
- Return the new format:

```python
{
    "metadata": {...},
    "total_pages": int,
    "pages": [...]
}
```

- `get_full_text()` must support both the old list format and the new dictionary format for backward compatibility.
- Do **not** add OCR.

## 2. `app/preprocessing.py` — Light upgrade

Keep the existing seven-step regex cleaning pipeline and add:

- `clean_text_detailed()` returning:

```python
{
    "cleaned_text": str,
    "stats": {
        "original_length": int,
        "cleaned_length": int,
        "characters_removed": int
    }
}
```

- Keep `clean_text()` unchanged and backward compatible.
- Do **not** add entity normalization or date parsing.

## 3. `app/domain_screening.py` — Light upgrade

Keep the existing singleton model-loading approach and add:

- Expand from 3 to **6 domains**, including:
  - `Intellectual Property Law`
  - `Employment and Labor Law`
  - `Financial and Banking Law`
- Define 3–4 contract subtypes for each of the new domains.
- Return scores for **all** domains:

```python
"domain_scores": {
    "domain1": 0.0,
    "domain2": 0.0
}
```

- Use two-tier confidence thresholds:
  - **HIGH:** score `>= 0.50`
  - **MEDIUM:** score `>= 0.30` and `< 0.50`; set `needs_review=True`
  - **LOW:** score `< 0.30`; mark as rejected
- Do **not** add keyword boosting or language detection.
- Import and reuse `get_classifier()` for classification tasks. Do not load the model more than once.

## 4. `app/segmentation.py` — Light upgrade

Keep the existing regex-based segmentation and add:

- `segment_clauses_detailed()` returning:

```python
{
    "clauses": [...],
    "stats": {
        "total_clauses": int,
        "avg_clause_length": float,
        "shortest_clause_id": str | None,
        "longest_clause_id": str | None
    }
}
```

- Keep `segment_clauses()` unchanged and backward compatible.
- Do **not** add hierarchical clause trees or NLP sentence splitting.

## 5. `app/classification.py` — Moderate upgrade with risk scoring

This is the key upgrade.

### Clause labels

Expand from 10 to **15 labels** by adding:

- `Force Majeure`
- `Intellectual Property`
- `Warranty`
- `Scope of Work / Services`
- `Assignment and Transfer`

Retain all existing labels.

### Keyword-based risk scoring

Define an extensible `RISK_PATTERNS` dictionary rather than hardcoding each category's logic in `if/else` statements.

Use these patterns:

```python
RISK_PATTERNS = {
    "Termination": {
        "high_risk": [
            "without cause",
            "immediate termination",
            "sole discretion",
            "at will"
        ],
        "medium_risk": [
            "30 days notice",
            "written notice"
        ],
        "low_risk": [
            "90 days notice",
            "mutual agreement"
        ]
    },
    "Indemnification": {
        "high_risk": [
            "unlimited liability",
            "all damages",
            "sole expense"
        ],
        "medium_risk": [
            "reasonable costs"
        ],
        "low_risk": [
            "mutual indemnification",
            "capped liability"
        ]
    },
    "Payment": {
        "high_risk": [
            "net 60",
            "net 90",
            "no interest"
        ],
        "medium_risk": [
            "net 30",
            "net 45"
        ],
        "low_risk": [
            "advance payment",
            "net 15",
            "upon receipt"
        ]
    },
    "Confidentiality": {
        "high_risk": [
            "perpetual",
            "no exceptions",
            "unlimited duration"
        ],
        "medium_risk": [
            "5 years",
            "indefinite"
        ],
        "low_risk": [
            "2 years",
            "3 years",
            "standard exceptions"
        ]
    },
    "Limitation of Liability": {
        "high_risk": [
            "no limitation",
            "unlimited",
            "consequential damages"
        ],
        "medium_risk": [
            "limited to fees paid"
        ],
        "low_risk": [
            "capped at",
            "not exceed",
            "aggregate liability"
        ]
    }
}
```

Add similar patterns for at least these categories:

- `Force Majeure`
- `Governing Law`
- `Dispute Resolution`
- `Penalties`

Cover at least **8–10 categories** overall. Make the dictionary easy to extend with new categories and phrases.

### Risk assessment for each clause

After zero-shot clause classification:

1. Scan the clause text in lowercase for phrases listed in `RISK_PATTERNS` for the predicted label.
2. Assign:
   - `risk_score`: float from `0.0` to `1.0`
   - `risk_level`: `LOW`, `MEDIUM`, or `HIGH`
   - `risk_factors`: list of matched phrases
3. Default to **LOW** risk if no patterns match for that category.

Use a consistent score mapping for risk levels, and document it in the code. Avoid presenting this basic keyword score as a legal conclusion.

### Missing-clause detection

After classifying all clauses, check whether these categories are absent:

| Missing category | Risk impact |
|---|---|
| Force Majeure | HIGH |
| Limitation of Liability | HIGH |
| Dispute Resolution | MEDIUM |
| Confidentiality | MEDIUM |

Flag missing categories in the response.

### Contract risk summary

Return a summary with this structure:

```python
{
    "overall_risk_score": float,
    "overall_risk_level": "LOW" | "MEDIUM" | "HIGH",
    "high_risk_count": int,
    "medium_risk_count": int,
    "low_risk_count": int,
    "critical_findings": [str],
    "missing_clauses": [
        {
            "category": str,
            "risk_impact": str
        }
    ],
    "recommendations": [str]
}
```

- Calculate `overall_risk_score` from the average clause risk score plus a documented missing-clause penalty.
- Clamp the final score to `0.0–1.0`.
- Derive `overall_risk_level` consistently from the overall score.
- Include actionable, clearly worded recommendations based on detected risks and missing clauses.
- Handle empty clause lists without division-by-zero errors.

### Required functions

- `classify_clauses(clauses)` — preserve the existing behavior and return shape as closely as possible for backward compatibility.
- `classify_clauses_with_risk(clauses)` — return:

```python
{
    "clauses": [...],
    "risk_summary": {...}
}
```

## 6. `main.py` — Updated API

- Keep existing `POST /analyze` endpoint backward compatible.
- Add `POST /analyze/detailed`, using all detailed functions and including risk analysis in its response.
- Add CORS middleware that allows all origins for the local Streamlit demo.
- Set API version to `2.0.0`.
- Validate uploads and handle edge cases:
  - Empty PDF
  - Non-PDF upload
  - PDF with no extractable text
  - No clauses found
- Return helpful HTTP error messages.
- Reuse the singleton classifier from `domain_screening.py`.

## 7. `streamlit_app.py` — New demo UI

Create a clean Streamlit dashboard with:

- PDF-only file uploader.
- Calls the FastAPI backend at `http://localhost:8000/analyze/detailed`.
- `st.set_page_config(page_title="Contract Risk Analyzer", layout="wide")`.
- Sidebar with app information and instructions.
- Spinner while analysis is processing.
- Contract information card displaying:
  - Domain
  - Contract type
  - Number of pages
  - Confidence
- Overall risk score displayed prominently, with an indicator:
  - 🟢 LOW
  - 🟡 MEDIUM
  - 🔴 HIGH
- Clause table with columns:
  - Clause ID
  - Label
  - Confidence
  - Risk Level
- Visually distinguish risk levels with colored badges or equivalent styling.
- Display missing-clause warnings in an `st.warning()` box.
- Display recommendations in an `st.info()` box.
- Add an expandable `st.expander()` section for each clause, showing:
  - Full clause text
  - Risk factors
  - Risk score and risk level
- Show useful messages for API connection failures, invalid uploads, and empty results.
- Keep the UI suitable for a live college mentor demonstration.

## 8. `requirements.txt`

Include these dependencies:

```text
fastapi
uvicorn[standard]
python-multipart
pymupdf
transformers
torch
scikit-learn
streamlit
requests
```

---

## Exclusions — Leave these for later phases

Do **not** add:

- OCR support
- Entity, date, or currency normalization
- Keyword boosting in domain screening
- Language detection
- Hierarchical clause trees
- NLP sentence splitting
- ML-based risk scoring (keyword-based scoring is sufficient)
- Authentication
- PDF report export
- Database storage
- Multi-language support

## Rules and quality requirements

1. Every file must be complete and ready to run; no placeholders or `# TODO` stubs.
2. Preserve all original function signatures and backwards compatibility.
3. Backend command:

   ```bash
   uvicorn main:app --reload
   ```

4. Frontend command:

   ```bash
   streamlit run streamlit_app.py
   ```

5. Use type hints and docstrings.
6. Risk patterns must be defined in an extensible dictionary, not scattered hardcoded logic.
7. Handle empty PDFs, non-PDF uploads, PDFs without extractable text, and cases where no clauses are found.
8. Import `get_classifier` from `app.domain_screening` and reuse the singleton; do not load the model twice.
9. Keep API response fields consistent and document any compatibility considerations.
10. Treat the risk engine as a **preliminary screening aid**, not legal advice or a substitute for review by a qualified legal professional.

## Expected output format

Output each file with a clear header and the complete code in a fenced code block:

### FILE: `app/extraction.py`

```python
# Complete code here
```

Repeat for all eight files. Do not omit imports, helper functions, error handling, or any required implementation.
