"""
grader.py — scores the multiagent-dataanalysis project 0-10.
Stages scoring below 6 are flagged for re-run.
"""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

RERUN_THRESHOLD = 6


@dataclass
class StageResult:
    name: str
    score: int
    max_score: int
    notes: List[str] = field(default_factory=list)
    needs_rerun: bool = False


def check_scaffold() -> StageResult:
    notes, score = [], 0
    for fpath, desc in [
        ("requirements.txt", "Dependencies file"),
        (".gitignore", "Git ignore"),
        ("Makefile", "Makefile"),
        ("checkpoints/.gitkeep", "Checkpoints dir"),
        ("data/.gitkeep", "Data dir"),
    ]:
        if Path(fpath).exists():
            score += 2
            notes.append(f"PASS {desc}: {fpath}")
        else:
            notes.append(f"FAIL {desc}: {fpath} missing")
    return StageResult("scaffold", min(score, 10), 10, notes, score < RERUN_THRESHOLD)


def check_ml_pipeline() -> StageResult:
    notes, score = [], 0
    for fpath, desc in [
        ("app/model.py", "Workbook analysis engine"),
        ("model/train.py", "Batch profiling script"),
        ("model/register_model.py", "MLflow registration"),
        ("compare_runs.py", "Run comparison script"),
    ]:
        if Path(fpath).exists():
            score += 2
            notes.append(f"PASS {desc}: {fpath}")
        else:
            notes.append(f"FAIL {desc}: {fpath} missing")

    if Path("app/model.py").exists():
        content = Path("app/model.py").read_text()
        if "read_excel" in content or "read_csv" in content:
            score += 1
            notes.append("PASS Workbook parsing detected")
        if "dataset_type" in content or "recommendations" in content:
            score += 1
            notes.append("PASS Analysis summarization detected")

    return StageResult("analysis_pipeline", min(score, 10), 10, notes, score < RERUN_THRESHOLD)


def check_deployment() -> StageResult:
    notes, score = [], 0
    for fpath, desc in [
        ("main.py", "FastAPI app entry point"),
        ("app/routers.py", "API routers"),
        ("app/schemas.py", "Pydantic schemas"),
        ("ui/app.py", "UI frontend"),
        ("tests/test_api.py", "API tests"),
    ]:
        if Path(fpath).exists():
            score += 2
            notes.append(f"PASS {desc}: {fpath}")
        else:
            notes.append(f"FAIL {desc}: {fpath} missing")

    if Path("app/routers.py").exists():
        content = Path("app/routers.py").read_text()
        if "/analyze" in content:
            score += 1
            notes.append("PASS Analyze route detected")
        if "MAX_FILE_SIZE" in content or "10MB" in content:
            score += 1
            notes.append("PASS File size validation detected")

    return StageResult("deployment", min(score, 10), 10, notes, score < RERUN_THRESHOLD)


def check_reliability() -> StageResult:
    notes, score = [], 0
    for fpath, desc in [
        ("app/middleware.py", "JSONL analysis logger middleware"),
        ("app/drift_checker.py", "Drift detection checker"),
        ("monitor_dashboard.py", "Monitoring dashboard"),
        ("grader.py", "Project grader"),
        ("logs/.gitkeep", "Logs directory placeholder"),
    ]:
        if Path(fpath).exists():
            score += 2
            notes.append(f"PASS {desc}: {fpath}")
        else:
            notes.append(f"FAIL {desc}: {fpath} missing")
    return StageResult("reliability", min(score, 10), 10, notes, score < RERUN_THRESHOLD)


def run_grader():
    print("=" * 60)
    print("EXCEL SHEET ANALYSIS — PROJECT GRADER")
    print("=" * 60)

    stages = [check_scaffold(), check_ml_pipeline(), check_deployment(), check_reliability()]
    total = sum(stage.score for stage in stages)
    max_total = sum(stage.max_score for stage in stages)
    overall = round(total / max_total * 10, 1)

    for stage in stages:
        status = "NEEDS RERUN" if stage.needs_rerun else "OK"
        print(f"\n[{stage.name.upper()}] Score: {stage.score}/{stage.max_score} — {status}")
        for note in stage.notes:
            print(f"  {note}")

    needs = [stage.name for stage in stages if stage.needs_rerun]
    print("\n" + "=" * 60)
    print(f"OVERALL SCORE: {overall}/10")
    print(f"Stages needing re-run: {needs or 'none'}")
    print("=" * 60)

    result = {
        "overall_score": overall,
        "stages": [
            {
                "name": stage.name,
                "score": stage.score,
                "max_score": stage.max_score,
                "needs_rerun": stage.needs_rerun,
            }
            for stage in stages
        ],
        "needs_rerun": needs,
    }

    Path(".agent_memory").mkdir(exist_ok=True)
    with open(".agent_memory/grader_result.json", "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
    print("\nGrader result saved to .agent_memory/grader_result.json")
    return result


if __name__ == "__main__":
    run_grader()
