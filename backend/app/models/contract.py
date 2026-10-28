import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.db.session import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    contract_type = Column(String, nullable=True, default="Unknown")
    domain = Column(String, nullable=True, default="Unknown")
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False, default="uploaded")
    overall_score = Column(Float, default=0.0)
    risk_level = Column(String, nullable=True, default="Low")
    confidence = Column(Float, default=0.0)
    summary = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Cascading relationships: deleting a contract deletes all its clauses and risks
    clauses = relationship(
        "Clause",
        back_populates="contract",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    risks = relationship(
        "Risk",
        back_populates="contract",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class Clause(Base):
    __tablename__ = "clauses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_id = Column(
        String,
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False
    )
    clause_number = Column(String, nullable=True)
    clause_type = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    page_number = Column(Integer, default=1)
    confidence = Column(Float, default=0.0)
    start_char = Column(Integer, default=0)
    end_char = Column(Integer, default=0)

    contract = relationship("Contract", back_populates="clauses")
    risks = relationship("Risk", back_populates="clause")


class Risk(Base):
    __tablename__ = "risks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_id = Column(
        String,
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False
    )
    clause_id = Column(
        String,
        ForeignKey("clauses.id", ondelete="SET NULL"),
        nullable=True
    )
    risk_type = Column(String, nullable=False)
    risk_level = Column(String, nullable=False)
    reason = Column(Text, nullable=True)
    evidence = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    score_weight = Column(Float, default=1.0)

    contract = relationship("Contract", back_populates="risks")
    clause = relationship("Clause", back_populates="risks")
