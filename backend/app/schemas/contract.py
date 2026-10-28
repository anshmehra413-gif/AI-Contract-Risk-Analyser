from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class ContractBase(BaseModel):
    filename: str
    file_path: Optional[str] = None
    contract_type: Optional[str] = "Unknown"
    domain: Optional[str] = "Unknown"
    status: Optional[str] = "uploaded"
    overall_score: Optional[float] = 0.0
    risk_level: Optional[str] = "Low"
    confidence: Optional[float] = 0.0
    summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ContractCreate(BaseModel):
    filename: str
    file_path: Optional[str] = None
    contract_type: Optional[str] = "Unknown"
    domain: Optional[str] = "Unknown"
    status: Optional[str] = "uploaded"

    model_config = ConfigDict(from_attributes=True)


class ContractUpdate(BaseModel):
    filename: Optional[str] = None
    file_path: Optional[str] = None
    contract_type: Optional[str] = None
    domain: Optional[str] = None
    status: Optional[str] = None
    overall_score: Optional[float] = None
    risk_level: Optional[str] = None
    confidence: Optional[float] = None
    summary: Optional[str] = None
    rejection_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ContractOut(BaseModel):
    id: str
    filename: str
    file_path: Optional[str] = None
    contract_type: Optional[str] = None
    domain: Optional[str] = None
    upload_date: Optional[Any] = None
    status: str = "uploaded"
    overall_score: Optional[float] = 0.0
    risk_level: Optional[str] = None
    confidence: Optional[float] = 0.0
    summary: Optional[str] = None
    created_at: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)
