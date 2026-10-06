import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import settings

class MetadataDB:
    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = db_path

    @property
    def db_path(self) -> Path:
        return self._db_path or settings.METADATA_DB_PATH

    def get_connection(self) -> sqlite3.Connection:
        path = self.db_path
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize all metadata tables in SQLite."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Pipelines
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipelines (
                pipeline_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                domain TEXT NOT NULL,
                schedule TEXT,
                status TEXT NOT NULL,
                owner TEXT,
                updated_at TEXT NOT NULL
            );
            """)

            # 2. Pipeline Runs
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id TEXT PRIMARY KEY,
                pipeline_id TEXT NOT NULL,
                status TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                records_processed INTEGER DEFAULT 0,
                error_message TEXT,
                log_path TEXT,
                FOREIGN KEY (pipeline_id) REFERENCES pipelines (pipeline_id)
            );
            """)

            # 3. Schemas
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS schemas (
                schema_id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                column_name TEXT NOT NULL,
                data_type TEXT NOT NULL,
                is_nullable INTEGER DEFAULT 1,
                is_primary_key INTEGER DEFAULT 0,
                version TEXT DEFAULT 'v1',
                updated_at TEXT NOT NULL
            );
            """)

            # 4. Data Quality Rules
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_quality_rules (
                rule_id TEXT PRIMARY KEY,
                table_name TEXT NOT NULL,
                column_name TEXT,
                rule_type TEXT NOT NULL,
                threshold REAL,
                enabled INTEGER DEFAULT 1
            );
            """)

            # 5. Lineage
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS lineage (
                lineage_id TEXT PRIMARY KEY,
                source_table TEXT NOT NULL,
                transformation_name TEXT NOT NULL,
                target_table TEXT NOT NULL,
                dependency_type TEXT DEFAULT 'DIRECT'
            );
            """)

            # 6. Incidents
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                incident_id TEXT PRIMARY KEY,
                pipeline_id TEXT NOT NULL,
                run_id TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                root_cause TEXT,
                evidence TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (pipeline_id) REFERENCES pipelines (pipeline_id),
                FOREIGN KEY (run_id) REFERENCES pipeline_runs (run_id)
            );
            """)

            # 7. Remediation Plans
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS remediation_plans (
                plan_id TEXT PRIMARY KEY,
                incident_id TEXT NOT NULL,
                status TEXT NOT NULL,
                sql_fix TEXT,
                pyspark_fix TEXT,
                impact_summary TEXT,
                requires_approval INTEGER DEFAULT 1,
                approved_by TEXT,
                approved_at TEXT,
                execution_result TEXT,
                FOREIGN KEY (incident_id) REFERENCES incidents (incident_id)
            );
            """)

            # 8. Audit Events
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                target_resource TEXT NOT NULL,
                details_json TEXT,
                approval_token TEXT
            );
            """)

            # 9. Evaluations
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                eval_id TEXT PRIMARY KEY,
                incident_id TEXT NOT NULL,
                score REAL NOT NULL,
                tool_accuracy REAL NOT NULL,
                safety_passed INTEGER NOT NULL,
                grounding_passed INTEGER NOT NULL,
                details_json TEXT,
                eval_time TEXT NOT NULL
            );
            """)

            conn.commit()

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    def execute(self, query: str, params: tuple = ()) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount

metadata_db = MetadataDB()
