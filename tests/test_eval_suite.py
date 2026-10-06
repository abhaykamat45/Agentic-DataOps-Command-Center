import pytest
from app.eval.evaluator import BenchmarkEvaluator

def test_benchmark_evaluator(seeded_env):
    evaluator = BenchmarkEvaluator()
    eval_summary = evaluator.run_evaluations()
    
    assert eval_summary["total_benchmarks_evaluated"] == 20
    assert eval_summary["average_system_score"] >= 80.0
    assert len(eval_summary["results"]) == 20
