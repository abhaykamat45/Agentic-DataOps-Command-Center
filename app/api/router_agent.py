from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.ai.orchestrator import orchestrator

router = APIRouter(prefix="/api/agent", tags=["AI Agent"])

class InvestigateRequest(BaseModel):
    incident_id: str
    user_prompt: Optional[str] = None

@router.post("/investigate")
def investigate_incident(req: InvestigateRequest):
    try:
        result = orchestrator.investigate_incident(req.incident_id, req.user_prompt)
        return result.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
