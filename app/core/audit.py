import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from app.core.db_metadata import metadata_db

class AuditLogger:
    def __init__(self):
        self.db = metadata_db

    def log_event(
        self,
        actor: str,
        action: str,
        target_resource: str,
        details: Optional[Dict[str, Any]] = None,
        approval_token: Optional[str] = None
    ) -> str:
        """Log an audit event to SQLite metadata DB."""
        event_id = f"AUD-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        details_json = json.dumps(details or {})

        query = """
        INSERT INTO audit_events (event_id, timestamp, actor, action, target_resource, details_json, approval_token)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute(query, (event_id, timestamp, actor, action, target_resource, details_json, approval_token))
        return event_id

    def generate_approval_token(self, plan_id: str, actor: str) -> str:
        """Generate a cryptographically unique approval token for a remediation plan."""
        token = f"APPR-{uuid.uuid4().hex[:12].upper()}"
        self.log_event(
            actor=actor,
            action="APPROVAL_TOKEN_ISSUED",
            target_resource=f"remediation_plan:{plan_id}",
            details={"plan_id": plan_id},
            approval_token=token
        )
        return token

    def verify_approval_token(self, token: str, plan_id: str) -> bool:
        """Verify if approval token is valid and matches plan."""
        query = """
        SELECT * FROM audit_events 
        WHERE action = 'APPROVAL_TOKEN_ISSUED' AND approval_token = ? AND target_resource = ?
        """
        record = self.db.fetch_one(query, (token, f"remediation_plan:{plan_id}"))
        return record is not None

audit_logger = AuditLogger()
