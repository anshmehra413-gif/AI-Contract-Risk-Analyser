import uuid
from typing import List, Optional, Union, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.models.contract import Contract
from backend.app.schemas.contract import ContractCreate, ContractUpdate


def create_contract(
    db: Session,
    filename: Optional[str] = None,
    file_path: Optional[str] = None,
    status: str = "uploaded",
    contract_in: Optional[ContractCreate] = None,
    **kwargs
) -> Contract:
    """
    Creates and persists a new Contract record with status 'uploaded'.
    Supports both direct parameters and ContractCreate schema object.
    """
    if contract_in:
        c_filename = contract_in.filename
        c_file_path = contract_in.file_path or file_path
        c_status = contract_in.status or status
        c_contract_type = contract_in.contract_type or "Unknown"
        c_domain = contract_in.domain or "Unknown"
    else:
        c_filename = filename or kwargs.get("filename", "unknown.pdf")
        c_file_path = file_path
        c_status = status
        c_contract_type = kwargs.get("contract_type", "Unknown")
        c_domain = kwargs.get("domain", "Unknown")

    contract = Contract(
        id=str(uuid.uuid4()),
        filename=c_filename,
        file_path=c_file_path,
        contract_type=c_contract_type,
        domain=c_domain,
        status=c_status,
        overall_score=kwargs.get("overall_score", 0.0),
        risk_level=kwargs.get("risk_level", "Low"),
        confidence=kwargs.get("confidence", 0.0),
        summary=kwargs.get("summary", None),
        upload_date=datetime.utcnow(),
        created_at=datetime.utcnow()
    )

    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


def get_contracts(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Contract]:
    """
    Fetches paginated list of contracts ordered by creation date descending.
    """
    return (
        db.query(Contract)
        .order_by(Contract.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_contract(
    db: Session,
    contract_id: str
) -> Optional[Contract]:
    """
    Fetches a single contract by ID. Returns None if not found.
    """
    return db.query(Contract).filter(Contract.id == contract_id).first()


def update_contract(
    db: Session,
    contract_id: str,
    contract_update: Union[ContractUpdate, Dict[str, Any]]
) -> Optional[Contract]:
    """
    Updates fields on an existing contract record.
    Returns the updated Contract or None if not found.
    """
    contract = get_contract(db, contract_id)
    if not contract:
        return None

    if isinstance(contract_update, dict):
        update_data = contract_update
    else:
        update_data = contract_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if hasattr(contract, field) and value is not None:
            setattr(contract, field, value)

    db.commit()
    db.refresh(contract)
    return contract


def delete_contract(
    db: Session,
    contract_id: str
) -> bool:
    """
    Deletes a contract and cascades deletion to associated clauses and risks.
    Returns True if deleted, False if contract does not exist.
    """
    contract = get_contract(db, contract_id)
    if not contract:
        return False

    db.delete(contract)
    db.commit()
    return True
