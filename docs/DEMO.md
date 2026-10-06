# 🎬 Demo Scenario Guide - Agentic DataOps Command Center

## 1. Quick Demo Walkthrough

### Scenario 1: Plan & GAID Integrity Failure (`INC-101`)
1. Open Streamlit Dashboard (`streamlit run app/ui/app.py`).
2. Navigate to **Incidents** page.
3. Select `INC-101 - Plan & GAID Integrity Failure`.
4. Observe initial incident state: pipeline `pipe_claims_integrity` failed.
5. Click **🤖 Launch AI Tool Investigation**.
6. Observe AI execution:
   - Tool calls executed: `inspect_pipeline`, `search_logs`, `profile_dataset`, `detect_anomalies`, `simulate_impact`.
   - Discovered root cause: 45 active claims and 28 benefits reference `PLAN-104` (status `TERMINATED`).
   - Impact simulation: 45 rows affected in `claims`.
7. Inspect generated SQL fix:
   ```sql
   DELETE FROM claims WHERE plan_id = 'PLAN-104';
   DELETE FROM benefits WHERE plan_id = 'PLAN-104';
   ```
8. Click **✅ Approve & Execute Fix**.
9. System issues approval token `APPR-XXXX`, executes SQL cleanup, re-runs pipeline, and runs `verify_remediation`.
10. Incident status updates to **RESOLVED** and 100% DQ rules pass!

---

### Scenario 2: Schema Drift Failure (`INC-102`)
- Detects column `country` type mismatch (float64 vs expected VARCHAR).

### Scenario 3: Data Quality Null Spike (`INC-103`)
- Detects 40% null spike in `transactions.amount` column, breaching 5% threshold.
