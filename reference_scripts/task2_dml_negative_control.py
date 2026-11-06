
"""MetaBench-AI | Task 2: Two separate DML associations and negative control.

Run from repository root:
python reference_scripts/task2_dml_negative_control.py

The estimates are model-adjusted associations,
NOT established causal effects.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
import econml

from sklearn.ensemble import RandomForestRegressor
from econml.dml import LinearDML


# ==========================================================
# 1. REPRODUCIBILITY AND PATHS
# ==========================================================

SEED = 42
np.random.seed(SEED)

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "Task2_input"
OUTPUT = ROOT / "reference_results" / "task2"

OUTPUT.mkdir(parents=True, exist_ok=True)


# ==========================================================
# 2. LOAD MICROBIOME MATRIX AND METADATA
# ==========================================================

microbiome = pd.read_csv(
    INPUT / "TPM_clr_batch_corrected_v2.csv",
    index_col=0
)

metadata = pd.read_csv(
    INPUT / "metadata_final_matched.csv"
)

# Remove metadata rows without sample IDs
metadata = metadata.dropna(
    subset=["Sample_ID"]
).copy()

# Set sample IDs as index
metadata = metadata.set_index("Sample_ID")

# Clean sample identifiers
microbiome.index = (
    microbiome.index.astype(str).str.strip()
)

microbiome.columns = (
    microbiome.columns.astype(str).str.strip()
)

metadata.index = (
    metadata.index.astype(str).str.strip()
)

# Remove any remaining empty sample identifiers
metadata = metadata[
    metadata.index != ""
].copy()


# ==========================================================
# 3. VERIFY MATRIX ORIENTATION AND SAMPLE ALIGNMENT
# ==========================================================

# Expected orientation: samples x species
if not microbiome.index.isin(metadata.index).any():

    if microbiome.columns.isin(metadata.index).any():
        microbiome = microbiome.T

    else:
        raise ValueError(
            "No matching sample IDs between matrix and metadata."
        )

# Check duplicate sample IDs
if not microbiome.index.is_unique:
    raise ValueError(
        "Duplicate sample IDs detected in microbiome matrix."
    )

if not metadata.index.is_unique:
    raise ValueError(
        "Duplicate sample IDs detected in metadata."
    )

# Match samples
common = metadata.index.intersection(
    microbiome.index
)

if len(common) == 0:
    raise ValueError("No matching samples found.")

data = metadata.loc[common].join(
    microbiome.loc[common]
)

print("\n===== DATA ALIGNMENT =====")
print("Matched samples:", len(common))
print("Merged dimensions:", data.shape)


# ==========================================================
# 4. SELECT CANCER AND HEALTHY SAMPLES
# ==========================================================

data = data[
    data["Group"].isin(["Cancer", "Healthy"])
].copy()

data["Cancer_binary"] = (
    data["Group"] == "Cancer"
).astype(int)

# Encode sex
data["Sex"] = data["Sex"].replace({
    "Male": 1,
    "Female": 0
})


# ==========================================================
# 5. DEFINE TAXA AND CONFOUNDERS
# ==========================================================

confounders = ["Age", "BMI", "Sex"]

taxa = [
    "Fusobacterium nucleatum_J",
    "Acidaminococcus intestini"
]

cols = [
    "Cancer_binary",
    *taxa,
    *confounders
]

# Verify required columns
missing = [
    col for col in cols
    if col not in data.columns
]

if missing:
    raise ValueError(
        f"Missing required columns: {missing}"
    )

# Convert to numeric
for col in cols:
    data[col] = pd.to_numeric(
        data[col],
        errors="coerce"
    )

# Remove incomplete observations
data = data[cols].dropna()

print("\n===== FINAL ANALYSIS DATA =====")

print("N:", len(data))
print(
    "Cancer:",
    sum(data["Cancer_binary"] == 1)
)
print(
    "Healthy:",
    sum(data["Cancer_binary"] == 0)
)


# ==========================================================
# 6. DOUBLE MACHINE LEARNING FUNCTION
# ==========================================================

def run_dml(taxon):

    y = data["Cancer_binary"].to_numpy()
    t = data[taxon].to_numpy()
    x = data[confounders].to_numpy()

    model_y = RandomForestRegressor(
        n_estimators=200,
        min_samples_leaf=10,
        random_state=SEED
    )

    model_t = RandomForestRegressor(
        n_estimators=200,
        min_samples_leaf=10,
        random_state=SEED
    )

    estimator = LinearDML(
        model_y=model_y,
        model_t=model_t,
        discrete_treatment=False,
        cv=5,
        random_state=SEED
    )

    estimator.fit(y, t, X=x)

    estimate = float(
        estimator.ate(X=x)
    )

    low, high = estimator.ate_interval(
        X=x
    )

    return {
        "Taxon": taxon,
        "Comparison": "Cancer_vs_Healthy",
        "N": len(data),
        "Estimate": estimate,
        "CI_lower": float(low),
        "CI_upper": float(high),
        "Seed": SEED
    }


# ==========================================================
# 7. RUN TARGET AND NEGATIVE-CONTROL ANALYSES
# ==========================================================

results = pd.DataFrame([
    run_dml(taxon)
    for taxon in taxa
])

print("\n===== TASK 2 DML RESULTS =====")
print(results.to_string(index=False))


# ==========================================================
# 8. SAVE GROUND-TRUTH RESULTS
# ==========================================================

results.to_csv(
    OUTPUT / "Task2_DML_GroundTruth.csv",
    index=False
)

print("\nGround-truth results saved.")


# ==========================================================
# 9. SAVE SOFTWARE VERSIONS
# ==========================================================

(OUTPUT / "software_versions.txt").write_text(
    f"numpy={np.__version__}\n"
    f"pandas={pd.__version__}\n"
    f"scikit-learn={sklearn.__version__}\n"
    f"econml={econml.__version__}\n"
)

print("Software versions saved.")
print("\nTask 2 analysis completed.")
