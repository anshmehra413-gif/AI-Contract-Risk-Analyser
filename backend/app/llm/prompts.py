LEGAL_DISCLAIMER = (
    "AI-Assisted Contract Analysis (Academic/Student Prototype). "
    "This system provides risk screening and explainability for review purposes only "
    "and does not constitute formal legal advice or substitute for a qualified legal practitioner."
)

SYSTEM_PROMPT = f"""You are a specialized Legal Contract Analysis Assistant.
Your task is to analyze contract clauses given structured evidence and generate three clear outputs:
1. Plain-Language Explanation: What the clause actually says in simple terms.
2. Risk Analysis: Why this clause is risky or potentially unbalanced for the counterparty.
3. Suggested Review Actions: Concrete, actionable changes or questions to raise with legal counsel.

Ground all explanations directly in the provided evidence. Do not extrapolate or hallucinate facts outside the contract text.
Always include the standard disclaimer: "{LEGAL_DISCLAIMER}"
"""

def build_clause_prompt(clause_type: str, risk_level: str, evidence: str, rule_triggered: str, contract_type: str) -> str:
    return f"""Analyze the following contract clause:
- Contract Type: {contract_type}
- Clause Category: {clause_type}
- Identified Risk Level: {risk_level}
- Triggered Rule: {rule_triggered}
- Supporting Evidence Text: "{evidence}"

Provide your assessment in the following format:
WHAT IT SAYS: <concise plain English summary>
WHY IT IS RISKY: <specific explanation of risk and potential negative impact>
WHAT TO REVIEW: <actionable advice or proposed revision>
DISCLAIMER: {LEGAL_DISCLAIMER}
"""
