from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from backend.app.database import get_all_contracts, get_contract_by_id, delete_contract
from backend.app.sample_contracts import SAMPLE_CONTRACTS

router = APIRouter(prefix="/api", tags=["Contracts Database & Samples"])

@router.get("/samples")
async def list_sample_contracts() -> List[Dict[str, Any]]:
    """
    Returns pre-loaded sample contracts representing the 3 supported domains
    and the out-of-domain negative test.
    """
    samples = []
    for key, val in SAMPLE_CONTRACTS.items():
        samples.append({
            "key": key,
            "id": val["id"],
            "title": val["title"],
            "filename": val["filename"],
            "domain": val["domain"],
            "contract_type": val["contract_type"],
            "description": val["description"],
            "text": val["text"]
        })
    return samples

@router.get("/contracts")
async def list_contracts() -> List[Dict[str, Any]]:
    """
    Returns list of contracts stored in the SQLite database.
    """
    return get_all_contracts()

@router.get("/contracts/{contract_id}")
async def get_contract(contract_id: str):
    """
    Retrieves full details of a saved contract with all clauses and risks.
    """
    record = get_contract_by_id(contract_id)
    if not record:
        raise HTTPException(status_code=404, detail="Contract not found in database.")
    return record

@router.delete("/contracts/{contract_id}")
async def remove_contract(contract_id: str):
    """
    Deletes a contract and its associated clauses and risks from the database.
    """
    success = delete_contract(contract_id)
    return {"success": success, "deleted_id": contract_id}
