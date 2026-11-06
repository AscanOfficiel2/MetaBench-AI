MetaBench-AI reference scripts

Copy task1_batch_effects.R and task2_dml_negative_control.py to reference_scripts/ in your repository.

Task 1 input filenames (in Task1_input/):
  TPM_raw_filtered_bact.csv
  metadata_final_matched.csv
Run: Rscript reference_scripts/task1_batch_effects.R
R dependencies: limma (Bioconductor), vegan (CRAN)

Task 2 input filenames (in Task2_input/):
  TPM_clr_batch_corrected_v2.csv (the ORIGINAL V2 matrix used for the 770-sample DML reference)
  metadata_final_matched.csv
Run: python reference_scripts/task2_dml_negative_control.py
Python dependencies: numpy, pandas, scikit-learn, econml

The figures from the full-cohort bootstrap demonstration are NOT outputs of the 770-sample benchmark.
The scripts were adapted from user-supplied scripts; they have not been executed end-to-end here because the original Task 2 V2 matrix is not attached in this turn.
