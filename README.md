# MetaBench-AI

### Reproducible Benchmarks for Evaluating AI Agents in Metagenomics

**MetaBench-AI** is an open-source benchmark collection designed to evaluate the ability of artificial intelligence (AI) agents to perform scientifically rigorous, reproducible and interpretable analyses of metagenomic data.

The project focuses on analytical challenges commonly encountered in microbiome research, including compositional data processing, batch-effect assessment, confounder-aware statistical inference and biological interpretation.

Rather than evaluating whether an AI agent can simply execute bioinformatics commands, MetaBench-AI aims to test whether it can make appropriate analytical decisions, recover verifiable results and avoid scientifically consequential errors.

**Current version:** v0.1.0 (development)

---

## 1. Scientific Motivation

Modern metagenomics involves multiple analytical challenges that require both computational proficiency and biological understanding.

Microbiome datasets are frequently sparse, compositional and heterogeneous across studies. Differences in sequencing platforms, laboratory protocols, cohort characteristics and host-associated variables can introduce variation that complicates biological interpretation.

As AI agents become increasingly capable of executing computational workflows, evaluating their scientific reliability becomes essential.

MetaBench-AI addresses this need through data-dependent tasks with independently calculated reference answers and predefined grading criteria.

The initial benchmark collection draws on multi-cohort gut metagenomic research investigating microbial associations with colorectal cancer (CRC).

## 2. Benchmark Tasks

MetaBench-AI currently includes two complementary tasks.

### Task 1: Compositional Processing and Batch-Effect Evaluation

**Task ID:** `mgx_batch_effect_evaluation`

**Objective:** Evaluate whether an AI agent can appropriately process species-level metagenomic abundance data, identify technical variation and assess batch correction.

**Input data:**
- Species-level TPM abundance matrix.
- Matched sample metadata containing disease status, cohort identifiers and sequencing-related variables.

**Required analysis:**
- Apply centered log-ratio (CLR) transformation using a pseudocount of 1 × 10⁻⁶.
- Remove zero-variance features.
- Evaluate technical variation using separate, one-factor Euclidean PERMANOVA models.
- Perform batch correction using `limma::removeBatchEffect`, accounting for Project, Instrument and Center_Name while preserving Group in the model design.
- Identify the technical factor with the largest marginal PERMANOVA R² before correction and report its R² before and after correction.

**Reference results:**

| Factor | R² before correction | R² after correction |
|---|---:|---:|
| Project | 0.066371 | 0.000761 |
| Center_Name | 0.054737 | 0.000538 |
| Instrument | 0.045340 | 0.000377 |
| Group | 0.009690 | 0.009073 |

**Expected answer:** Project, with R² = 0.066371 before correction and R² = 0.000761 after correction.

**Proposed grading tolerance:** ±0.0001 for each R² value.

**Scientific challenges evaluated:** Compositionality, sample alignment, technical heterogeneity, marginal variance interpretation and batch-correction assessment.

### Task 2: Confounder-Aware Microbial Association and Negative-Control Evaluation

**Task ID:** `mgx_crc_dml_negative_control`

**Objective:** Evaluate whether an AI agent can estimate confounder-adjusted microbial associations with CRC status and interpret negative-control findings appropriately.

**Input data:**
- CLR-transformed, batch-corrected species abundance matrix.
- Matched clinical metadata.

**Required analysis:**
- Restrict the analysis to Healthy and Cancer samples, excluding Adenoma.
- Encode Cancer as 1 and Healthy as 0.
- Evaluate `Fusobacterium nucleatum_J` and `Acidaminococcus intestini` as separate continuous exposures.
- Adjust for Age, Sex and BMI.
- Apply `econml.LinearDML` with five-fold cross-fitting, random-forest nuisance models (200 estimators, minimum leaf size 10), `discrete_treatment=False` and random seed 42.
- Report adjusted estimates and 95% confidence intervals.

**Reference results (770 samples):**

| Taxon | Adjusted estimate | 95% confidence interval |
|---|---:|---|
| *Fusobacterium nucleatum_J* | 0.021408 | 0.015502–0.027315 |
| *Acidaminococcus intestini* | −0.002120 | −0.006650–0.002410 |

**Proposed grading tolerance:** ±0.002 for the point estimates. Confidence-interval grading tolerances require further validation.

**Scientific challenges evaluated:** Appropriate disease-group selection, taxonomic precision, confounder adjustment, cross-fitting, negative-control reasoning and interpretation of observational associations.

The DML estimates are model-dependent adjusted associations. They should not be interpreted as definitive evidence of causality.

## 3. Repository Structure

```text
MetaBench-AI/
├── README.md
├── Task1_input/
├── Task2_input/
├── benchmarks/
│   ├── task1_batch_effects.md
│   └── task2_dml_negative_control.md
├── reference_scripts/
│   ├── task1_batch_effects.R
│   ├── task2_dml_association.py
│   └── task2_dml_negative_control.py
├── reference_results/
│   └── MetaBench_AI_Ground_Truth.xlsx
└── docs/
```

Some directories represent the intended repository organization and may be added progressively.

## 4. Datasets and Provenance

The benchmark uses harmonized species-level metagenomic abundance data and associated metadata derived from publicly sourced colorectal cancer cohorts.

The datasets are organized into two task-specific input directories:

- [Task 1 input data](https://github.com/AscanOfficiel2/MetaBench-AI/tree/main/Task1_input)
- [Task 2 input data](https://github.com/AscanOfficiel2/MetaBench-AI/tree/main/Task2_input)

The input matrices are derived analytical datasets, not raw sequencing reads. Task 1 uses the filtered TPM matrix, whereas Task 2 uses the original V2 CLR-transformed and batch-corrected matrix associated with its reference DML analysis.

Detailed cohort accession information, preprocessing provenance and data redistribution permissions should be documented before the first stable release.

## 5. Reference Analysis and Reproducibility

Reference analyses were developed using R and Python.

**Task 1** uses `compositions`, `limma`, `vegan` and `dplyr` for compositional transformation, batch correction and PERMANOVA.

**Task 2** uses `pandas`, `numpy`, `scikit-learn` and `econml` for confounder-adjusted DML estimation.

The reference scripts and results are intended to allow independent verification of the benchmark answers. Numerical results depend on the specified datasets, preprocessing choices and computational environments.

Software versions and end-to-end execution instructions will be documented as part of the repository's reproducibility validation.

## 6. Benchmark Evaluation

MetaBench-AI is designed around deterministic evaluation of numerical and categorical outputs.

Each task includes a scientific question, specified input data, reference answer, grading tolerance and anticipated analytical failure modes.

The current collection provides reference analyses and proposed grading criteria. An automated evaluation harness and systematic testing against AI agents are planned for subsequent development.

Reference answers should be withheld from agents during evaluation to avoid answer leakage.

## 7. Scientific Limitations

The benchmark has several important limitations:

- Its initial tasks are derived from CRC-associated gut metagenomic data and do not represent the full diversity of metagenomics applications.
- Batch-associated PERMANOVA R² values are marginal and should not be interpreted as independent contributions to total variation.
- Reduction of technical variation does not establish that batch correction preserves all biologically meaningful information.
- DML estimates from observational data depend on modelling and identification assumptions and do not independently establish causality.
- The proposed grading tolerances require further evaluation against alternative correct implementations.
- The current benchmark collection has not yet undergone systematic evaluation across multiple AI models.

## 8. Development Roadmap

Future development will focus on automated grading, independent reproducibility testing, evaluation of AI-agent performance and expansion into additional metagenomics domains.

Potential extensions include taxonomic profiling, MAG quality assessment, functional annotation, microbial ecological modelling and cross-cohort generalization.

## 9. Project Development and Contributions

MetaBench-AI is developed and maintained by **AbdulAziz Ascandari**, building on research experience in microbiome science, shotgun metagenomics, computational biology and statistical modelling.

The initial analytical workflows draw on collaborative research and should retain appropriate attribution to contributing researchers and original cohort data providers.

Contributions, suggestions and scientific discussions are welcome through GitHub Issues.

## 10. Citation and License

## License

The original MetaBench-AI software and reference scripts are released under the MIT License.

See the [LICENSE](LICENSE) file for details.

The underlying metagenomic datasets may be subject to separate data-use and redistribution conditions. The MIT License does not override those conditions.

**Repository:** https://github.com/AscanOfficiel2/MetaBench-AI

---

*MetaBench-AI is an evolving research resource intended to support transparent and reproducible evaluation of scientific AI agents in metagenomics.*
