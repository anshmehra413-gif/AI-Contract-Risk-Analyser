from typing import Dict, Any, List
from datetime import datetime
from backend.app.llm.prompts import LEGAL_DISCLAIMER

def generate_html_report(contract_data: Dict[str, Any], clauses: List[Dict[str, Any]], risks: List[Dict[str, Any]]) -> str:
    """
    Generates a professional, print-ready HTML/PDF report suitable for mentor review and legal audit.
    """
    contract_type = contract_data.get("contract_type", "Legal Document")
    domain = contract_data.get("domain", "General Law")
    score = contract_data.get("overall_score", 0.0)
    risk_level = contract_data.get("risk_level", "Low")
    upload_date = contract_data.get("upload_date", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))
    filename = contract_data.get("filename", "Contract")
    summary = contract_data.get("summary", "")
    
    score_color = "#ef4444" if risk_level == "High" else ("#f59e0b" if risk_level == "Medium" else "#10b981")
    
    # Render risk items
    risk_rows = ""
    for r in risks:
        level = r.get("risk_level", "Low")
        badge_bg = "#fee2e2" if level == "High" else ("#fef3c7" if level == "Medium" else "#e0f2fe")
        badge_color = "#b91c1c" if level == "High" else ("#b45309" if level == "Medium" else "#0369a1")
        
        risk_rows += f"""
        <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px; margin-bottom: 16px; background: #fafafa;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h3 style="margin: 0; font-size: 16px; color: #0f172a;">{r.get('risk_type')}</h3>
                <span style="background: {badge_bg}; color: {badge_color}; padding: 4px 10px; border-radius: 9999px; font-weight: 600; font-size: 12px;">{level} RISK</span>
            </div>
            <p style="margin: 4px 0 8px 0; font-size: 13px; color: #475569;">
                <strong>Clause:</strong> {r.get('clause_number', 'N/A')} &nbsp;|&nbsp; <strong>Category:</strong> {r.get('clause_type', 'General')} &nbsp;|&nbsp; <strong>Source Page:</strong> Page {r.get('page_number', 1)}
            </p>
            <div style="background: #ffffff; border-left: 4px solid #3b82f6; padding: 10px 14px; margin: 10px 0; font-style: italic; font-size: 13px; color: #334155;">
                "{r.get('evidence', '')}"
            </div>
            <p style="margin: 8px 0 4px 0; font-size: 13px; color: #1e293b;">
                <strong>Why Risky:</strong> {r.get('reason', '')}
            </p>
            <p style="margin: 4px 0 0 0; font-size: 13px; color: #047857;">
                <strong>Suggested Review:</strong> {r.get('recommendation', '')}
            </p>
        </div>
        """
        
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Legal Contract Audit Report - {filename}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.5; color: #0f172a; margin: 0; padding: 30px; }}
        .header {{ border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 25px; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 9999px; font-weight: 600; font-size: 12px; }}
        .metric-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 20px; }}
        .footer {{ margin-top: 40px; padding-top: 15px; border-top: 1px solid #e2e8f0; font-size: 11px; color: #64748b; text-align: center; }}
        @media print {{ body {{ padding: 0; }} }}
    </style>
</head>
<body>
    <div class="header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin: 0; font-size: 24px; color: #1e293b;">AI Legal Contract Audit Report</h1>
                <p style="margin: 5px 0 0 0; color: #64748b; font-size: 13px;">Document: <strong>{filename}</strong> | Generated: {upload_date}</p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 32px; font-weight: 800; color: {score_color};">{score}<span style="font-size: 18px; color: #94a3b8;">/100</span></div>
                <div style="font-weight: 600; font-size: 14px; color: {score_color};">{risk_level.upper()} RISK</div>
            </div>
        </div>
    </div>

    <div class="metric-card">
        <h3 style="margin: 0 0 8px 0; font-size: 15px; color: #334155;">Domain & Classification</h3>
        <p style="margin: 0; font-size: 14px;"><strong>Domain:</strong> {domain} &nbsp;|&nbsp; <strong>Contract Type:</strong> {contract_type}</p>
        <p style="margin: 10px 0 0 0; font-size: 13px; color: #475569;"><strong>Executive Summary:</strong> {summary}</p>
    </div>

    <h2 style="font-size: 18px; color: #1e293b; margin: 25px 0 15px 0;">Identified Risk Findings ({len(risks)})</h2>
    {risk_rows}

    <div class="footer">
        <p><strong>Disclaimer:</strong> {LEGAL_DISCLAIMER}</p>
        <p>AI-Assisted Legal Contract Analysis & Risk Detection System &bull; Academic Mentor Review Prototype</p>
    </div>
</body>
</html>
    """
    return html
