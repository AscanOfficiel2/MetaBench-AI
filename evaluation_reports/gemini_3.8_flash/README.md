# MetaBench-AI: Gemini 3.8 Flash Evaluation

**Evaluation date:** November 6, 2026  
**Model:** Gemini 3.8 Flash  
**Evaluation type:** Supervised computational benchmark  
**Tasks evaluated:** 2

## Objective

This evaluation assesses whether Gemini 3.8 Flash can generate executable scientific analysis code and reproduce independently established numerical reference results from metagenomic datasets.

Both tasks were performed using model-generated code executed within Docker environments with restricted access to task-specific datasets.

## Evaluation Results

| Task | Score | Execution |
|---|---|---|
| Task 1: Batch-effect evaluation | 3/3 (100%) | Successful |
| Task 2: DML negative-control analysis | 12/12 (100%) after JSON normalization | Successful |

### Task 1: Batch-effect evaluation

Gemini generated an R script that performed CLR transformation, feature filtering, batch correction using `limma`, and separate Euclidean PERMANOVA analyses.

**Results:**

- Largest technical factor: Project
- R² before correction: 0.066371
- R² after correction: 0.000761

The generated script reproduced all three graded reference fields.

The first execution exceeded the initial 600-second timeout. A subsequent execution using an 1,800-second limit completed successfully.

The batch-correction model generated warnings about non-estimable coefficients, reflecting limitations in independently estimating overlapping technical effects.

### Task 2: DML negative-control analysis

Gemini generated a Python script implementing `econml.LinearDML` with random-forest nuisance models and five-fold cross-fitting.

The analysis included 770 Healthy and Cancer samples.

| Taxon | Estimate | 95% confidence interval |
|---|---:|---|
| Fusobacterium nucleatum_J | 0.021408 | 0.015502 to 0.027315 |
| Acidaminococcus intestini | −0.002121 | −0.006653 to 0.002410 |

The model correctly identified that the confidence interval for *F. nucleatum_J* excludes zero, while the interval for *A. intestini* includes zero.

The original JSON used a list-based result structure that was not accepted by the grader. A separate normalization step converted it into the expected schema without modifying the numerical results.

The original submission received 0/12 format-dependent checks; the normalized submission passed 12/12 checks.

## Evaluation Protocol

The model received the benchmark prompts, permitted dataset paths and information about available scientific packages.

Gemini generated the analysis scripts independently. The scripts were reviewed by a human before execution inside Docker.

Reference scripts and ground-truth values were not supplied in the agent prompts.

## Limitations

- This evaluation involved one generated solution per task.
- Execution was supervised rather than fully autonomous.
- The benchmark reference values are publicly accessible.
- Task 1 required an extended execution timeout.
- Task 2 required JSON normalization for automated grading.
- Numerical agreement does not establish that all statistical assumptions were satisfied.
- The evaluation does not establish general superiority over other AI models.

## Conclusion

Gemini 3.8 Flash successfully generated executable code for both MetaBench-AI tasks and reproduced the numerical reference results within the specified tolerances.

These findings provide an initial proof of concept for evaluating computational scientific capabilities using MetaBench-AI. Additional models, repeated trials and standardized execution conditions are required for broader comparative conclusions.