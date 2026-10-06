from fastapi import APIRouter
from typing import Dict, Any
from app.eval.evaluator import BenchmarkEvaluator

router = APIRouter(prefix="/api/eval", tags=["AI Evaluation"])

@router.get("/run")
def run_evaluations() -> Dict[str, Any]:
    evaluator = BenchmarkEvaluator()
    return evaluator.run_evaluations()
