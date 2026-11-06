## How to use MetaBench-AI
MetaBench-AI currently provides two open development benchmark tasks. Each task has an agent-facing prompt, input datasets, and independently computed reference results.



## Run a task
1. Open the task prompt linked above and download the files in its input folder.
2. Start an AI-agent session that can read local CSV files and execute R or Python as required. Supply only the task prompt and its corresponding input files; do not supply the ground-truth workbook or reference scripts.
3. Ask the agent to carry out the analysis and return its answer in the JSON format specified in the task prompt.
4. Save the JSON response and compare its numerical fields with the reference results in MetaBench_AI_Ground_Truth.xlsx using the proposed tolerances (Task 1: ±0.0001 for each R-squared; Task 2: ±0.002 for point estimates). Confidence-interval tolerances have not yet been validated. An automated grader is planned.
5. Record the agent/model name, version, software environment, input file versions, and whether the agent actually ran the analysis. Report failures as observed only after testing.
   
## Important limitations
- Public answers: Ground truths and reference scripts are visible in this repository. These tasks are suitable for reproducibility demonstrations and development testing, not for leakage-resistant model ranking.
- Task independence: Task 2 uses its own original V2 processed matrix; do not replace it with the output of Task 1.
- Interpretation: PERMANOVA R-squared values are marginal, and DML estimates from observational data are not proof of causation.
- Provenance: Cite the original cohort datasets and confirm redistribution permissions before reusing the underlying data.
