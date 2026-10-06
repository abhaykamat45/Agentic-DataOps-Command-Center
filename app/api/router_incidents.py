from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.core.db_metadata import metadata_db

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])

@router.get("", response_model=List[Dict[str, Any]])
def list_incidents():
    return metadata_db.fetch_all("SELECT * FROM incidents ORDER BY created_at DESC")

@router.get("/{incident_id}", response_model=Dict[str, Any])
def get_incident(incident_id: str):
    inc = metadata_db.fetch_one("SELECT * FROM incidents WHERE incident_id = ?", (incident_id,))
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    plans = metadata_db.fetch_all("SELECT * FROM remediation_plans WHERE incident_id = ?", (incident_id,))
    return {"incident": inc, "remediation_plans": plans}
