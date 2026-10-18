# Research correction record

## Original submission

The original six notebooks, six Word reports, and ten figure/table files are preserved byte-for-byte under `original_submission/`. Their original checksums are in that folder's manifest. The raw and cleaned data remain in `01_Data/`. The original claims are reviewed in `audit/AUDIT_REPORT.md`; original experiment outputs must not be cited as verified results.

## Corrected implementation

- Replaced hardcoded benchmarking with 33 actual fitted model configurations over three seeds. Deliberately narrowed the claimed architecture scope to Logistic Regression, Random Forest, and CatBoost; no claim is made to have implemented the original MLP, XGBoost or LightGBM experiment.
- Replaced missing Colab dependencies and paths with local, versioned configuration and reproducible Python entry points.
- Added schema validation, conditional missing-charge handling, explicit target/ID exclusion, and fitting-only transforms.
- Separated fitting, calibration, policy selection, and test partitions and persisted every customer ID assignment.
- Added disjoint logistic probability calibration; retained raw predictions for comparison.
- Used random oversampling as the mixed-data resampling comparator, explicitly replacing the original broken SMOTE path.
- Implemented threshold enumeration with tied-score handling and no-contact policies, true empirical EMPC integration, and validation-only threshold choice.
- Computed actual demographic/intersectional confusion matrices and fairness metrics from ID-linked predictions, including trained demographic-excluded and feature-engineered ablations.
- Added paired conditional bootstrap intervals and nine economic scenarios.
- Replaced fabricated SHAP tables with native CatBoost TreeSHAP and numerical checks of both raw-margin and calibrated-probability reconstruction.
- Archived unsupported prose and generated the corrected research report, abstract, figures and tables from executed outputs.
- Added meaningful mathematical tests and integration checks replaying all 66 saved probability files, plus an executed review/reproduction notebook.

## Remaining research limitations

No external dataset, prospective time split, observed campaign costs, treatment assignment, or offer acceptance outcomes were supplied. Therefore simulated profits do not measure realized revenue, and explanations do not identify causal interventions. Three overlapping splits are not independent datasets. The literature gap still requires a full systematic comparison before claiming novelty or submitting a paper. The corrected project reports these limits and the observed failure of fairness constraints to generalize in two splits.

## Organized final project on 18 October 2026

Made the ten-split configuration/results canonical; archived obsolete three-split work and unsubstantiated readiness claims; consolidated publication tooling under src; regenerated documents and supplement; added build provenance and a bounded verification record. See CLEANUP_REPORT.md. Earlier path references in this historical changelog describe the layout at the time.
