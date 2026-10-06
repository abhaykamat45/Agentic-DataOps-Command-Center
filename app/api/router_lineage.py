from fastapi import APIRouter
from typing import List, Dict, Any
from app.core.db_metadata import metadata_db

router = APIRouter(prefix="/api/lineage", tags=["Lineage"])

@router.get("", response_model=List[Dict[str, Any]])
def get_lineage():
    return metadata_db.fetch_all("SELECT * FROM lineage")
