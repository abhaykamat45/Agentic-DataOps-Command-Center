# 🎯 Evaluation Methodology - Agentic DataOps Command Center

## 1. Automated Benchmark Dataset
The system includes `app/eval/benchmark_dataset.json` containing **20 predefined incident scenarios**.

Each benchmark evaluates:
- **Tool Selection Accuracy**: Percentage of required diagnostic tools invoked.
- **Safety Adherence**: 100% enforcement of approval token requirement before destructive actions.
- **Grounding**: Verification that claims reference actual tool outputs.
- **Remediation Correctness**: Verification that executed cleanup resolves underlying data defects.

---

## 2. Running Evals
Run evaluations via command line:
```bash
python -m pytest tests/test_eval_suite.py
```
Or via FastAPI REST API: `GET /api/eval/run`.
