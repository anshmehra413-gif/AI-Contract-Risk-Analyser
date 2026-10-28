import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "contracts.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 15.1 contracts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contracts (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        contract_type TEXT NOT NULL,
        domain TEXT NOT NULL,
        upload_date TEXT NOT NULL,
        status TEXT NOT NULL,
        overall_score REAL NOT NULL,
        risk_level TEXT NOT NULL,
        confidence REAL DEFAULT 0.0,
        summary TEXT,
        rejection_reason TEXT,
        raw_text TEXT,
        metadata_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 15.2 clauses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clauses (
        id TEXT PRIMARY KEY,
        contract_id TEXT NOT NULL,
        clause_number TEXT NOT NULL,
        clause_type TEXT NOT NULL,
        text TEXT NOT NULL,
        page_number INTEGER NOT NULL,
        confidence REAL NOT NULL,
        start_char INTEGER DEFAULT 0,
        end_char INTEGER DEFAULT 0,
        FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
    );
    """)
    
    # 15.3 risks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS risks (
        id TEXT PRIMARY KEY,
        contract_id TEXT NOT NULL,
        clause_id TEXT,
        risk_type TEXT NOT NULL,
        risk_level TEXT NOT NULL,
        reason TEXT NOT NULL,
        evidence TEXT NOT NULL,
        recommendation TEXT NOT NULL,
        score_weight REAL DEFAULT 1.0,
        FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE,
        FOREIGN KEY (clause_id) REFERENCES clauses(id) ON DELETE SET NULL
    );
    """)
    
    conn.commit()
    conn.close()

def save_contract_record(contract_data: Dict[str, Any], clauses: List[Dict[str, Any]], risks: List[Dict[str, Any]]):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT OR REPLACE INTO contracts (
        id, filename, contract_type, domain, upload_date, status, 
        overall_score, risk_level, confidence, summary, rejection_reason, raw_text, metadata_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        contract_data["id"],
        contract_data["filename"],
        contract_data.get("contract_type", "Unknown"),
        contract_data.get("domain", "Unknown"),
        contract_data.get("upload_date", datetime.utcnow().isoformat()),
        contract_data.get("status", "analyzed"),
        contract_data.get("overall_score", 0.0),
        contract_data.get("risk_level", "Low"),
        contract_data.get("confidence", 0.0),
        contract_data.get("summary", ""),
        contract_data.get("rejection_reason", None),
        contract_data.get("raw_text", ""),
        json.dumps(contract_data.get("metadata", {}))
    ))
    
    # Clear existing clauses and risks for this contract
    cursor.execute("DELETE FROM risks WHERE contract_id = ?", (contract_data["id"],))
    cursor.execute("DELETE FROM clauses WHERE contract_id = ?", (contract_data["id"],))
    
    # Insert clauses
    for c in clauses:
        cursor.execute("""
        INSERT INTO clauses (
            id, contract_id, clause_number, clause_type, text, page_number, confidence, start_char, end_char
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c["id"],
            contract_data["id"],
            c["clause_number"],
            c["clause_type"],
            c["text"],
            c.get("page_number", 1),
            c.get("confidence", 0.9),
            c.get("start_char", 0),
            c.get("end_char", 0)
        ))
        
    # Insert risks
    for r in risks:
        cursor.execute("""
        INSERT INTO risks (
            id, contract_id, clause_id, risk_type, risk_level, reason, evidence, recommendation, score_weight
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r["id"],
            contract_data["id"],
            r.get("clause_id"),
            r["risk_type"],
            r["risk_level"],
            r["reason"],
            r["evidence"],
            r["recommendation"],
            r.get("score_weight", 1.0)
        ))
        
    conn.commit()
    conn.close()

def get_all_contracts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, contract_type, domain, upload_date, status, overall_score, risk_level, confidence, created_at FROM contracts ORDER BY created_at DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_contract_by_id(contract_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM contracts WHERE id = ?", (contract_id,))
    c_row = cursor.fetchone()
    if not c_row:
        conn.close()
        return None
        
    contract = dict(c_row)
    if contract.get("metadata_json"):
        try:
            contract["metadata"] = json.loads(contract["metadata_json"])
        except Exception:
            contract["metadata"] = {}
            
    cursor.execute("SELECT * FROM clauses WHERE contract_id = ? ORDER BY page_number ASC", (contract_id,))
    clauses = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM risks WHERE contract_id = ?", (contract_id,))
    risks = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    return {
        "contract": contract,
        "clauses": clauses,
        "risks": risks
    }

def delete_contract(contract_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contracts WHERE id = ?", (contract_id,))
    cursor.execute("DELETE FROM clauses WHERE contract_id = ?", (contract_id,))
    cursor.execute("DELETE FROM risks WHERE contract_id = ?", (contract_id,))
    conn.commit()
    conn.close()
    return True
