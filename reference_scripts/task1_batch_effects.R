# MetaBench-AI | Task 1: CLR and batch-effect reference analysis
# Run from the repository root: Rscript reference_scripts/task1_batch_effects.R
suppressPackageStartupMessages({
  library(limma)
  library(vegan)
})
set.seed(43)
input_dir <- "Task1_input"
out_dir <- "reference_results/task1"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

tpm <- read.csv(file.path(input_dir, "TPM_raw_filtered_bact.csv"), row.names = 1, check.names = FALSE)
meta <- read.csv(file.path(input_dir, "metadata_final_matched.csv"), check.names = FALSE)
colnames(tpm) <- trimws(colnames(tpm))
meta$Sample_ID <- trimws(as.character(meta$Sample_ID))
stopifnot(!anyDuplicated(colnames(tpm)), !anyDuplicated(meta$Sample_ID))
common <- intersect(colnames(tpm), meta$Sample_ID)
stopifnot(length(common) > 0)
tpm <- as.matrix(tpm[, common, drop = FALSE])
storage.mode(tpm) <- "numeric"
meta <- meta[match(common, meta$Sample_ID), , drop = FALSE]
stopifnot(identical(colnames(tpm), meta$Sample_ID))
tpm[is.na(tpm)] <- 0
stopifnot(all(is.finite(tpm)), all(tpm >= 0))
stopifnot(!anyNA(meta[, c("Group", "Project", "Instrument", "Center_Name")]))

# CLR across taxa within each sample (species rows, sample columns).
pseudocount <- 1e-6
logged <- log(tpm + pseudocount)
clr_matrix <- t(sweep(logged, 2, colMeans(logged), FUN = "-"))
keep <- apply(clr_matrix, 2, var) > 1e-12
counts <- clr_matrix[, keep, drop = FALSE]
write.csv(counts, file.path(out_dir, "Task1_CLR_Filtered.csv"))

# V2 correction: preserve Group, remove Project, Instrument and Center_Name effects.
design <- model.matrix(~ Group, data = meta)
covars <- model.matrix(~ Instrument + Center_Name, data = meta)[, -1, drop = FALSE]
corrected <- t(removeBatchEffect(t(counts), batch = meta$Project,
                                 covariates = covars, design = design))
write.csv(corrected, file.path(out_dir, "Task1_CLR_BatchCorrected_V2.csv"))

factors <- c("Group", "Project", "Center_Name", "Instrument")
permanova <- function(x, stage) {
  do.call(rbind, lapply(factors, function(factor_name) {
    formula <- as.formula(paste("x ~", factor_name))
    ad <- adonis2(formula, data = meta, method = "euclidean", permutations = 999)
    data.frame(Stage = stage, Factor = factor_name,
               Df = ad$Df[1], SumOfSqs = ad$SumOfSqs[1],
               R2 = ad$R2[1], F = ad$F[1], P_value = ad$`Pr(>F)`[1])
  }))
}
set.seed(43)
before <- permanova(counts, "Before")
set.seed(43)
after <- permanova(corrected, "After_V2")
write.csv(before, file.path(out_dir, "Task1_PERMANOVA_Before.csv"), row.names = FALSE)
write.csv(after, file.path(out_dir, "Task1_PERMANOVA_After_V2.csv"), row.names = FALSE)
comparison <- merge(before[, c("Factor", "R2")], after[, c("Factor", "R2")],
                    by = "Factor", suffixes = c("_Before", "_After"), sort = FALSE)
comparison$R2_Change <- comparison$R2_After - comparison$R2_Before
comparison$Percent_Change <- 100 * comparison$R2_Change / comparison$R2_Before
write.csv(comparison, file.path(out_dir, "Task1_R2_Comparison.csv"), row.names = FALSE)
print(comparison)
cat("Note: separate one-factor PERMANOVA R2 values are marginal, not independent partitions.\n")
capture.output(sessionInfo(), file = file.path(out_dir, "R_session_info.txt"))
