#!/usr/bin/env python3
"""Deterministic answer grader for MetaBench-AI development tasks.

The ground truths are public. This is an open-book development benchmark,
not a leakage-resistant evaluation. Passing does not verify code execution.
"""
import argparse
import json
import math
from pathlib import Path
from typing import Any

TASKS = {
    "mgx_batch_effect_evaluation": {
        "factor": "Project", "r2_before": 0.0663707059056571,
        "r2_after": 0.000761409501714426,
        "r2_tolerance": 0.0001,
    },
    "mgx_crc_dml_negative_control": {
        "estimate_tolerance": 0.002,
        "ci_tolerance": 0.003,  # provisional; not validated across implementations
        "taxa": {
            "Fusobacterium nucleatum_J": {
                "estimate": 0.021408, "ci_lower": 0.015502,
                "ci_upper": 0.027315, "ci_excludes_zero": True,
            },
            "Acidaminococcus intestini": {
                "estimate": -0.002120, "ci_lower": -0.006650,
                "ci_upper": 0.002410, "ci_excludes_zero": False,
            },
        },
    },
}


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    value = float(value)
    return value if math.isfinite(value) else None


def _check_numeric(actual: Any, expected: float, tolerance: float) -> dict:
    number = _number(actual)
    return {
        "pass": number is not None and abs(number - expected) <= tolerance,
        "actual": actual,
        "expected": expected,
        "tolerance": tolerance,
        "absolute_error": abs(number - expected) if number is not None else None,
    }


def _check_exact(actual: Any, expected: Any) -> dict:
    return {"pass": type(actual) is type(expected) and actual == expected,
            "actual": actual, "expected": expected}


def grade(answer: dict) -> dict:
    if not isinstance(answer, dict):
        raise ValueError("Answer must be a JSON object")
    task_id = answer.get("task_id")
    if task_id not in TASKS:
        raise ValueError("Unknown or missing task_id; expected one of: " + ", ".join(TASKS))

    spec = TASKS[task_id]
    checks = {}
    if task_id == "mgx_batch_effect_evaluation":
        checks["factor"] = _check_exact(answer.get("factor"), spec["factor"])
        for field in ("r2_before", "r2_after"):
            checks[field] = _check_numeric(answer.get(field), spec[field], spec["r2_tolerance"])
    else:
        taxa = answer.get("taxa")
        if not isinstance(taxa, dict):
            taxa = {}
        for taxon, expected in spec["taxa"].items():
            submitted = taxa.get(taxon)
            if not isinstance(submitted, dict):
                submitted = {}
            for field in ("estimate", "ci_lower", "ci_upper"):
                tolerance = (spec["estimate_tolerance"] if field == "estimate"
                             else spec["ci_tolerance"])
                checks[f"{taxon}.{field}"] = _check_numeric(
                    submitted.get(field), expected[field], tolerance
                )
            checks[f"{taxon}.ci_excludes_zero"] = _check_exact(
                submitted.get("ci_excludes_zero"), expected["ci_excludes_zero"]
            )
            lower = _number(submitted.get("ci_lower"))
            upper = _number(submitted.get("ci_upper"))
            checks[f"{taxon}.ci_order_valid"] = {
                "pass": lower is not None and upper is not None and lower <= upper,
                "actual": [submitted.get("ci_lower"), submitted.get("ci_upper")],
                "expected": "ci_lower <= ci_upper",
            }
            checks[f"{taxon}.interpretation_consistent"] = {
                "pass": (lower is not None and upper is not None and lower <= upper
                         and type(submitted.get("ci_excludes_zero")) is bool
                         and submitted["ci_excludes_zero"] == (lower > 0 or upper < 0)),
                "actual": submitted.get("ci_excludes_zero"),
                "expected": "Boolean consistent with reported interval",
            }

    passed = sum(int(check["pass"]) for check in checks.values())
    return {
        "task_id": task_id,
        "passed": passed,
        "total": len(checks),
        "score": round(passed / len(checks), 4),
        "all_passed": passed == len(checks),
        "checks": checks,
        "limitations": (
            "Open-book reference values; grading does not verify execution or provenance. "
            "DML confidence-interval tolerance (0.003) is provisional."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Grade a MetaBench-AI JSON answer")
    parser.add_argument("answer", type=Path, help="Path to the agent answer JSON")
    parser.add_argument("--output", type=Path, help="Optional path for JSON grading report")
    args = parser.parse_args()
    try:
        with args.answer.open(encoding="utf-8") as handle:
            answer = json.load(handle)
        report = grade(answer)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    rendered = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
