# Metagenomic Batch-Effect Evaluation
suppressPackageStartupMessages({
  library(vegan)
  library(limma)
})

# Define input file paths
tpm_file <- if (file.exists("/workspace/Task1_input/TPM_raw_filtered_bact.csv")) {
  "/workspace/Task1_input/TPM_raw_filtered_bact.csv"
} else {
  "Task1_input/TPM_raw_filtered_bact.csv"
}

meta_file <- if (file.exists("/workspace/Task1_input/metadata_final_matched.csv")) {
  "/workspace/Task1_input/metadata_final_matched.csv"
} else {
  "Task1_input/metadata_final_matched.csv"
}

# 1. Read input data
tpm <- read.csv(tpm_file, row.names = 1, check.names = FALSE, stringsAsFactors = FALSE)
metadata <- read.csv(meta_file, check.names = FALSE, stringsAsFactors = FALSE)

# Treat missing abundance entries as zero
tpm[is.na(tpm)] <- 0
tpm <- as.matrix(tpm)

# 2. Match samples present in both files
common_samples <- intersect(metadata$Sample_ID, colnames(tpm))
metadata <- metadata[match(common_samples, metadata$Sample_ID), ]
tpm <- tpm[, common_samples]

# 3. Apply Centered Log-Ratio (CLR) transformation separately to each sample
# Pseudocount: 1e-6
log_tpm <- log(tpm + 1e-6)
clr_mat <- sweep(log_tpm, 2, colMeans(log_tpm), "-")

# 4. Remove taxa with variance at or below 1e-12 across samples after CLR
taxa_var <- apply(clr_mat, 1, var)
clr_filtered <- clr_mat[taxa_var > 1e-12, , drop = FALSE]

# CLR matrix with samples in rows for vegan::adonis2
clr_transposed <- t(clr_filtered)

# 5. Fit separate one-factor PERMANOVA models before correction
factors <- c("Project", "Center_Name", "Instrument")
r2_before <- numeric(length(factors))
names(r2_before) <- factors

for (f in factors) {
  form <- as.formula(paste("clr_transposed ~", f))
  fit <- vegan::adonis2(form, data = metadata, method = "euclidean", permutations = 999)
  r2_before[f] <- fit$R2[1]
}

# 6. Batch correction using limma::removeBatchEffect
# - Project as batch
# - Non-intercept columns of model.matrix(~ Instrument + Center_Name) as covariates
# - model.matrix(~ Group) as design
cov_mat <- model.matrix(~ Instrument + Center_Name, data = metadata)
covariates <- cov_mat[, colnames(cov_mat) != "(Intercept)", drop = FALSE]
design_mat <- model.matrix(~ Group, data = metadata)

clr_corrected <- limma::removeBatchEffect(
  clr_filtered,
  batch = metadata$Project,
  covariates = covariates,
  design = design_mat
)

clr_corr_transposed <- t(clr_corrected)

# 7. Repeat one-factor PERMANOVA on the corrected matrix
r2_after <- numeric(length(factors))
names(r2_after) <- factors

for (f in factors) {
  form <- as.formula(paste("clr_corr_transposed ~", f))
  fit_post <- vegan::adonis2(form, data = metadata, method = "euclidean", permutations = 999)
  r2_after[f] <- fit_post$R2[1]
}

# 8. Identify the factor with the highest marginal PERMANOVA R-squared before correction
best_factor <- names(which.max(r2_before))
best_r2_before <- round(r2_before[best_factor], 6)
best_r2_after <- round(r2_after[best_factor], 6)

# Construct and print final JSON
json_output <- sprintf(
  '{\n  "task_id": "mgx_batch_effect_evaluation",\n  "factor": "%s",\n  "r2_before": %.6f,\n  "r2_after": %.6f\n}',
  best_factor,
  best_r2_before,
  best_r2_after
)

cat(json_output, "\n")
