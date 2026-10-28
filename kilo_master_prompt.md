# MASTER PROMPT — Build the ML layer for a Legal Contract Risk Analyzer

## 1. ROLE
You are a senior Python engineer. The frontend and backend of this app are ALREADY
COMPLETE and working. Your only job is to build the machine-learning module and wire
it into the existing backend — WITHOUT breaking anything that already works.

## 2. WHAT THE APP DOES
A user uploads a contract PDF and receives a risk report. The pipeline is:
ingest PDF -> clean text -> split into clauses -> classify each clause into a risk
category -> return structured JSON -> the frontend renders it.

## 3. WHAT ALREADY EXISTS — DO NOT MODIFY
- Frontend (Next.js / React / TypeScript / Tailwind): complete. DO NOT edit any file
  under the frontend directory.
- Backend (FastAPI): complete — upload, storage, status, the analysis endpoint, and
  its response schema.
- The one step that is missing is the ML classification logic behind the analysis
  endpoint (currently a stub / placeholder).

## 4. STEP 0 — INSPECT FIRST (do this before writing any code)
Read the existing backend and report back to me, with file paths and line references:
  a) Which endpoint returns the analysis result (e.g. POST /analyze).
  b) The EXACT JSON response schema it currently returns (paste a real sample).
  c) Where the placeholder / stub result is produced.
  d) How the backend is structured (routes, services, models).
Then STOP and wait for my go-ahead. Do not write code in Step 0.

## 5. YOUR TASK
Build the ML module and integrate it into the existing endpoint:
  1. Ingest a PDF -> raw text
  2. Preprocess text (strip headers/footers/page numbers, fix broken lines)
  3. Segment text into individual clauses
  4. Classify each clause into a risk category (zero-shot + embeddings)
  5. Add cosine-similarity matching and K-Means clustering
  6. Train a classical TF-IDF + classifier baseline on the LEDGAR dataset
  7. Wire the result into the existing analysis endpoint, matching the EXISTING
     response schema EXACTLY.

## 6. LOCKED TECH CONSTRAINTS (do not deviate)
- Python 3.12, FastAPI, Pydantic.
- Allowed libraries ONLY: fastapi, pydantic, pymupdf, sentence-transformers,
  transformers, torch, scikit-learn, pandas, numpy, joblib, datasets.
  Do NOT add any other dependency without asking me first.
- Models: sentence-transformers "all-MiniLM-L6-v2" for embeddings, and
  "facebook/bart-large-mnli" for zero-shot classification. Both self-hosted
  (download weights locally). NO external inference APIs.
- Do NOT train or fine-tune the transformer. Use it pretrained (zero-shot).
  Training is only for the classical baseline in step 6.
- Load models ONCE at server startup as a module-level singleton. NEVER reload a
  model per request.

## 7. MODULE CONTRACTS (exact inputs and outputs)
| Module        | Input          | Library                          | Output                                   |
|---------------|----------------|----------------------------------|------------------------------------------|
| ingest.py     | PDF file path  | pymupdf (fitz)                   | raw_text: str                            |
| preprocess.py | raw_text: str  | re                               | clean_text: str                          |
| segment.py    | clean_text:str | re                               | clauses: list[str]                       |
| classify.py   | clauses:list   | sentence-transformers + transformers | list[dict: text, category, confidence]|
| similarity.py | clause, categories | numpy (cosine)               | list[dict: category, score]              |
| cluster.py    | clauses:list   | scikit-learn (KMeans)            | list[dict: cluster_id, clause]           |

## 8. RESPONSE SCHEMA
The endpoint's response MUST match the schema the backend already returns.
Do NOT invent, rename, or add fields. If you believe a field is missing, ASK me —
do not change the schema on your own.

## 9. DELIVERABLES (create these files)
- backend/ml/__init__.py
- backend/ml/ingest.py
- backend/ml/preprocess.py
- backend/ml/segment.py
- backend/ml/classify.py
- backend/ml/similarity.py
- backend/ml/cluster.py
- backend/ml/models.py        (singleton model loader)
- backend/ml/train_baseline.py
- scripts/download_ledgar.py
- tests/test_pipeline.py
- data/sample_contract.pdf    (I will provide; use for testing)

## 10. ALGORITHMS REQUIRED (this is a graded requirement)
Implement these as clear, named, documented algorithms:
  1. Cosine similarity — match each clause embedding against category embeddings.
  2. K-Means clustering — group clauses into themes (scikit-learn).
  3. TF-IDF + classical classifier — a trainable baseline (SGDClassifier or
     LogisticRegression) trained on LEDGAR, evaluated with accuracy + macro-F1.
     Keep this so we can report "classical baseline vs transformer".

## 11. TRAINING — LEDGAR BASELINE
Download LEDGAR (verified working):
  curl -L https://zenodo.org/records/5532976/files/ledgar.jsonl -o ledgar.jsonl
Load it:
  df = pd.read_json("ledgar.jsonl", lines=True)
  # 80,000 rows; columns: text, year, data_type, clause_type
  # data_type: 60,000 train / 10,000 dev / 10,000 test
  # 100 clause types
Reference baseline (measured on CPU, ~62s, no GPU):
  from sklearn.feature_extraction.text import TfidfVectorizer
  from sklearn.linear_model import SGDClassifier
  from sklearn.pipeline import make_pipeline
  from sklearn.metrics import accuracy_score, f1_score
  clf = make_pipeline(
      TfidfVectorizer(max_features=8000, ngram_range=(1,2), min_df=3),
      SGDClassifier(loss="log_loss", alpha=1e-5, max_iter=30, random_state=0))
  clf.fit(tr["text"], tr["clause_type"])
  # expected: ~0.84 accuracy, ~0.76 macro-F1
Save the trained model with joblib.dump(clf, "backend/ml/baseline.joblib").
NOTE: do NOT use LogisticRegression on the full 100-class set — it exhausts RAM.
Use SGDClassifier.

## 12. INTEGRATION RULES
- Wire the ML call into the EXISTING analysis endpoint.
- Put it behind a flag: USE_REAL_ML = True (env var). If False, keep the old stub.
- Load models at startup, not per request.
- Set a generous request timeout (60s+) for the analysis endpoint.
- Do NOT modify any frontend file. Do NOT refactor existing working code.

## 13. NON-NEGOTIABLES
- Do not touch the frontend.
- Do not change the response schema.
- Do not refactor working backend code.
- One module per step: write it, RUN it, show me the output, then continue.
- Handle failure cases explicitly: empty PDF, no extractable text, zero clauses.
- Type hints on every function. Docstrings on every module.
- Never hardcode API keys, tokens, or secrets.

## 14. BUILD ORDER (one step at a time; run and show output after each)
  Step 0: inspect backend, report seam + schema, then STOP.
  Step 1: scripts/download_ledgar.py — download and verify 80,000 rows.
  Step 2: ingest.py — test on data/sample_contract.pdf, print first 500 chars.
  Step 3: preprocess.py — show before/after on the sample.
  Step 4: segment.py — print the clause list for the sample. Test on 3 real PDFs.
  Step 5: classify.py — run zero-shot on the clauses, print category + confidence.
  Step 6: similarity.py and cluster.py — show outputs on the sample.
  Step 7: train_baseline.py — run it, report accuracy + macro-F1.
  Step 8: models.py — singleton loader, verify server starts fast.
  Step 9: wire into the endpoint behind USE_REAL_ML.
  Step 10: end-to-end test — upload the sample through the API, show the JSON.

## 15. DEFINITION OF DONE
- Uploading a real contract PDF produces a rendered report with per-clause categories.
- train_baseline.py prints accuracy and macro-F1.
- Every module has been run at least once and its output shown.
- No frontend file has changed; the response schema is unchanged.

## 16. START
Begin with Step 0 ONLY. Inspect the backend, report the endpoint, the exact response
schema, and the stub location. Then wait for my go-ahead.
