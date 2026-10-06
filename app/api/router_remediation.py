from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.core.db_metadata import metadata_db
from app.core.audit import audit_logger
from app.ai.orchestrator import orchestrator

router = APIRouter(prefix="/api/remediation", tags=["Remediation"])

class ApprovePlanRequest(BaseModel):
    plan_id: str
    approved_by: str = "DATA_ENGINEER_ADMIN"

@router.get("/plans", response_model=List[Dict[str, Any]])
def list_plans():
    return metadata_db.fetch_all("SELECT * FROM remediation_plans ORDER BY plan_id DESC")

@router.post("/approve")
def approve_and_execute_remediation(req: ApprovePlanRequest):
    plan = metadata_db.fetch_one("SELECT * FROM remediation_plans WHERE plan_id = ?", (req.plan_id,))
    if not plan:
        raise HTTPException(status_code=404, detail=f"Plan '{req.plan_id}' not found.")
    
    # 1. Issue approval token
    token = audit_logger.generate_approval_token(req.plan_id, req.approved_by)
    
    # 2. Execute remediation via orchestrator
    res = orchestrator.execute_remediation(req.plan_id, req.approved_by, token)
    return res
