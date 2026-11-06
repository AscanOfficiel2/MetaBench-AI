# Task 1: Metagenomic Batch-Effect Evaluation

**Task ID:** `mgx_batch_effect_evaluation`

## Agent-facing prompt

You are given a species-by-sample TPM abundance matrix and matched sample metadata from multiple colorectal cancer cohorts. The input files are `TPM_raw_filtered_bact.csv` (taxa in rows, samples in columns; first column contains taxon identifiers) and `metadata_final_matched.csv` (one row per sample; `Sample_ID` identifies samples).

Match the samples by `Sample_ID` and use only samples present in both files. Treat missing abundance entries as zero. Apply centered log-ratio (CLR) transformation separately to each sample, using a pseudocount of `1e-6`, and remove taxa with variance at or below `1e-12` across samples after CLR transformation.

Using `vegan::adonis2` with Euclidean distance, fit **separate one-factor PERMANOVA models** for `Project`, `Center_Name`, and `Instrument` on the CLR matrix. Then correct the CLR matrix using `limma::removeBatchEffect`, with `Project` as `batch`, the non-intercept columns of `model.matrix(~ Instrument + Center_Name)` as `covariates`, and `model.matrix(~ Group)` as `design` to retain disease-group-associated variation. Repeat the same one-factor PERMANOVA analyses on the corrected matrix.

**Question:** Which of the three technical factors has the highest *marginal* PERMANOVA R-squared before correction? Report its exact metadata field name, its R-squared before correction, and its R-squared after correction. Round numerical answers to six decimal places. Do not interpret a reduction in technical R-squared as proof that all biological information has been preserved.

Return **only** a JSON object in this format:

```json
{
  "task_id": "mgx_batch_effect_evaluation",
  "factor": "<metadata field name>",
  "r2_before": 0.0,
  "r2_after": 0.0
}
```

## Input files

- [`Task1_input/TPM_raw_filtered_bact.csv`](../Task1_input/TPM_raw_filtered_bact.csv)
- [`Task1_input/metadata_final_matched.csv`](../Task1_input/metadata_final_matched.csv)

## Evaluation note

Only the input files and the agent-facing prompt should be supplied to the agent. Reference scripts and ground-truth outputs are published separately for transparency and must be excluded from the agent's analysis context. This is a public, open-book development benchmark, not a hidden-answer leaderboard.
