# 🧠 AI Design & Agentic Loop - Agentic DataOps Command Center

## 1. ReAct Execution Loop
The orchestrator agent (`app/ai/orchestrator.py`) executes a 7-step investigation loop:

1. **PLAN**: Formulates investigation checklist based on incident alert details.
2. **CALL TOOLS**: Invokes typed tools (`inspect_pipeline`, `search_logs`, `inspect_schema`, `profile_dataset`, `detect_anomalies`, `find_dependencies`, `simulate_impact`, `generate_sql_fix`, `generate_remediation_plan`).
3. **COLLECT EVIDENCE**: Captures output datasets, log traces, and DQ rule violation counts.
4. **ANALYZE ROOT CAUSE**: Pinpoints exact root cause with high confidence.
5. **RECOMMEND & SIMULATE**: Generates SQL/PySpark fixes and dry-runs impact simulation.
6. **REQUEST APPROVAL**: Formulates pending remediation plan awaiting human review.
7. **EXECUTE & VERIFY**: Executes approved action with human token and verifies resolution.

---

## 2. Multi-Model LLM Abstraction
Supported via `app/ai/llm_factory.py`:
- `MockLLMClient`: 100% offline, deterministic mock driver for demos and evals.
- `OpenAILLMClient`: Standard tool-calling via OpenAI REST API.
- `OllamaLLMClient`: Local open-source model server (Llama3 / Qwen).
