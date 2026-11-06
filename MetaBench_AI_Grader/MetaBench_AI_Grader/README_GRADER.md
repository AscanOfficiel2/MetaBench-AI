# MetaBench-AI deterministic grader (development version)

This package uses only the Python standard library (Python 3.10+ recommended).
It grades **structured numerical outputs**, not the quality of code execution or scientific reasoning processes.

## Files

- `graders/grade_benchmark.py`: CLI grader for both tasks.
- `examples/task1_answer.json`: reference-shaped Task 1 example.
- `examples/task2_answer.json`: reference-shaped Task 2 example.
- `tests/test_grader.py`: unit tests for passing and failing responses.

## Run

From the repository root:

```bash
python graders/grade_benchmark.py examples/task1_answer.json --output reports/task1_report.json
python graders/grade_benchmark.py examples/task2_answer.json --output reports/task2_report.json
python -m unittest discover -s tests -v
```

To evaluate an agent, save its output as JSON matching the schema shown in the examples, then replace the example path with the agent's file path.

## Scoring

- Task 1: exact `Project` match and ±0.0001 absolute tolerance for each R².
- Task 2: ±0.002 absolute tolerance for each estimate; ±0.003 for each confidence interval bound (**provisional, unvalidated**); exact booleans for zero-exclusion, plus interval-order and internal-consistency checks.
- Score = fraction of checks passed, equally weighted. `all_passed` is true only if all checks pass.
- Wrong/missing fields fail their checks. Invalid JSON and unknown task IDs cause a nonzero CLI exit.

## Important limitations

1. The ground truths are publicly available. This is an open development benchmark, not leakage-resistant model ranking.
2. A high score does not demonstrate that an AI agent ran the analysis. Record execution logs separately.
3. The confidence-interval tolerance is provisional and should be validated against independent implementations.
4. Numerical matching does not assess causal interpretation; the DML coefficients do not establish causal effects.
5. The example JSON files contain the expected answers and must **not** be provided to an evaluated agent.

