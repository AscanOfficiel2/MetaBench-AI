# Task 2: Confounder-Aware DML and Negative-Control Analysis

**Task ID:** `mgx_crc_dml_negative_control`

## Agent-facing prompt

You are given a sample-by-species CLR-transformed, batch-corrected abundance matrix and matched clinical metadata from colorectal cancer cohorts. Use the **original V2 matrix provided for this task**; do not substitute the matrix produced in Task 1. The metadata contain `Sample_ID`, `Group`, `Age`, `BMI`, and `Sex`.

Match samples using `Sample_ID`, restricting the analysis to `Healthy` and `Cancer` and **excluding `Adenoma`**. Encode `Cancer` as 1 and `Healthy` as 0, and encode `Sex` as Male = 1 and Female = 0. For the analysis, retain samples with nonmissing outcome, both specified taxon abundances, and all three covariates (`Age`, `BMI`, `Sex`).

Fit **two separate** `econml.dml.LinearDML` models, treating each taxon's abundance as a continuous exposure (`discrete_treatment=False`):

- `Fusobacterium nucleatum_J`
- `Acidaminococcus intestini`

For each model, set `Y` to the binary disease outcome, `T` to the selected taxon's abundance, and `X` to the three covariates in this order: `Age`, `BMI`, `Sex`. Use `RandomForestRegressor(n_estimators=200, min_samples_leaf=10, random_state=42)` for both `model_y` and `model_t`. Use five-fold cross-fitting (`cv=5`) and `random_state=42` for `LinearDML`. Fit the model and report `dml.ate(X=X)` and `dml.ate_interval(X=X)` at the default 95% confidence level.

**Question:** What is the estimated adjusted association and its 95% confidence interval for each taxon? For each interval, state whether it excludes zero. Report numerical values to six decimal places. These are observational model-dependent estimates, not proof of causality.

Return **only** a JSON object in this format:

```json
{
  "task_id": "mgx_crc_dml_negative_control",
  "sample_count": 0,
  "results": [
    {
      "taxon": "Fusobacterium nucleatum_J",
      "estimate": 0.0,
      "ci_lower": 0.0,
      "ci_upper": 0.0,
      "ci_excludes_zero": false
    },
    {
      "taxon": "Acidaminococcus intestini",
      "estimate": 0.0,
      "ci_lower": 0.0,
      "ci_upper": 0.0,
      "ci_excludes_zero": false
    }
  ]
}
```

## Input files

- [`Task2_input/TPM_clr_batch_corrected_v2.csv`](../Task2_input/TPM_clr_batch_corrected_v2.csv)
- [`Task2_input/metadata_final_matched.csv`](../Task2_input/metadata_final_matched.csv)

**Check the exact filenames in `Task2_input/` before running:** if the published filenames differ, use the actual filenames without modifying the data.

## Evaluation note

Only the input files and the agent-facing prompt should be supplied to the agent. Reference scripts and ground-truth outputs are published separately for transparency and must be excluded from the agent's analysis context. This is a public, open-book development benchmark, not a hidden-answer leaderboard.
