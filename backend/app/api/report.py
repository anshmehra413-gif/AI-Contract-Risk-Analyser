from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from backend.app.database import get_contract_by_id
from backend.app.reports.generator import generate_html_report

router = APIRouter(prefix="/api/reports", tags=["Reports & Exports"])

@router.get("/{contract_id}/html", response_class=HTMLResponse)
async def get_report_html(contract_id: str):
    """
    Renders exportable HTML/print report for mentor review and audit.
    """
    record = get_contract_by_id(contract_id)
    if not record:
        raise HTTPException(status_code=404, detail="Contract not found.")
        
    html = generate_html_report(record["contract"], record["clauses"], record["risks"])
    return HTMLResponse(content=html, status_code=200)

@router.get("/{contract_id}/json")
async def get_report_json(contract_id: str):
    """
    Returns full contract audit report payload as structured JSON.
    """
    record = get_contract_by_id(contract_id)
    if not record:
        raise HTTPException(status_code=404, detail="Contract not found.")
    return JSONResponse(content=record, status_code=200)
