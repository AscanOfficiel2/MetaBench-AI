"""MetaBench-AI | Task 2: two separate DML associations and negative control.
Run from repository root: python reference_scripts/task2_dml_negative_control.py
The estimates are model-adjusted associations, NOT established causal effects.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import sklearn
import econml
from sklearn.ensemble import RandomForestRegressor
from econml.dml import LinearDML

SEED = 42
np.random.seed(SEED)
ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "Task2_input"
OUTPUT = ROOT / "reference_results" / "task2"
OUTPUT.mkdir(parents=True, exist_ok=True)

microbiome = pd.read_csv(INPUT / "TPM_clr_batch_corrected_v2.csv", index_col=0)
metadata = pd.read_csv(INPUT / "metadata_final_matched.csv").set_index("Sample_ID")
microbiome.index = microbiome.index.astype(str).str.strip()
metadata.index = metadata.index.astype(str).str.strip()
if not microbiome.index.isin(metadata.index).any():
    if microbiome.columns.isin(metadata.index).any():
        microbiome = microbiome.T
    else:
        raise ValueError("No matching sample IDs between matrix and metadata")
if not microbiome.index.is_unique or not metadata.index.is_unique:
    raise ValueError("Duplicate sample IDs detected")
common = metadata.index.intersection(microbiome.index)
data = metadata.loc[common].join(microbiome.loc[common])
data = data[data["Group"].isin(["Cancer", "Healthy"])].copy()
data["Cancer_binary"] = (data["Group"] == "Cancer").astype(int)
data["Sex"] = data["Sex"].replace({"Male": 1, "Female": 0})
confounders = ["Age", "BMI", "Sex"]
taxa = ["Fusobacterium nucleatum_J", "Acidaminococcus intestini"]
cols = ["Cancer_binary", *taxa, *confounders]
for col in cols:
    data[col] = pd.to_numeric(data[col], errors="coerce")
data = data[cols].dropna()
print("N:", len(data), "Cancer:", sum(data.Cancer_binary == 1),
      "Healthy:", sum(data.Cancer_binary == 0))

def run_dml(taxon):
    y = data["Cancer_binary"].to_numpy()
    t = data[taxon].to_numpy()
    x = data[confounders].to_numpy()
    model_y = RandomForestRegressor(n_estimators=200, min_samples_leaf=10, random_state=SEED)
    model_t = RandomForestRegressor(n_estimators=200, min_samples_leaf=10, random_state=SEED)
    estimator = LinearDML(model_y=model_y, model_t=model_t,
                          discrete_treatment=False, cv=5, random_state=SEED)
    estimator.fit(y, t, X=x)
    estimate = float(estimator.ate(X=x))
    low, high = estimator.ate_interval(X=x)
    return {"Taxon": taxon, "Comparison": "Cancer_vs_Healthy", "N": len(data),
            "Estimate": estimate, "CI_lower": float(low),
            "CI_upper": float(high), "Seed": SEED}

results = pd.DataFrame([run_dml(taxon) for taxon in taxa])
results.to_csv(OUTPUT / "Task2_DML_GroundTruth.csv", index=False)
print(results.to_string(index=False))
(OUTPUT / "software_versions.txt").write_text(
    f"numpy={np.__version__}\npandas={pd.__version__}\n"
    f"scikit-learn={sklearn.__version__}\neconml={econml.__version__}\n"
)
