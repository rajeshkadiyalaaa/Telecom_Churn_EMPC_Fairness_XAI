# Corrected experiment protocol

This is a retrospective repair of an already inspected benchmark, not a preregistered confirmatory trial. The original three-split configuration and selection rules were fixed before running the replacement experiments. The ten-split extension was specified after those initial results were known; see publication/EXTENSION_PROTOCOL.md. No headline result from the original submission is used as a target to reproduce or tune toward.

## Data and partitions

The input is the provided 7,043-row IBM Telco CSV. IDs and targets never enter predictors. Whitespace TotalCharges values are set to zero only when tenure is zero, with a missingness indicator retained. Unexpected invalid entries cause an error. Zero filling is a modeling convention, not proof of historical billing values. Predictive features are a cross-sectional snapshot: there is no verified prospective feature timestamp or intervention outcome.

For each seed (42, 17, 2026, 7, 101, 211, 307, 401, 503, 601), make a churn-stratified 80/20 development/test split. Divide development into 75/25 remaining/validation, then remaining into 75/25 fitting/calibration. Approximate shares are 45/15/20/20. Exact customer IDs are exported. Repeats overlap and are not independent datasets. The old 42 split is intentionally retained as one diagnostic repeat; none is described as a newly untouched external test population.

Only fitting data trains estimators, scalers, encoders, and oversamplers. Calibration uses a separate unresampled partition. Validation chooses a primary model and thresholds. No early stopping or hyperparameter search uses test data. Test results are descriptive evaluations of frozen decisions. The primary model is selected independently within each repeat, not chosen after looking at test performance.

## Models and calibration

Compare LogisticRegression(max_iter=2000), RandomForest(n_estimators=200, min_samples_leaf=5, max_features=sqrt), and CatBoost(iterations=250, depth=5, learning_rate=0.05). Each is run unweighted, with balanced class weights, and with random oversampling of fitting rows. Logistic/RF preprocessing standardizes numeric fields and one-hot encodes categorical fields using only fitting data. CatBoost handles categories natively. All original predictors plus the missingness flag are retained for the primary comparison.

Fit a logistic calibrator on the base model logit/margin with C=1e6 and an intercept. This is regularized Platt-style calibration, not an assertion of perfect calibration. Report both raw and calibrated probabilities. Feature additions and exclusion of SeniorCitizen/gender are two fixed CatBoost baseline ablations, outside primary model selection. Excluding demographics does not remove all proxies or establish fairness.

Primary model selection maximizes validation scenario profit at the analytic economic threshold using calibrated probabilities; ties use lexical model name order. This defines a comparison of fixed configurations, not an exhaustive architecture competition.

## Economics and policies

Assume CLV=200, offer cost=10, contact cost=1, acceptance=0.3. Benefit per selected observed churner is acceptance*(CLV-offer)-contact=56; cost per selected observed non-churner is offer+contact=11. These are not measured customer values. All policies use >= threshold and keep tied scores together.

Evaluate contact none, contact all, standard 0.5, analytic economic threshold 11/67, validation-maximized profit, and validation-constrained equal opportunity. Equal opportunity maximizes validation profit over pairs of senior/non-senior thresholds subject to an absolute validation TPR difference <=0.05. Include contact none and contact all in the search. No claim guarantees that the constraint holds on test data. Group-specific rules are experimental and not deployment recommendations.

Empirical MPC searches all score cutoffs. Empirical EMPC integrates the maximum profit across those cutoffs under Beta(6,14), using 128-point Gauss-Legendre quadrature on [0,1]. When evaluated on test labels, it is explicitly an oracle descriptive score metric; its maximizing cutoff is not used as the deployed test policy. Sensitivity analysis reselects validation policies for CLV in {100,200,400} and acceptance in {0.1,0.3,0.5}; offer/contact costs stay fixed. No customer-specific CLV is inferred from cumulative spending.

## Measurement and uncertainty

Export AP, ROC-AUC, Brier, log loss, confusion matrices, recall, precision, FPR, F1, selection rate, and simulated profit. Calculate group statistics by ID-linked demographics for senior, gender, and intersections. Undefined precision is missing, not zero evidence of fairness. Signed senior TPR gap means senior minus non-senior; absolute gaps are used for constraints.

Use 1,000 paired bootstrap resamples stratified jointly by observed label, senior group, and gender. Intervals describe test-case uncertainty conditional on the fitted model, selected policy, and empirical stratum counts. They exclude economic-parameter and full training-selection uncertainty. Ten full retraining repeats summarize sensitivity, not population confidence intervals or independent significance tests. No causal, population-fairness, or state-of-the-art claim follows from these results.

## Explanations

Explain the fixed unweighted original-feature CatBoost comparator on seed 42, whether or not it wins model selection. CatBoost native path-dependent TreeSHAP uses training tree path statistics. Raw SHAP values sum to raw margin. For sigmoid calibration logit(p)=a*margin+b, multiply contributions by a and transform the base value by a*base+b. This is the affine Shapley transformation for the same game, not an explanation in probability units. Verify both raw additivity and reconstructed calibrated probabilities numerically. Select four actual test customers by probability order (minimum, one-third, two-thirds, maximum), not by a fabricated story or chosen outcome.

## Research scope

The study tests robustness of profit/fairness trade-offs and calibration rather than claiming invention of these methods. The focused literature map is in publication/LITERATURE_REVIEW.md; it does not establish a field-wide novelty claim. Publication also needs venue-specific review, data/license verification, and preferably independent external validation. Report negative findings, including fairness constraints failing to transfer to test data. Preserve the original misleading submission and disclose corrections and assistance as appropriate.
