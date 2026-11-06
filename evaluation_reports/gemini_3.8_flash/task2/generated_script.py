import json
import os
import numpy as np
import pandas as pd
from econml.dml import LinearDML
from sklearn.ensemble import RandomForestRegressor


def main():
    abundance_path = "/workspace/Task2_input/TPM_clr_batch_corrected_v2.csv"
    metadata_path = "/workspace/Task2_input/metadata_final_matched.csv"
    output_dir = "/workspace/output"
    os.makedirs(output_dir, exist_ok=True)

    taxa = ["Fusobacterium nucleatum_J", "Acidaminococcus intestini"]

    # 1. Load abundance matrix
    df_raw = pd.read_csv(abundance_path)
    if taxa[0] in df_raw.columns and taxa[1] in df_raw.columns:
        if "Sample_ID" in df_raw.columns:
            df_abundance = df_raw.set_index("Sample_ID")
        else:
            df_abundance = df_raw.set_index(df_raw.columns[0])
    elif df_raw.iloc[:, 0].isin(taxa).any():
        df_abundance = df_raw.set_index(df_raw.columns[0]).T
    else:
        df_raw_idx = pd.read_csv(abundance_path, index_col=0)
        if taxa[0] in df_raw_idx.columns:
            df_abundance = df_raw_idx
        else:
            df_abundance = df_raw_idx.T

    df_abundance.index = df_abundance.index.astype(str).str.strip()

    # 2. Load metadata
    df_meta = pd.read_csv(metadata_path)
    df_meta["Sample_ID"] = df_meta["Sample_ID"].astype(str).str.strip()

    # 3. Filter for Healthy and Cancer only (exclude Adenoma)
    df_meta = df_meta[df_meta["Group"].isin(["Healthy", "Cancer"])].copy()

    # 4. Encode outcome: Cancer = 1, Healthy = 0
    df_meta["Y"] = df_meta["Group"].map({"Cancer": 1, "Healthy": 0})

    # 5. Encode Sex: Male = 1, Female = 0
    def encode_sex(val):
        if pd.isna(val):
            return np.nan
        s = str(val).strip().lower()
        if s in ["male", "m", "1"]:
            return 1
        elif s in ["female", "f", "0"]:
            return 0
        return np.nan

    df_meta["Sex_encoded"] = df_meta["Sex"].apply(encode_sex)
    df_meta["Age"] = pd.to_numeric(df_meta["Age"], errors="coerce")
    df_meta["BMI"] = pd.to_numeric(df_meta["BMI"], errors="coerce")

    # 6. Merge with abundance data
    df_merged = df_meta.merge(
        df_abundance[taxa], left_on="Sample_ID", right_index=True, how="inner"
    )

    # 7. Retain samples with nonmissing outcome, both taxa, and all three covariates
    required_cols = ["Y", "Age", "BMI", "Sex_encoded"] + taxa
    df_merged = df_merged.dropna(subset=required_cols).copy()
    sample_count = len(df_merged)

    # Prepare covariates X in the exact order: Age, BMI, Sex
    X = df_merged[["Age", "BMI", "Sex_encoded"]].rename(
        columns={"Sex_encoded": "Sex"}
    )
    Y = df_merged["Y"].values

    results = []

    # 8. Fit DML for each taxon
    for taxon in taxa:
        T = df_merged[taxon].values

        model_y = RandomForestRegressor(
            n_estimators=200, min_samples_leaf=10, random_state=42
        )
        model_t = RandomForestRegressor(
            n_estimators=200, min_samples_leaf=10, random_state=42
        )

        dml = LinearDML(
            model_y=model_y,
            model_t=model_t,
            discrete_treatment=False,
            cv=5,
            random_state=42,
        )

        dml.fit(Y=Y, T=T, X=X)

        ate_val = float(np.ravel(dml.ate(X=X))[0])
        interval = dml.ate_interval(X=X)
        ci_lower = float(np.ravel(interval[0])[0])
        ci_upper = float(np.ravel(interval[1])[0])

        ci_excludes_zero = bool((ci_lower > 0) or (ci_upper < 0))

        results.append(
            {
                "taxon": taxon,
                "estimate": round(ate_val, 6),
                "ci_lower": round(ci_lower, 6),
                "ci_upper": round(ci_upper, 6),
                "ci_excludes_zero": ci_excludes_zero,
            }
        )

    output = {
        "task_id": "mgx_crc_dml_negative_control",
        "sample_count": sample_count,
        "results": results,
    }

    # Save output to file
    with open(os.path.join(output_dir, "results.json"), "w") as f:
        json.dump(output, f, indent=2)

    # Print JSON result
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
