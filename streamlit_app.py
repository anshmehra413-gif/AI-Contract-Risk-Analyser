"""
Streamlit Demo UI — Legal Contract Risk Analyzer
=================================================
A clean, presentation-ready dashboard that calls the FastAPI backend
at http://localhost:8000 and renders clause-level risk analysis.

Run with:
    streamlit run streamlit_app.py

Make sure the FastAPI backend is running first:
    cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

import streamlit as st
import requests
import json
from typing import Dict, Any, Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_BASE = "http://localhost:8000/api"

st.set_page_config(
    page_title="Contract Risk Analyzer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS for premium look
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    /* Risk badge pills */
    .risk-high {
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        color: #991b1b;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 13px;
        display: inline-block;
    }
    .risk-medium {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        color: #92400e;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 13px;
        display: inline-block;
    }
    .risk-low {
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        color: #065f46;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 13px;
        display: inline-block;
    }

    /* Score display */
    .big-score {
        font-size: 56px;
        font-weight: 800;
        line-height: 1;
    }
    .score-suffix {
        font-size: 22px;
        color: #94a3b8;
        font-weight: 500;
    }

    /* Card styling */
    .info-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }

    /* Clause expander override */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
    }

    /* Hide default streamlit footer */
    footer {visibility: hidden;}

    /* Divider */
    .section-divider {
        border-top: 2px solid #e2e8f0;
        margin: 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚖️ Contract Risk Analyzer")
    st.markdown("**AI-Powered Legal Analysis**")
    st.markdown("---")
    st.markdown("""
    ### How to use
    1. **Upload** a PDF contract using the file uploader
    2. **Or** select a sample contract to test instantly
    3. **Wait** for the analysis pipeline to complete
    4. **Review** clause-by-clause risk assessment

    ### Supported Domains
    - 🏛️ Legal & Contract Law
    - 🏠 Real Estate Law
    - 🏗️ Construction Law

    ### Pipeline Steps
    1. PDF Text Extraction
    2. Domain Screening
    3. Clause Segmentation
    4. CUAD Classification (15 categories)
    5. Risk Engine (Rules + Missing Clauses)
    6. Hybrid Risk Fusion & Scoring
    7. AI Explainability Layer
    """)
    st.markdown("---")
    st.caption(
        "⚠️ **Academic Prototype** — AI-assisted risk screening only. "
        "Does not constitute legal advice."
    )


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def risk_indicator(level: str) -> str:
    """Returns emoji + level text for display."""
    mapping = {
        "HIGH": "🔴 HIGH",
        "High": "🔴 HIGH",
        "MEDIUM": "🟡 MEDIUM",
        "Medium": "🟡 MEDIUM",
        "LOW": "🟢 LOW",
        "Low": "🟢 LOW",
    }
    return mapping.get(level, f"⚪ {level}")


def risk_badge_html(level: str) -> str:
    """Returns HTML badge for risk level."""
    level_upper = level.upper() if level else "LOW"
    css_class = f"risk-{level_upper.lower()}"
    return f'<span class="{css_class}">{level_upper} RISK</span>'


def score_color(score: float) -> str:
    """Returns hex color based on risk score."""
    if score >= 61:
        return "#ef4444"
    elif score >= 31:
        return "#f59e0b"
    return "#10b981"


def call_api_with_text(filename: str, text: str) -> Optional[Dict[str, Any]]:
    """Calls the /analyze/detailed endpoint with contract text."""
    try:
        resp = requests.post(
            f"{API_BASE}/analyze/detailed",
            json={"filename": filename, "text": text},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.ConnectionError:
        st.error(
            "❌ **Cannot connect to the FastAPI backend.**\n\n"
            "Make sure the server is running:\n"
            "```\ncd backend && python -m uvicorn app.main:app --reload --port 8000\n```"
        )
        return None
    except requests.HTTPError as e:
        st.error(f"❌ API returned error {resp.status_code}: {resp.text}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        return None


def call_api_with_file(file_bytes: bytes, filename: str) -> Optional[Dict[str, Any]]:
    """Calls the /analyze/upload endpoint with a PDF file."""
    try:
        files = {"file": (filename, file_bytes, "application/pdf")}
        resp = requests.post(
            f"{API_BASE}/analyze/upload",
            files=files,
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.ConnectionError:
        st.error(
            "❌ **Cannot connect to the FastAPI backend.**\n\n"
            "Make sure the server is running:\n"
            "```\ncd backend && python -m uvicorn app.main:app --reload --port 8000\n```"
        )
        return None
    except requests.HTTPError as e:
        st.error(f"❌ API returned error {resp.status_code}: {resp.text}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        return None


def load_samples() -> list:
    """Loads sample contracts from the backend."""
    try:
        resp = requests.get(f"{API_BASE}/samples", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Main UI
# ---------------------------------------------------------------------------

st.markdown("# ⚖️ Legal Contract Risk Analyzer")
st.markdown("Upload a contract PDF or choose a sample to get an AI-powered risk assessment.")
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# --- Input section ---
col_upload, col_sample = st.columns([1, 1], gap="large")

analysis_result = None

with col_upload:
    st.markdown("### 📄 Upload Contract PDF")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload a legal contract in PDF format (max 25 MB)",
        key="pdf_uploader",
    )
    if uploaded_file is not None:
        if st.button("🔍 Analyze Uploaded PDF", type="primary", use_container_width=True):
            with st.spinner("⏳ Running full analysis pipeline... This may take a moment."):
                analysis_result = call_api_with_file(
                    uploaded_file.getvalue(), uploaded_file.name
                )

with col_sample:
    st.markdown("### 🧪 Quick Test Samples")
    samples = load_samples()
    if samples:
        sample_options = {s["title"]: s for s in samples}
        selected_title = st.selectbox(
            "Choose a sample contract:",
            options=list(sample_options.keys()),
            key="sample_select",
        )
        selected_sample = sample_options[selected_title]
        st.caption(f"**Domain:** {selected_sample.get('domain', 'N/A')}")
        st.caption(f"**Type:** {selected_sample.get('contract_type', 'N/A')}")

        if st.button("🚀 Analyze Sample", type="primary", use_container_width=True):
            with st.spinner("⏳ Running full analysis pipeline..."):
                analysis_result = call_api_with_text(
                    selected_sample.get("filename", "sample.pdf"),
                    selected_sample.get("text", ""),
                )
    else:
        st.info("Could not load samples. Make sure the backend is running.")


# ---------------------------------------------------------------------------
# Results Display
# ---------------------------------------------------------------------------

if analysis_result is not None:
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Check for rejection
    if analysis_result.get("status") == "Rejected":
        st.error(f"🚫 **Document Rejected:** {analysis_result.get('message', 'Not a supported legal document.')}")
        screening = analysis_result.get("screening", {})
        if screening:
            st.warning(f"**Detected as:** {screening.get('contract_type', 'Unknown')}")
            st.info(f"**Supported domains:** {', '.join(analysis_result.get('supported_domains', []))}")
        st.stop()

    # --- Contract Info Card ---
    st.markdown("## 📋 Analysis Results")

    screening = analysis_result.get("screening", {})
    overall_score = analysis_result.get("overall_score", 0)
    risk_level = analysis_result.get("risk_level", "Low")
    clauses = analysis_result.get("clauses", [])
    risks = analysis_result.get("risks", [])
    risk_summary = analysis_result.get("risk_summary", {})
    missing_analysis = analysis_result.get("missing_analysis", {})

    # --- Top-level metrics ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Domain", screening.get("domain", "N/A"))
    with m2:
        st.metric("Contract Type", screening.get("contract_type", "N/A"))
    with m3:
        st.metric("Pages", analysis_result.get("total_pages", 1))
    with m4:
        st.metric("Confidence", f"{int(screening.get('confidence', 0) * 100)}%")

    st.markdown("")

    # --- Overall Risk Score ---
    score_col, breakdown_col = st.columns([1, 2])

    with score_col:
        color = score_color(overall_score)
        st.markdown(
            f'<div style="text-align:center; padding:20px;">'
            f'<div class="big-score" style="color:{color};">{overall_score}'
            f'<span class="score-suffix">/100</span></div>'
            f'<div style="margin-top:8px;">{risk_badge_html(risk_level)}</div>'
            f'<div style="margin-top:6px; color:#64748b; font-size:13px;">Hybrid Risk Fusion Score</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with breakdown_col:
        score_bd = analysis_result.get("score_breakdown", {})
        if score_bd:
            st.markdown("**Score Breakdown (Hybrid Fusion)**")
            bd_cols = st.columns(4)
            components = [
                ("Rule Engine", score_bd.get("rule_score", 0), "40%"),
                ("ML Score", score_bd.get("ml_score", 0), "30%"),
                ("LLM Assessment", score_bd.get("llm_score", 0), "20%"),
                ("Missing Clauses", score_bd.get("missing_score", 0), "10%"),
            ]
            for i, (label, val, weight) in enumerate(components):
                with bd_cols[i]:
                    st.metric(label, f"{val}", delta=f"Weight: {weight}", delta_color="off")

    # --- Risk Counts ---
    risk_counts = analysis_result.get("risk_counts", {})
    if risk_counts:
        rc1, rc2, rc3, rc4 = st.columns(4)
        with rc1:
            st.metric("Total Risks", risk_counts.get("total_risks", 0))
        with rc2:
            st.metric("🔴 High", risk_counts.get("high", 0))
        with rc3:
            st.metric("🟡 Medium", risk_counts.get("medium", 0))
        with rc4:
            st.metric("🟢 Low", risk_counts.get("low", 0))

    # --- Executive Summary ---
    summary_text = analysis_result.get("summary", "")
    if summary_text:
        st.info(f"**📝 Executive Summary:**\n\n{summary_text}")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # --- Missing Clause Warnings ---
    if risk_summary and risk_summary.get("missing_clauses"):
        st.warning("⚠️ **Missing Clause Warnings**")
        for mc in risk_summary["missing_clauses"]:
            emoji = "🔴" if mc.get("risk_impact") == "HIGH" else "🟡"
            st.markdown(f"  {emoji} **{mc['category']}** — Risk Impact: {mc['risk_impact']}")

    # --- Recommendations ---
    if risk_summary and risk_summary.get("recommendations"):
        st.info("💡 **Recommendations**\n\n" + "\n".join(
            f"- {r}" for r in risk_summary["recommendations"]
        ))

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # --- Clause Table ---
    st.markdown("### 📑 Clause Analysis")

    if clauses:
        # Build a summary table
        table_data = []
        for c in clauses:
            table_data.append({
                "Clause ID": c.get("clause_number", c.get("id", "N/A")),
                "Label": c.get("clause_type", "Unknown"),
                "Confidence": f"{int(c.get('confidence', 0) * 100)}%",
                "Risk Level": c.get("risk_level", "LOW"),
            })
        st.dataframe(
            table_data,
            use_container_width=True,
            column_config={
                "Risk Level": st.column_config.TextColumn(
                    "Risk Level",
                    help="Keyword-based risk assessment",
                ),
            },
        )

        # --- Expandable clause details ---
        st.markdown("### 🔍 Clause Details")
        for clause in clauses:
            clause_label = clause.get("clause_type", "Unknown")
            clause_num = clause.get("clause_number", clause.get("id", "?"))
            risk_lvl = clause.get("risk_level", "LOW")
            indicator = risk_indicator(risk_lvl)

            with st.expander(f"{clause_num} — {clause_label}  |  {indicator}"):
                st.markdown(f"**Full Clause Text:**")
                st.text(clause.get("text", "(no text)"))

                st.markdown("---")
                detail_cols = st.columns(3)
                with detail_cols[0]:
                    st.markdown(f"**Risk Score:** `{clause.get('risk_score', 0)}`")
                with detail_cols[1]:
                    st.markdown(f"**Risk Level:** {indicator}")
                with detail_cols[2]:
                    st.markdown(f"**Confidence:** `{clause.get('confidence', 0)}`")

                factors = clause.get("risk_factors", [])
                if factors:
                    st.markdown("**Risk Factors Found:**")
                    for f in factors:
                        st.markdown(f"  - `{f}`")
                else:
                    st.markdown("_No specific risk patterns matched._")
    else:
        st.warning("No clauses were detected in this document.")

    # --- Enriched Risk Findings ---
    if risks:
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### ⚠️ Detailed Risk Findings")
        for r in risks:
            r_level = r.get("risk_level", "Low")
            indicator = risk_indicator(r_level)
            with st.expander(f"{r.get('risk_type', 'Risk')} — {r.get('clause_number', 'N/A')}  |  {indicator}"):
                st.markdown(f"**Rule:** {r.get('rule_name', 'N/A')}")
                st.markdown(f"**Category:** {r.get('clause_type', 'N/A')}")
                st.markdown(f"**Reason:** {r.get('reason', '')}")

                evidence = r.get("evidence", "")
                if evidence:
                    st.markdown(f'> *"{evidence}"*')

                if r.get("plain_explanation"):
                    st.markdown(f"**What it says:** {r['plain_explanation']}")
                if r.get("risk_reasoning"):
                    st.markdown(f"**Why it's risky:** {r['risk_reasoning']}")
                if r.get("actionable_advice"):
                    st.success(f"💡 **Suggested Action:** {r['actionable_advice']}")

    # --- Disclaimer ---
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.caption(
        "⚠️ **Disclaimer:** AI-Assisted Contract Analysis (Academic/Student Prototype). "
        "This system provides risk screening and explainability for review purposes only "
        "and does not constitute formal legal advice or substitute for a qualified legal practitioner."
    )
