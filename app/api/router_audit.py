from fastapi import APIRouter
from typing import List, Dict, Any
from app.core.db_metadata import metadata_db

router = APIRouter(prefix="/api/audit", tags=["Audit Log"])

@router.get("/logs", response_model=List[Dict[str, Any]])
def get_audit_logs():
    return metadata_db.fetch_all("SELECT * FROM audit_events ORDER BY timestamp DESC LIMIT 100")
