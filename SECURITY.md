# Security Policy

## 🛡️ Overview

Security is a primary architectural pillar of the **Agentic DataOps Command Center**. Because this system bridges generative AI orchestration with enterprise data engineering pipelines and analytical stores, strict guardrails are enforced at every layer to prevent data exfiltration, unauthorized mutations, and prompt-injection-driven execution.

---

## 🔒 Security Architecture & Guardrails

### 1. Human-in-the-Loop (HITL) Gate
- **Cryptographic Approval Tokens**: All destructive, write, or state-changing operations (such as SQL schema modifications, data deletions, or pipeline re-executions) require a cryptographically generated human approval token (`APPR-...`).
- **Token Verification**: Execution tools reject any attempt to run without a validated approval token registered in the audit store.
- **Audit Logging**: Every action, tool invocation, token issuance, and execution result is immutably recorded in the audit trail.

### 2. Read-Only SQL & Blast Radius Isolation
- The investigative SQL tool (`run_sql`) enforces strict read-only execution patterns.
- Mutations (`UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`) are blocked on analytical inspection channels.
- Simulated impact tools (`simulate_impact`) calculate the blast radius and affected row counts before any remediation can be approved.

### 3. Credential & Secret Management
- **Zero Hardcoded Secrets**: No API keys, passwords, private keys, or tokens are stored in the codebase or git history.
- **Environment Isolation**: Sensitive configuration (such as `OPENAI_API_KEY`) is read exclusively from environment variables or a local `.env` file (which is git-ignored).
- **Deterministic Mock Mode**: Default operation runs via `LLM_PROVIDER=mock`, allowing full offline execution, automated testing, and evaluation without transmitting any data over the public internet.

---

## 📋 Supported Versions

We provide security updates and patches for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability within this project:

1. **Do not create a public issue** on GitHub.
2. Email a detailed security report to the maintainer: **kamatabhay45@gmail.com**.
3. Include the following details:
   - Type of issue (e.g., secret leakage, unauthorized execution, SQL injection, bypass of approval gates)
   - Step-by-step reproduction instructions or proof-of-concept
   - Impact assessment
4. You will receive an acknowledgment within **48 hours**, followed by status updates as the fix is developed and deployed.
