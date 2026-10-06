import random
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from app.config import settings
from app.core.db_metadata import MetadataDB, metadata_db
from app.core.db_analytical import AnalyticalDB, analytical_db

class SyntheticDataGenerator:
    def __init__(self, metadata_db: MetadataDB, analytical_db: AnalyticalDB):
        self.meta_db = metadata_db
        self.ana_db = analytical_db
        self.now = datetime.now()

    def generate_all(self):
        """Generate parquet datasets and seed metadata database."""
        self.meta_db.init_db()
        self._generate_parquet_datasets()
        self._seed_metadata()
        self._create_log_files()

    def _generate_parquet_datasets(self):
        random.seed(42)
        np.random.seed(42)

        # 1. Plans
        plans_data = [
            {"plan_id": "PLAN-101", "plan_name": "Basic Individual Plan", "tier": "Bronze", "monthly_cost": 29.99, "status": "ACTIVE"},
            {"plan_id": "PLAN-102", "plan_name": "Family Health Premier", "tier": "Silver", "monthly_cost": 89.99, "status": "ACTIVE"},
            {"plan_id": "PLAN-103", "plan_name": "Corporate Platinum Care", "tier": "Gold", "monthly_cost": 199.99, "status": "ACTIVE"},
            {"plan_id": "PLAN-104", "plan_name": "Legacy Gold Enterprise Plan", "tier": "Gold", "monthly_cost": 149.99, "status": "TERMINATED"}, # Terminated Plan!
            {"plan_id": "PLAN-105", "plan_name": "Senior Supplemental Plus", "tier": "Silver", "monthly_cost": 59.99, "status": "ACTIVE"}
        ]
        df_plans = pd.DataFrame(plans_data)
        self.ana_db.save_dataframe_as_table(df_plans, "plans")

        # 2. GAIDs (Group Account IDs)
        gaids_data = [
            {"gaid_id": f"GAID-10{i}", "gaid_code": f"GRP-US-EAST-{i}", "region": "US-East", "status": "ACTIVE"}
            for i in range(1, 6)
        ]
        gaids_data.append({"gaid_id": "GAID-999", "gaid_code": "GRP-EXPIRED-LEGACY", "region": "US-West", "status": "INACTIVE"})
        df_gaids = pd.DataFrame(gaids_data)
        self.ana_db.save_dataframe_as_table(df_gaids, "gaids")

        # 3. Customers
        customers_data = []
        for i in range(1, 501):
            # Inject null spike for anomaly scenario if i > 300
            email = f"user_{i}@example.com" if i <= 300 or i > 400 else None
            customers_data.append({
                "customer_id": f"CUST-{i:04d}",
                "name": f"Customer Name {i}",
                "email": email,
                "country": "USA" if i % 2 == 0 else "Canada",
                "created_at": (self.now - timedelta(days=i%100)).strftime("%Y-%m-%d"),
                "status": "ACTIVE" if i % 10 != 0 else "INACTIVE"
            })
        df_customers = pd.DataFrame(customers_data)
        self.ana_db.save_dataframe_as_table(df_customers, "customers")

        # 4. Employees
        depts = ["Engineering", "DataOps", "Finance", "Healthcare Operations", "Compliance"]
        employees_data = [
            {
                "emp_id": f"EMP-{i:03d}",
                "name": f"Employee {i}",
                "department": random.choice(depts),
                "role": "Data Engineer" if i % 3 == 0 else "Analyst",
                "salary": float(random.randint(70000, 150000)),
                "hire_date": "2022-01-15"
            }
            for i in range(1, 101)
        ]
        df_employees = pd.DataFrame(employees_data)
        self.ana_db.save_dataframe_as_table(df_employees, "employees")

        # 5. Benefits
        benefits_data = []
        for i in range(1, 301):
            # Injected issue: 28 references to PLAN-104 (Terminated)
            plan_id = "PLAN-104" if i <= 28 else f"PLAN-10{(i%3)+1}"
            gaid_id = f"GAID-10{(i%4)+1}"
            benefits_data.append({
                "benefit_id": f"BEN-{i:04d}",
                "customer_id": f"CUST-{(i%500)+1:04d}",
                "plan_id": plan_id,
                "gaid_id": gaid_id,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            })
        df_benefits = pd.DataFrame(benefits_data)
        self.ana_db.save_dataframe_as_table(df_benefits, "benefits")

        # 6. Claims
        claims_data = []
        for i in range(1, 601):
            # Injected issue: 45 references to PLAN-104 and 15 references to GAID-999 (Inactive)
            plan_id = "PLAN-104" if i <= 45 else f"PLAN-10{(i%3)+1}"
            gaid_id = "GAID-999" if 46 <= i <= 60 else f"GAID-10{(i%4)+1}"
            claims_data.append({
                "claim_id": f"CLM-{i:05d}",
                "customer_id": f"CUST-{(i%500)+1:04d}",
                "plan_id": plan_id,
                "gaid_id": gaid_id,
                "claim_amount": round(random.uniform(50.0, 3500.0), 2),
                "status": "APPROVED" if i % 2 == 0 else "PENDING",
                "submitted_at": (self.now - timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S")
            })
        df_claims = pd.DataFrame(claims_data)
        self.ana_db.save_dataframe_as_table(df_claims, "claims")

        # 7. Transactions
        txns_data = []
        for i in range(1, 1001):
            # Injected null spike anomaly for amount in last 400 rows
            is_null_spike = i > 600
            txns_data.append({
                "txn_id": f"TXN-{i:06d}",
                "customer_id": f"CUST-{(i%500)+1:04d}",
                "amount": None if is_null_spike else round(random.uniform(10.0, 500.0), 2),
                "currency": None if is_null_spike else "USD",
                "timestamp": (self.now - timedelta(minutes=i*10)).strftime("%Y-%m-%d %H:%M:%S"),
                "status": "COMPLETED"
            })
        df_txns = pd.DataFrame(txns_data)
        self.ana_db.save_dataframe_as_table(df_txns, "transactions")

        # 8. Products
        products_data = [
            {"product_id": f"PROD-{i:03d}", "product_name": f"Healthcare Device {i}", "category": "Medical", "price": round(random.uniform(19.99, 499.99), 2), "stock": random.randint(10, 500)}
            for i in range(1, 51)
        ]
        df_products = pd.DataFrame(products_data)
        self.ana_db.save_dataframe_as_table(df_products, "products")

    def _seed_metadata(self):
        conn = self.meta_db.get_connection()
        cursor = conn.cursor()

        # Clean existing metadata
        for tbl in ["pipelines", "pipeline_runs", "schemas", "data_quality_rules", "lineage", "incidents", "remediation_plans", "audit_events", "evaluations"]:
            cursor.execute(f"DELETE FROM {tbl};")

        # Pipelines
        pipelines = [
            ("PIPE-001", "pipe_claims_integrity", "Healthcare Claims", "0 */2 * * *", "FAILED", "DataOps Team", self.now.strftime("%Y-%m-%d %H:%M:%S")),
            ("PIPE-002", "pipe_schema_sync", "Customer Metadata", "0 0 * * *", "FAILED", "Core Data Platform", self.now.strftime("%Y-%m-%d %H:%M:%S")),
            ("PIPE-003", "pipe_txn_aggregate", "Finance & Billing", "*/30 * * * *", "FAILED", "Finance Data Team", self.now.strftime("%Y-%m-%d %H:%M:%S")),
            ("PIPE-004", "pipe_employees_etl", "HR Analytics", "0 6 * * *", "SUCCESS", "HR Tech", self.now.strftime("%Y-%m-%d %H:%M:%S")),
            ("PIPE-005", "pipe_products_inventory", "Supply Chain", "0 1 * * *", "SUCCESS", "Logistics", self.now.strftime("%Y-%m-%d %H:%M:%S"))
        ]
        cursor.executemany("INSERT INTO pipelines VALUES (?,?,?,?,?,?,?)", pipelines)

        # Pipeline Runs
        runs = [
            ("RUN-001-A", "PIPE-001", "FAILED", (self.now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"), self.now.strftime("%Y-%m-%d %H:%M:%S"), 600, "IntegrityValidationError: Referencing TERMINATED plan_id PLAN-104 in active claims and benefits.", str(settings.LOGS_DIR / "run_001.log")),
            ("RUN-002-A", "PIPE-002", "FAILED", (self.now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"), self.now.strftime("%Y-%m-%d %H:%M:%S"), 0, "SchemaMismatchError: Expected column 'country' in landing payload but received unexpected data type float64.", str(settings.LOGS_DIR / "run_002.log")),
            ("RUN-003-A", "PIPE-003", "FAILED", (self.now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"), self.now.strftime("%Y-%m-%d %H:%M:%S"), 1000, "DataQualityError: Null rate for 'amount' column reached 40.0%, exceeding max threshold 5.0%.", str(settings.LOGS_DIR / "run_003.log")),
            ("RUN-004-A", "PIPE-004", "SUCCESS", (self.now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"), (self.now - timedelta(hours=4, minutes=50)).strftime("%Y-%m-%d %H:%M:%S"), 100, None, str(settings.LOGS_DIR / "run_004.log")),
            ("RUN-005-A", "PIPE-005", "SUCCESS", (self.now - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"), (self.now - timedelta(hours=5, minutes=55)).strftime("%Y-%m-%d %H:%M:%S"), 50, None, str(settings.LOGS_DIR / "run_005.log"))
        ]
        cursor.executemany("INSERT INTO pipeline_runs VALUES (?,?,?,?,?,?,?,?)", runs)

        # Schemas
        schema_entries = [
            ("plans", "plan_id", "VARCHAR", 0, 1, "v1"),
            ("plans", "plan_name", "VARCHAR", 0, 0, "v1"),
            ("plans", "tier", "VARCHAR", 0, 0, "v1"),
            ("plans", "monthly_cost", "DOUBLE", 0, 0, "v1"),
            ("plans", "status", "VARCHAR", 0, 0, "v1"),

            ("claims", "claim_id", "VARCHAR", 0, 1, "v1"),
            ("claims", "customer_id", "VARCHAR", 0, 0, "v1"),
            ("claims", "plan_id", "VARCHAR", 0, 0, "v1"),
            ("claims", "gaid_id", "VARCHAR", 0, 0, "v1"),
            ("claims", "claim_amount", "DOUBLE", 0, 0, "v1"),
            ("claims", "status", "VARCHAR", 0, 0, "v1"),

            ("benefits", "benefit_id", "VARCHAR", 0, 1, "v1"),
            ("benefits", "customer_id", "VARCHAR", 0, 0, "v1"),
            ("benefits", "plan_id", "VARCHAR", 0, 0, "v1"),
            ("benefits", "gaid_id", "VARCHAR", 0, 0, "v1"),

            ("transactions", "txn_id", "VARCHAR", 0, 1, "v1"),
            ("transactions", "customer_id", "VARCHAR", 0, 0, "v1"),
            ("transactions", "amount", "DOUBLE", 1, 0, "v1"),
            ("transactions", "currency", "VARCHAR", 1, 0, "v1"),

            ("customers", "customer_id", "VARCHAR", 0, 1, "v1"),
            ("customers", "name", "VARCHAR", 0, 0, "v1"),
            ("customers", "email", "VARCHAR", 1, 0, "v1"),
            ("customers", "country", "VARCHAR", 1, 0, "v1")
        ]
        now_str = self.now.strftime("%Y-%m-%d %H:%M:%S")
        cursor.executemany("INSERT INTO schemas (table_name, column_name, data_type, is_nullable, is_primary_key, version, updated_at) VALUES (?,?,?,?,?,?,?)",
                          [(*item, now_str) for item in schema_entries])

        # Data Quality Rules
        dq_rules = [
            ("DQ-001", "claims", "plan_id", "REFERENTIAL_INTEGRITY", 0.0, 1),
            ("DQ-002", "claims", "gaid_id", "REFERENTIAL_INTEGRITY", 0.0, 1),
            ("DQ-003", "transactions", "amount", "NULL_RATE", 0.05, 1),
            ("DQ-004", "transactions", "currency", "NULL_RATE", 0.05, 1),
            ("DQ-005", "customers", "email", "NULL_RATE", 0.02, 1),
            ("DQ-006", "plans", "status", "ALLOWED_VALUES", 0.0, 1)
        ]
        cursor.executemany("INSERT INTO data_quality_rules VALUES (?,?,?,?,?,?)", dq_rules)

        # Lineage
        lineage_entries = [
            ("LIN-001", "plans", "join_plan_claims", "claims", "FOREIGN_KEY"),
            ("LIN-002", "gaids", "join_gaid_claims", "claims", "FOREIGN_KEY"),
            ("LIN-003", "plans", "join_plan_benefits", "benefits", "FOREIGN_KEY"),
            ("LIN-004", "customers", "sync_customer_txns", "transactions", "DIRECT"),
            ("LIN-005", "claims", "aggregate_claims_summary", "claims_summary_report", "AGGREGATION")
        ]
        cursor.executemany("INSERT INTO lineage VALUES (?,?,?,?,?)", lineage_entries)

        # Incidents
        incidents = [
            ("INC-101", "PIPE-001", "RUN-001-A", "CRITICAL", "OPEN",
             "Plan & GAID Integrity Failure: Terminated Plan & Inactive GAID references in claims/benefits",
             "Pipeline pipe_claims_integrity failed because active claims & benefits reference plan PLAN-104 marked TERMINATED in plans master table, along with INACTIVE GAID-999.",
             "Active claims and benefits reference PLAN-104 (status=TERMINATED) and GAID-999 (status=INACTIVE).",
             json.dumps({"affected_tables": ["claims", "benefits"], "affected_plan_id": "PLAN-104", "affected_gaid_id": "GAID-999", "claims_count": 45, "benefits_count": 28}),
             self.now.strftime("%Y-%m-%d %H:%M:%S")),

            ("INC-102", "PIPE-002", "RUN-002-A", "HIGH", "OPEN",
             "Schema Drift Failure: Mismatched schema type on customer_sync payload",
             "Source dataset payload has type drift for country column.",
             "Source column country detected as float64 instead of VARCHAR.",
             json.dumps({"affected_tables": ["customers"], "expected_type": "VARCHAR", "actual_type": "FLOAT64"}),
             (self.now - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")),

            ("INC-103", "PIPE-003", "RUN-003-A", "HIGH", "OPEN",
             "Data Quality Anomaly: Severe Null Spike in Transactions Amount",
             "Transactions ingestion pipeline detected 40% null values in transaction amount column.",
             "DQ Check DQ-003 failed. Expected max null rate 5%, actual null rate 40.0%.",
             json.dumps({"affected_tables": ["transactions"], "column": "amount", "null_rate": 0.40, "threshold": 0.05}),
             (self.now - timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S"))
        ]
        cursor.executemany("INSERT INTO incidents VALUES (?,?,?,?,?,?,?,?,?,?)", incidents)

        # Audit events
        audit_events = [
            ("AUD-001", (self.now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"), "SYSTEM", "PIPELINE_FAILURE_DETECTED", "PIPE-001", json.dumps({"incident_id": "INC-101", "run_id": "RUN-001-A"}), None),
            ("AUD-002", (self.now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"), "SYSTEM", "PIPELINE_FAILURE_DETECTED", "PIPE-002", json.dumps({"incident_id": "INC-102", "run_id": "RUN-002-A"}), None)
        ]
        cursor.executemany("INSERT INTO audit_events VALUES (?,?,?,?,?,?,?)", audit_events)

        conn.commit()
        conn.close()

    def _create_log_files(self):
        """Create mock pipeline log execution files."""
        logs = {
            "run_001.log": """[2026-09-20 12:00:00] [INFO] Starting pipeline run RUN-001-A for pipe_claims_integrity...
[2026-09-20 12:00:05] [INFO] Extracting claims dataset from storage... Read 600 records.
[2026-09-20 12:00:10] [INFO] Extracting plans master dataset from storage... Read 5 records.
[2026-09-20 12:00:15] [ERROR] IntegrityValidationError: Foreign key integrity check failed!
[2026-09-20 12:00:15] [ERROR] 45 active claims reference PLAN-104 which is marked status='TERMINATED' in plans master table.
[2026-09-20 12:00:15] [ERROR] 28 active benefits reference PLAN-104 which is marked status='TERMINATED'.
[2026-09-20 12:00:15] [ERROR] 15 active claims reference GAID-999 which is marked status='INACTIVE'.
[2026-09-20 12:00:16] [FATAL] Pipeline RUN-001-A terminated with exit code 1.
""",
            "run_002.log": """[2026-09-20 11:00:00] [INFO] Starting pipeline run RUN-002-A for pipe_schema_sync...
[2026-09-20 11:00:02] [INFO] Validating landing schema for customers_sync...
[2026-09-20 11:00:05] [ERROR] SchemaMismatchError: Column 'country' data type mismatch. Expected VARCHAR, found FLOAT64.
[2026-09-20 11:00:06] [FATAL] Pipeline RUN-002-A terminated with exit code 1.
""",
            "run_003.log": """[2026-09-20 10:30:00] [INFO] Starting pipeline run RUN-003-A for pipe_txn_aggregate...
[2026-09-20 10:30:04] [INFO] Running Data Quality Check DQ-003 on transactions.amount...
[2026-09-20 10:30:08] [ERROR] DataQualityError: Null rate threshold violated for column 'amount'. Threshold: 0.05, Actual: 0.4000.
[2026-09-20 10:30:09] [FATAL] Pipeline RUN-003-A terminated with exit code 1.
""",
            "run_004.log": "[2026-09-20 08:00:00] [INFO] Pipeline RUN-004-A finished successfully. Processed 100 records.\n",
            "run_005.log": "[2026-09-20 07:00:00] [INFO] Pipeline RUN-005-A finished successfully. Processed 50 records.\n"
        }

        for filename, content in logs.items():
            log_path = settings.LOGS_DIR / filename
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(content)

if __name__ == "__main__":
    gen = SyntheticDataGenerator(metadata_db, analytical_db)
    gen.generate_all()
    print("Synthetic data generation complete!")
