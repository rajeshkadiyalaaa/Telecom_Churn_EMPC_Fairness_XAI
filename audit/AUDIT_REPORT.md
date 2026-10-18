> Historical audit of the original submission. Paths below describe the pre-cleanup layout. Original artifacts now reside in archive/original_submission/; supporting audit outputs and scripts are preserved in archive/superseded_work.zip. Current research results are in results/.

# Telecom churn project evidence audit and research repair plan

Date: 18 October 2026

## Assessment

The project has a useful research theme and a substantially correct initial data audit, but its central experimental claims are not supported by the supplied implementation. It is not ready for academic submission. This requires rebuilding the experimental evidence, not merely editing the abstract or repairing notebook syntax.

The strongest confirmed problems are hardcoded fairness confusion matrices presented as empirical measurements, hardcoded SHAP attributions presented as model explanations, and a benchmark notebook that reads a results table instead of fitting the claimed models. Some reported statistics also contradict direct recomputation. These observations establish defects in the submitted artifacts. They do not establish who authored the numbers, whether experiments exist elsewhere, or deliberate misconduct by the student. Request any original training logs, models, predictions, and source history before drawing conclusions about intent.

This is the requested first-stage audit. Original files have been preserved. An independent audit script and a diagnostic model were executed; the complete six-stage research pipeline has not been repaired or validated yet. Do not describe the diagnostic model below as a reproduction of the claimed CatBoost experiment.

## Scope and evidence

Inspected all six notebook sources and their saved output structure, extracted text from all six Word report versions, inspected the result workbooks, and independently checked the local data. Compared the local raw table with the IBM download: values and row order match. Read selected primary research sources to check methodological and novelty claims. This was a targeted literature check, not a completed systematic review. Word layout and figure aesthetics were not the object of this audit.

Evidence files in this folder:

- `verify_project.py`: independent data, split, feature, failure-reproduction, and diagnostic-model checks.
- `verification_results.json`: measured results, package versions, and SHA-256 fingerprints of original project files.
- `verification_run.log`: execution output.
- `diagnostic_predictions.csv`: customer-keyed probabilities from the newly run logistic-regression baseline.
- `Step*.txt`: notebook source and saved text outputs, with zero-based cell indices.
- `Scientific_Research_Report*.txt`: extracted report text for locating claims.
- `requirements-audit.txt`: installed environment versions.

Run the independent checks from the project root with `audit/.venv/bin/python audit/verify_project.py`. The virtual environment is local to this audit. The original package versions are unknown; none were supplied. New results describe the recorded audit environment.

## Confirmed findings and their consequences

### 1 The 24-model-configuration experiment is not implemented

Evidence: Step 3, code cells 1 and 3. The notebook imports Logistic Regression and Random Forest, resamples training data, defines a focal-loss class and a prior-adjustment function, then reads `Step3_MultiModel_Imbalance_Benchmark_Table.csv`. That CSV is missing; an XLSX exists instead. There is no classifier fitting, probability prediction, cross-validation loop, neural-network architecture, optimizer, or training loop. CatBoost, LightGBM, and XGBoost are not trained there. The reported five-fold scores have no generating procedure.

Consequently ROC-AUC 0.856, average precision 0.684, calibrated Brier 0.132, model rankings, and all claimed comparative improvements are unsupported by this submission. Converting XLSX to CSV would only allow printing the existing numbers; it would not reproduce the experiment.

Repair: implement actual estimators, fold-contained preprocessing, model selection, prediction exports, and metric generation. Require every benchmark row to identify its model configuration, split, seed, and prediction artifact.

### 2 Step 2 does not provide the promised model-ready representation

Evidence: Step 2, cells 3 and 5. The feature function starts with a copy of the original table, adds features, and retains the original text categories and `TotalCharges`. It does not implement the claimed categorical encoding or actually remove the supposedly replaced predictors. Fifteen text columns remain after dropping IDs and labels.

Executing the submitted feature function, the submitted scaling operation, and Step 3's SMOTE operation produces `ValueError: could not convert string to float: 'Male'`. This is a confirmed computational failure independent of the missing Colab files. The supplied folder also lacks both Step 2 preprocessed CSVs; its hardcoded `/content/drive/MyDrive/...` paths do not work locally.

Repair: use a single explicit feature schema and fitted preprocessing pipeline. Keep raw demographic attributes and IDs in a separate audit table. For mixed data, choose categorical-aware sampling or justify the geometry of encoded sampling. Do not assume ordinary SMOTE on one-hot columns creates valid customer records.

### 3 Fairness measurements are supplied constants rather than prediction-derived results

Evidence: Step 5, cells 2 and 3. Subgroup sizes and all TP, FP, TN, FN counts are typed into dictionaries. The notebook does not load customer-level predictions, retrain a model without demographic variables, or optimize group thresholds. It has no saved execution outputs. Absence of outputs alone would not prove non-execution, but the hardcoded source proves that these cells do not measure fairness from the fitted model.

The actual stated split (`test_size=0.20`, `random_state=42`, stratification by churn) produces:

| Test subgroup | Recomputed size | Recomputed churners | Step 5 assumed size | Step 5 assumed churners |
|---|---:|---:|---:|---:|
| Senior | 222 | 98 | 228 | 95 |
| Non-senior | 1,187 | 276 | 1,181 | 279 |
| Female | 687 | 193 | 698 | 188 |
| Male | 722 | 181 | 711 | 186 |

The test total of 1,409 and 374 churners is correct, but matching totals do not validate subgroup counts. Step 2's saved demographic summary also differs from both the recomputation and Step 5.

Withdraw the claimed measured fairness gaps, the “unawareness fails” experiment, and the claim that equal opportunity costs only $23 until reproduced. The $23 arithmetic is correct for the supplied hypothetical counts, but the counts have not been established as observations.

### 4 SHAP results and customer explanations are manually supplied

Evidence: Step 6, cells 1–3. There is no SHAP import, explainer construction, model loading, or model prediction. Global attributions are literal numbers in `global_shap_df`; local contributions are literal dictionaries in `archetypes`. No customer IDs connect those archetypes to held-out observations. Some feature names also differ from the implementation, such as `Contract_Tenure_Stability_Index` versus `Contract_Tenure_Stability`.

The notebook sets the explanation baseline to the logit of test-set prevalence. A SHAP baseline must come from the explained model and the chosen background/perturbation convention; it is not generally the logit of empirical class prevalence. In general, the mean logit is not the logit of the mean probability. Raw tree explanations also do not automatically explain an arbitrarily calibrated wrapper. See [TreeExplainer documentation](https://shap.readthedocs.io/en/latest/generated/shap.TreeExplainer.html).

Withdraw all claimed global rankings and observed local attributions. The claims that “82%” of senior risk is mediated by modifiable features and that a billing credit will rescue a customer have no supporting mediation analysis or intervention experiment. Even genuine SHAP values explain model behavior, not causal treatment effects.

### 5 Feature statistics and orthogonalization claims do not reproduce

Evidence: Step 2 cell 5, Step 2 workbook, and final report sections 3 and 4. The VIF calculation uses a literal correlation matrix rather than calculating correlations from the actual training partition. Its saved output includes a Stage C computation and scaler checks absent from the cell source. Step 3 also contains a saved plot without corresponding plotting code. These are provenance inconsistencies; stale outputs are one possible explanation.

Using the submitted feature formulas on all 7,043 rows:

| Quantity | Reported | Recomputed |
|---|---:|---:|
| Billing residual correlation with churn | +0.118 | −0.000307 |
| Realized monthly ratio correlation | −0.114 | −0.011971 |
| Protection count correlation | −0.264 | −0.173061 |
| Protection to streaming ratio correlation | −0.318 | −0.167869 |
| Average price per service range | 6.04–70.70 | 8.65–36.125 |
| Realized monthly ratio range | 0.78–1.24 | 0.689356–1.573453 |

On the actual training partition, raw three-variable `TotalCharges` VIF is 9.68294. In the three-variable replacement block, billing-residual VIF is 1.00008. But within the six scaled variables, tenure VIF is 3.42872 and contract-tenure stability VIF is 3.01560, already contradicting the claimed maximum below 2.34. These are subset-specific VIFs, not a validation of the entire design matrix. Retaining service components alongside their sums can introduce exact dependencies.

Subtracting `MonthlyCharges * tenure` from a cumulative bill is not regression residualization and does not prove statistical orthogonality. Positive residuals here mean the current-rate extrapolation exceeds observed cumulative charges; this does not prove historical overbilling or bill shock. Preserve such a feature only as a neutrally named candidate and test it through ablation.

### 6 The profit threshold has valid algebra but the empirical EMPC claim is incorrect

Under the explicitly assumed payoff `56*TP - 11*FP`, the probability break-even threshold is `11/67 = 0.164179`. That derivation is valid when the probability and payoff assumptions are appropriate. The reported $10,358 and $14,841 also follow arithmetically from the supplied counts. They are not verified campaign outcomes.

Step 4's integration function substitutes an analytic probability cutoff for every acceptance rate. It does not maximize empirical profit over available score cutoffs, and it truncates and renormalizes the acceptance distribution. Thus it does not implement the general empirical EMPC defined by integrating the threshold-wise maximum. It also promises an instance-dependent CLV function that is absent; the plotting function accepts monthly charges but never uses them. The diagnostic plot call is commented out, and no probabilities are produced upstream.

Keep distinct: fixed-policy scenario profit, MPC maximized over empirical score thresholds, and EMPC integrating those maxima. Include the contact-nobody option. A threshold selected using test outcomes cannot subsequently be presented as an independently evaluated deployment policy. The canonical reference provides the cost assumptions and maximization definitions, not evidence of this project's realized gains. See [Höppner et al., equations 14–17](https://arxiv.org/pdf/1712.08101).

### 7 Calibration is asserted rather than measured

The prior-odds adjustment function is a useful conditional mathematical identity, but it is not called on predictions in Step 3. Its “exact restoration” claim depends on valid probabilities and prior-shift assumptions. SMOTE-ENN changes feature distributions and boundary structure; focal loss is not merely changing the class prior. A blanket correction does not guarantee calibration.

Equal subgroup precision at a single threshold also does not prove probability calibration or absence of bias. Estimate calibration on held-out or cross-fitted development predictions, measure Brier/log loss and reliability, and evaluate the frozen calibrated pipeline on outer evaluation data.

### 8 Statistical and scientific interpretations are too strong

- Opposite correlations of monthly and cumulative charges with churn do not establish Simpson's paradox. Demonstrate aggregate versus within-stratum reversal for the same association, or use the more limited description “different marginal associations related to tenure.”
- Eleven zero-tenure blanks justify investigating a zero-charge convention. They do not mathematically prove the unobserved billing values are zero. The unconditional `fillna(0)` also replaces any future unexpected nonnumeric value. Assert the eligible rows and compare reasonable alternatives.
- Retaining those rows does not establish that survival bias has been eliminated.
- Close fairness point estimates are not “exact parity”; report uncertainty and a predeclared tolerance. Different base rates do not by themselves force every fairness statistic to differ. The incompatibility result has specific conditions; it is not an empirical proof of the project's mechanisms. See [Chouldechova](https://arxiv.org/abs/1703.00056).
- A few manually selected policy points are not a demonstrated Pareto frontier. Evaluate candidate policies and identify non-dominated ones.
- The 80% ratio should be described as a chosen screening heuristic here, not a demonstrated telecom compliance test. A ratio defined as min/max is bounded by one, making the table's upper acceptance bound of 1.25 irrelevant to that definition.
- Positive targeting allocates an offer. Define who benefits and what harms are being measured before declaring one fairness criterion scientifically superior.
- No confidence intervals, retraining uncertainty, feature ablation experiment, or external validation supports the superiority claims.

### 9 Literature and report provenance require repair

The final abstract refers to research-matrix rows that are absent from the supplied project. Report versions disagree: Updated Step 5 describes five different engineered predictors and CatBoost ROC-AUC 0.8482, whereas the final report claims a different feature set and 0.856. No run IDs or change record explain these differences.

The project calls another paper's AUC 0.992 “impossible” and attributes it definitively to pre-split ENN deleting all difficult test cases. AUC 0.992 is mathematically possible. The [IIETA paper](https://www.iieta.org/journals/isi/paper/10.18280/isi.300910) does report high AUCs and describes splitting/cross-validation, but that does not establish the exact causal diagnosis claimed by this project. There are methodological questions worth investigating, including test-based model-selection language. Critique documented procedures precisely; do not assert an unverified replication or mechanism.

## What the student did well

1. Chose a useful decision problem: churn prediction should be evaluated in relation to retention decisions, economic assumptions, and allocation across demographic groups.
2. Correctly identified a subtle data-quality issue. All 11 whitespace `TotalCharges` entries, their row indices, zero tenures, and non-churn labels reproduce. The supplied cleaned CSV exactly matches recomputation of the stated transformation.
3. Correctly reported 7,043 unique customers, no exact duplicate rows, and 1,869 churners. The train/test total sizes and class counts also reproduce.
4. Intended to split before fitting scalers and keep resampling within training. Step 2 actually fits its scaler only on training. Preserve this principle and extend it to every validation fold.
5. Selected useful evaluation concepts: probability-based ROC-AUC, average precision, Brier score, confusion matrices, and subgroup error rates. The missing work is calculating them from real experiments.
6. Derived the assumed-payoff threshold correctly and explicitly acknowledged that campaign economics are assumed. Preserve this separation while replacing unsupported empirical counts.
7. Organized the work into sensible stages. The six-stage structure can become a useful teaching workflow once each stage has executable evidence and acceptance checks.

Credit should be given for these sound choices, without treating an attractive plan as a completed experiment.

## Independently executed diagnostic results

I fitted a fixed, untuned logistic regression using the original predictors, training-only standardization, and training-fitted one-hot encoding. IDs and both target columns were excluded. Zero-charge imputation followed the existing convention. The 80/20 split matches the stated seed and stratification. This is a diagnostic benchmark on an already inspected dataset, not new confirmatory evidence.

| Metric or policy | New measured result |
|---|---:|
| ROC-AUC | 0.842171 |
| Average precision | 0.635015 |
| Brier score | 0.137978 |
| Threshold 0.5: TP / FP / TN / FN | 210 / 108 / 927 / 164 |
| Threshold 11/67: TP / FP / TN / FN | 337 / 419 / 616 / 37 |
| Assumed payoff at 0.5 | 10,572 currency units |
| Assumed payoff at 11/67 | 14,263 currency units |

The lower threshold catches more observed churners but also selects more retained customers. This illustrates why the research question is useful. It does not validate the original CatBoost results, prove real retention benefit, or establish superiority over competing models. No confidence intervals or model selection were performed for this small diagnostic run.

## A defensible academic research direction

Provisional title: **Calibration and economic uncertainty in fairness constrained telecom churn targeting**

The defensible contribution should be a carefully controlled investigation, not a claim that using profit, fairness, and SHAP together is automatically novel. Profit-sensitive churn modeling already exists in [Höppner et al.](https://arxiv.org/abs/1712.08101). The authors' repository for [Rahman, Janssens, and Bogaert](https://github.com/ShimantoRahman/churn-preprocessing) identifies a 2025 Journal of Business Research paper combining profit-driven churn preprocessing with fairness techniques. Its fairness application is not necessarily identical to demographic parity; compare the actual objectives. A recent paper titled [Predictability Is Not Profitability](https://www.mdpi.com/2078-2489/17/9/880) also explicitly combines calibration, explanations, and profit evaluation. Its abstract/search record was available, but full-text retrieval failed in this audit. Inspect its full methods before asserting novelty.

Candidate gap, still to be validated through a systematic literature matrix: **How stable is the measured cost of demographic fairness when probabilities are calibrated correctly and retention economics, sampling strategy, and evaluation splits vary?**

Research questions:

1. Do imbalance remedies improve decision profit after calibration, or mainly shift the effective decision threshold?
2. How does a validation-selected equal-opportunity constraint change simulated profit and offer coverage across economic scenarios?
3. Are those trade-offs stable across splits, demographic intersections, and a second independent dataset?
4. Do engineered features improve out-of-sample performance and explanation stability relative to the original predictors?

Treat the IBM data as a public benchmark, not a field retention trial. IBM describes related 7,043-customer Telco sample data as involving a fictional company; document the exact version and provenance. See [IBM's sample description](https://community.ibm.com/community/user/blogs/steven-macko/2019/07/11/telco-customer-churn-1113). This CSV contains no observed intervention assignments, offer acceptance outcomes, or counterfactual retention outcomes. It cannot establish causal effectiveness of offers or realized incremental revenue. A second data source should be independent, not a re-upload or expanded version of the same sample.

## Step by step implementation plan

| Phase | Implementation | Acceptance evidence |
|---|---|---|
| 1 Preserve and classify claims | Keep original artifacts; record hashes; mark each claim as reproduced, contradicted, assumption, or unsupported. Preserve any recovered original logs separately. | Claim ledger with source locations and evidence links. |
| 2 Establish the research gap | Build a primary-paper matrix covering data, splitting, calibration, economic objective, fairness definition, uncertainty, and code availability. Verify citation details and claims. | Narrow contribution statement that survives comparison with existing work. |
| 3 Freeze an evaluation protocol | Predeclare objectives, models, tuning budgets, seeds, economic scenarios, fairness tolerance, and primary comparisons. Use outer evaluation folds with inner fitting/tuning/calibration/policy selection. | Saved split IDs and protocol; no outer-test use for choosing models or thresholds. |
| 4 Repair data and features | Add local configuration, schema assertions, conditional handling of blanks, preprocessing pipelines, and a separate demographic/ID audit table. Compare original versus engineered predictors. | Raw-to-feature reproducibility; target/ID exclusion; fold-isolation checks. |
| 5 Implement real baselines | Start with dummy, regularized logistic regression, and a strong tree booster. Add RF, other boosters, and the MLP only with an explicit scientific purpose and comparable budgets. | Actual fitted models, per-fold predictions, hyperparameters, timings, and seeds. |
| 6 Study imbalance and calibration | Compare no resampling, class weights, and justified mixed-data resampling within folds. Compare uncalibrated probabilities with sigmoid/isotonic or cross-fitted calibration as appropriate. | Out-of-sample AP, ROC-AUC, Brier, log loss, reliability plots and uncertainty. |
| 7 Implement decision economics | Add fixed-threshold, contact-none, contact-all, and capacity-matched policies. Implement genuine empirical MPC/EMPC separately from fixed-policy expected profit. Vary CLV, contact cost, offer cost and acceptance assumptions. | Unit-tested hand examples; policy chosen on development data; held-out scenario results. |
| 8 Implement fairness experiments | Join real predictions to demographics by ID. Fit demographic-included and excluded variants. Choose group thresholds using development data and a stated tolerance/budget. | Group counts reconcile to totals; uncertainty, achieved test gaps, and any infeasibility are reported. |
| 9 Implement genuine explanations | Explain actual fitted model outputs with documented background data and output scale. Select real customer IDs by a declared rule. Handle calibration explicitly. | Additivity checks, genuine global/local figures, and explanation stability analysis. |
| 10 Quantify uncertainty | Use paired comparisons on the same evaluation cases, stratified bootstrap for fixed-model test metrics, and repeated outer evaluation for training variability. Address multiple primary comparisons. | Confidence intervals and effect sizes; no treating correlated CV folds as independent observations. |
| 11 Validate scope | Add an independent dataset where feasible; use temporal evaluation only when genuine timestamps exist. Examine imputation and feature-ablation sensitivity. | Generalization evidence or an explicitly narrow single-benchmark limitation. |
| 12 Regenerate the manuscript | Generate tables and figures from logged outputs, rewrite abstract last, package environment/configuration, and rerun from a fresh environment. | Every numerical claim traceable to predictions; manuscript agrees with the final run. |

Because the existing data and split have already been extensively inspected, a new random split alone does not magically create an untouched confirmatory study. Repeated nested evaluation improves internal estimation; external data or a genuinely prospective evaluation strengthens confirmation. State this limitation openly.

The student should be able to explain the target, each transformation, probability calibration, threshold selection, fairness objective, and the origin of every reported number. Maintain an experiment log and disclose AI assistance according to the eventual institution/venue policy. Do not promise a performance increase; null or negative results are valid research findings.

## Repairing the abstract

The existing abstract says the study resolves three research gaps across completed experiments. That is presently unsupported. It also treats a broad research theme as an established novel contribution and jumps from predictive explanation to individualized intervention.

Use this as a **proposal abstract**, not a completed-results abstract:

> Customer churn classifiers can achieve useful predictive accuracy without establishing whether their retention decisions are economically robust or equitably allocated. This study proposes a reproducible evaluation of how probability calibration, class-imbalance treatment, and decision thresholds affect simulated retention profit and demographic error-rate disparities. Using the public IBM Telco benchmark, we will compare baseline and gradient-boosting models under an evaluation design that separates model fitting, calibration, policy selection, and final assessment. Economic parameters will be treated as scenario assumptions, and fairness constraints will be selected using development data. Feature ablations, repeated evaluation, and model-derived SHAP explanations will assess performance and explanation stability. The study will quantify trade-offs and uncertainty rather than infer causal retention benefits from observational labels. Its intended contribution is an auditable assessment of the robustness of fairness-constrained churn targeting under alternative economic assumptions.

After experiments finish, replace future tense with completed methods and add measured primary results with confidence intervals, the actual dataset count, and the principal limitation. Do not put the original 0.856, 43.3%, $23, or 82% claims back unless new evidence supports the exact statements.

## Publication readiness

At present this is a repairable student project, not a supported research manuscript. A rigorous single-benchmark reproduction/robustness study may suit an applied workshop or student research venue. A stronger journal submission needs a clearly demonstrated contribution, adequate uncertainty analysis, and preferably independent validation. Venue selection should follow the completed contribution; acceptance cannot be guaranteed.

Before submission, require a clean-environment run, recoverable models and predictions, a complete bibliography and literature matrix, data/license documentation, traceable tables, an honest limitations section, and appropriate disclosure of assistance. If earlier versions have already been shared or submitted, prepare a factual correction identifying which results were unsupported rather than silently replacing them.

The immediate result of this audit is that the original headline model, fairness, and SHAP claims should not be used as empirical evidence. The verified data audit, sensible decision framing, and correctly derived assumed-payoff threshold provide a sound starting point for rebuilding the research.
