from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.core.db_metadata import metadata_db

router = APIRouter(prefix="/api/pipelines", tags=["Pipelines"])

@router.get("", response_model=List[Dict[str, Any]])
def list_pipelines():
    return metadata_db.fetch_all("SELECT * FROM pipelines ORDER BY pipeline_id ASC")

@router.get("/{pipeline_id}", response_model=Dict[str, Any])
def get_pipeline(pipeline_id: str):
    pipe = metadata_db.fetch_one("SELECT * FROM pipelines WHERE pipeline_id = ?", (pipeline_id,))
    if not pipe:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    runs = metadata_db.fetch_all("SELECT * FROM pipeline_runs WHERE pipeline_id = ? ORDER BY start_time DESC", (pipeline_id,))
    return {"pipeline": pipe, "runs": runs}
