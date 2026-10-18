# Validation to test transfer of equal opportunity constraints in profit sensitive telecom churn prediction

[Author 1 full publication name] and [Author 2 if applicable]

[Department and institution or independent researcher affiliation, city, country]

Corresponding author [Name and email] | ORCID [Optional]

Author completion copy — replace all bracketed administrative fields before submission.

## Abstract

Purpose: This study examines whether a demographic recall constraint selected on validation data transfers to held-out telecom churn data while preserving profit under explicit economic assumptions.

Methods: A retrospective analysis used 7,043 records from the public IBM Telco Customer Churn benchmark. Ten stratified splits separated fitting, calibration, policy selection, and testing. Logistic regression, random forests, and CatBoost were compared with baseline, class-weighted, and randomly oversampled training. A validation-selected model supported global profit thresholds and senior-group thresholds constrained to an absolute true-positive-rate gap of at most five percentage points. Campaign values were assumed; paired bootstrap intervals were conditional on fitted policies.

Results: All ten constrained policies satisfied the validation tolerance, but seven exceeded it on test data. The median test gap was 5.62 percentage points, ranging from 1.86 to 11.79. Constrained-minus-global scenario profit differences ranged from −430 to +235 currency units per 1,409 test customers, with a median of +4.5. Across nine economic scenarios, constraint exceedances ranged from two to seven splits.

Conclusion: A validation fairness constraint did not reliably transfer within this benchmark. Its economic effect depended on the split and assumed campaign values. These results support separate reporting of selection-stage compliance and held-out fairness, without establishing causal retention benefits or external validity.

Keywords: customer churn; equal opportunity; profit-sensitive classification; calibration; reproducibility; telecom

## 1 Introduction

Churn classifiers rank customers by estimated attrition risk, but a retention campaign also requires a decision rule. Classification accuracy alone does not specify which customers should receive an offer or whether its expected benefit exceeds its cost. Profit-based churn metrics and decision trees already address this distinction [1, 2]. Adding a demographic constraint introduces a further question: does a rule that satisfies the constraint on the policy-selection sample also satisfy it on held-out customers?

Profit and fairness are not new combined concerns. Rahman and colleagues use fairness-inspired preprocessing to prioritize customer-value groups in business-to-business churn modeling [3]. Maw and colleagues evaluate demographic fairness under imbalance and sampling in telecom churn [4]. Recent work combines explanations, survival modeling, profitability, and fairness auditing [5]; another recent study evaluates explainability and cost-sensitive churn decisions across sectors [6]. These precedents rule out claiming that merely combining profit, fairness, and explanations constitutes a novel research contribution.

The present contribution is narrower: a fully recorded empirical assessment of validation-to-test transfer for a deterministic senior-group recall constraint, with a separate calibration partition and explicit economic assumptions. Equal opportunity motivates equal true-positive rates across groups [7]. Here the favorable action is receiving a retention contact among customers labeled as churners. This operational interpretation does not establish that contact benefits every customer, that the label is normatively ideal, or that equal recall constitutes comprehensive fairness.

Three research questions guide the analysis. RQ1 asks how often the five-percentage-point validation constraint is exceeded on held-out test splits. RQ2 asks how constrained and global profit thresholds differ under fixed campaign assumptions and alternative economic scenarios. RQ3 examines calibration, feature ablations, and additive explanations as supporting checks. This is a retrospective benchmark study, not a new learning algorithm or an independently confirmed intervention study.

## 2 Materials and methods

### 2.1 Dataset and study design

The supplied file matches the public IBM repository CSV [8]. It contains 7,043 customer records, 21 original columns, and 1,869 churn labels (26.54%). The customer identifier and outcome are excluded from predictors. Eleven blank TotalCharges values occur at zero tenure; these are set to zero and a missing-charge indicator is retained. Other invalid numeric charges cause the pipeline to fail rather than being silently imputed. The supplied gender and SeniorCitizen fields are used as recorded; the binary indicators cannot represent the full complexity of gender or age.

For each seed, stratified random partitioning yields 3,168 fitting records, 1,057 calibration records, 1,409 validation records, and 1,409 test records. Stratification is by outcome, not by demographic intersection. The fixed seeds are 42, 17, 2026, 7, 101, 211, 307, 401, 503, and 601. Records overlap between repetitions, so ten splits are not ten independent datasets. Results from the initial three seeds were known before the extension to ten was specified. The extension retained model settings and all seeds; it is explicitly a retrospective sensitivity analysis, not preregistration. The benchmark had also been inspected previously, which limits the interpretation of the test partitions as completely untouched scientific evidence.

### 2.2 Models and calibration

The primary comparison crosses three families with three training regimes: unmodified class frequencies, balanced class weights, and random oversampling of the minority class. Oversampling uses only the fitting partition. Logistic regression uses a maximum of 2,000 iterations. Random forests use 200 trees, minimum leaf size five, and square-root feature sampling. CatBoost uses 250 boosting iterations, depth five, learning rate 0.05, and log-loss training. Other estimator settings follow the recorded package defaults. Hyperparameters are fixed; there is no test-guided tuning or claim that these are optimal models.

For logistic regression and random forests, numerical standardization and categorical one-hot encoding are fitted within the training pipeline; unseen categories are ignored. CatBoost processes categorical variables natively. A logistic sigmoid calibrator with C = 1,000,000 is fitted on the separate calibration partition. Its input is the CatBoost raw margin or the clipped logit of predicted probabilities for the other families. Calibration is assessed by Brier score and log loss, with ROC AUC and average precision reported separately. Calibration is an estimation step, not a guarantee; the broader literature likewise distinguishes discrimination from calibrated probabilities [9].

Two fixed CatBoost ablations add six domain-motivated features or remove gender and SeniorCitizen. The engineered features summarize current-rate versus cumulative-charge differences, protection-to-streaming counts, price per service, contract–tenure interaction, early lifecycle, and a fiber/electronic-check/monthly-contract interaction. Exact definitions appear in the code. These ablations are excluded from the nine-candidate primary selection pool. Each ablation is retrained; demographic exclusion is not simulated by editing a stored metric.

### 2.3 Economic assumptions and policy selection

The base scenario assumes customer value 200, offer cost 10, contact cost 1, and offer acceptance probability 0.30, expressed in arbitrary currency units. For a contacted customer labeled as a churner, expected net value is acceptance multiplied by customer value minus offer cost, less contact cost: 0.30 × (200 − 10) − 1 = 56. For a contacted non-churner, the assumed loss is offer cost plus contact cost, or 11. Uncontacted customers contribute zero incremental campaign value. Thus scenario profit is 56 times the number of true positives minus 11 times the number of false positives. This stylized payoff assumes different offer-cost realization for would-be churners and non-churners and constant value across customers. It is not observed revenue or a causal estimate of retention uplift.

For calibrated churn probability, the resulting Bayes cutoff is 11 divided by 67, approximately 0.1642. The selected primary model maximizes validation scenario profit at this cutoff; ties are resolved lexically by model name. Its predictions are then used for six policies: contact none, contact all, cutoff 0.5, the assumed Bayes cutoff, a single validation-profit-maximizing cutoff, and a constrained pair of group cutoffs. The global cutoff is searched over every realizable score threshold, including no contact, with tied scores kept together. Profit ties prefer fewer contacts.

The group policy searches all pairs of realizable SeniorCitizen cutoffs and maximizes validation scenario profit subject to an absolute senior-group true-positive-rate difference of at most 0.05. This deterministic search is motivated by equal opportunity [7] but is not the full randomized postprocessing construction. The first maximizing pair in the ordered search resolves ties. Thresholds and the model are frozen before application to the test partition. No test label participates in the deployed threshold selection. Demographic group membership is required at application time; practical use would require an appropriate governance and legal assessment.

### 2.4 Evaluation and uncertainty

The primary endpoint is the descriptive count of splits exceeding the 0.05 absolute test TPR-gap tolerance. Secondary outcomes include scenario profit, contact rate, recall, false-positive rate, and group confusion matrices. Gender and age-by-gender intersections are audited but not constrained. Equal recall does not imply equal selection rates, false-positive rates, or calibration; fairness criteria can conflict [10]. No hypothesis test or binomial confidence interval is applied to the overlapping split count.

Within each test split, 1,000 bootstrap replicates resample with replacement within outcome-by-SeniorCitizen-by-gender strata. The same resampled customers are used for both policies when estimating their profit difference. The 2.5th and 97.5th percentiles form conditional intervals. These intervals keep fitted models, selected thresholds, and stratum counts fixed; they omit training and selection uncertainty and are not population-level confidence guarantees. No multiple-comparison adjustment is applied, so isolated intervals excluding zero are descriptive findings.

A nine-scenario analysis crosses customer values 100, 200, and 400 with acceptance probabilities 0.10, 0.30, and 0.50. Offer and contact costs remain 10 and 1. The originally selected model is held fixed, while each scenario reselects its global and constrained cutoffs on validation data. This assesses policy sensitivity, not full model reselection for each economic scenario.

An empirical expected maximum profit criterion integrates the maximum attainable score-threshold profit over a Beta(6,14) acceptance distribution using 128-node Gauss–Legendre quadrature [1, 2]. This exported score is explicitly an oracle ranking diagnostic: because each maximum uses the evaluated sample labels, it is not the realized profit of a deployable test-selected policy. It is kept separate from the frozen-policy results.

### 2.5 Explanations and computational verification

Native CatBoost path-dependent TreeSHAP explanations [11] are computed for the fixed baseline CatBoost model in seed 42, whether or not it wins primary selection. Training tree-path statistics define the explanation background. Raw-margin contributions are multiplied by the sigmoid calibration slope, with the intercept included in the transformed base value. Summing these calibrated-logit contributions and applying the sigmoid reconstructs the calibrated probability. Contributions are not additive probability effects, causal drivers, or evidence that changing a feature would prevent churn.

The experiment exports split identifiers, fitted estimators, probabilities, decisions, group counts, configurations, package versions, and source/data hashes. A separate replay script reloads every fitted estimator and reconstructs the saved calibrated predictions and metrics. OpenAI Codex assisted code development, execution, literature retrieval, and manuscript drafting. [Authors must verify the analysis and text and finalize the AI-use disclosure before submission.] AI assistance is not assigned authorship.

## 3 Results

### 3.1 Fairness constraint transfer

Every constrained policy met the validation tolerance, with validation gaps between 1.22 and 4.66 percentage points. Seven of ten test splits exceeded five percentage points. The median absolute test gap was 5.62 percentage points, with a range of 1.86–11.79 (Table 1 and Fig. 1). This count describes the ten specified repetitions only. It is not an estimate based on ten independent deployments. The test gap was signed in the exported metrics; Table 1 uses absolute values, so direction should be consulted in the supplementary files when interpreting which group received more contacts among churners.

[TABLE1]

[FIGURE1]

### 3.2 Scenario profit and uncertainty

Mean constrained test scenario profit was 14,125.7 currency units per 1,409 customers, compared with 14,101.3 for the global validation-profit cutoff, 14,152.2 for the assumed Bayes cutoff, 10,035.1 for cutoff 0.5, 9,559.0 for contact all, and zero for contact none. These overlapping-split averages are descriptive. The constrained-minus-global difference had median +4.5 and ranged from −430 to +235. The mean difference of +24.4 does not establish a general economic benefit from the constraint.

Conditional paired bootstrap intervals excluded zero positively for seeds 42 and 401 and negatively for seed 211; seven intervals included zero (Fig. 2). A constraint can appear to improve test profit even though it restricts the validation search, because unconstrained validation optimization can overfit its own sample. The experiment does not identify the precise mechanism for a particular split. Both profit sign and fairness transfer should therefore be reported instead of selecting a favorable repetition.

[FIGURE2]

### 3.3 Discrimination calibration and ablations

Primary validation selection chose logistic regression in six splits, CatBoost in three, and a random forest in one. Among the eleven configurations, mean calibrated test ROC AUC ranged from 0.8430 to 0.8468. Baseline CatBoost had mean AUC 0.8468 and Brier score 0.1344; these values do not establish statistical superiority over the alternatives (Table 2). Selection for profit and ranking by AUC need not agree.

[TABLE2]

Calibration reduced mean test Brier score by approximately 0.0171–0.0312 for weighted or oversampled configurations. For the three original-feature baseline models it slightly increased mean Brier score, by approximately 0.00005–0.00021. Thus calibration corrected substantial probability distortion in some regimes but was not uniformly beneficial. These are observed paired changes, not a universal justification for a calibration method.

The engineered CatBoost ablation had mean AUC 0.8465 and Brier score 0.1348, compared with 0.8468 and 0.1344 for original features. Removing the two demographic inputs yielded AUC 0.8460 and Brier score 0.1348. Neither feature engineering nor demographic exclusion established an improvement in discrimination or calibration here. Excluding demographic inputs also does not establish demographic fairness, because other variables may carry correlated information and the fairness constraint is a separate decision-stage operation.

### 3.4 Economic sensitivity and verification

Across the nine economic scenarios, constrained test-gap exceedances ranged from two to seven of ten splits (Table 3). The value-400, acceptance-0.50 scenario had two exceedances and a median gap of 2.54 percentage points, whereas the base scenario had seven and a median gap of 5.62. Economic parameters alter the preferred contact set and therefore measured recall differences. These assumed scenarios are not estimated from campaign outcomes.

[TABLE3]

All 220 saved validation/test probability artifacts were replayed successfully. Group counts reconciled with overall confusion matrices in 180 policy-by-attribute checks. The maximum raw SHAP additivity discrepancy was 7.99 × 10⁻¹⁵, and calibrated probability reconstruction differed by at most 6.66 × 10⁻¹⁶. These checks establish internal numerical consistency, not external predictive validity, causal explanation, or freedom from all software errors.

## 4 Discussion

The main finding concerns the gap between enforcing a constraint and demonstrating that it transfers. A model developer can truthfully report validation compliance while the frozen policy exceeds the same tolerance on test data. In this benchmark, that occurred in seven of ten specified splits. Separate reporting of the constraint-selection sample, threshold values, held-out group counts, and uncertainty prevents validation compliance from being mistaken for a population guarantee.

The effect on scenario profit was small on average relative to total assumed profit but variable in sign. Reporting only an average would hide the −430 result in seed 211 and positive differences in other seeds. Likewise, a large economic benefit over cutoff 0.5 would mainly demonstrate the importance of the chosen cost assumptions and threshold rule, not necessarily a superior predictive model. Contact-all and contact-none comparators provide useful anchors, while the Bayes cutoff separates probability-based action from empirical threshold optimization.

The prior literature already addresses profitability [1, 2], customer-value allocation [3], imbalance and demographic auditing [4], and broad explainable retention frameworks [5, 6]. This study contributes a reproducible, limited benchmark result on constraint transfer rather than a claim that these topics were previously disconnected. Its strongest reusable component is the separation of fitting, calibration, policy selection, and evaluation, together with customer-level decision evidence.

Several limitations bound the findings. The analysis uses one public demonstration benchmark, which cannot establish transfer to a current telecom population. Random splitting does not represent temporal drift or a future deployment. The initial results and dataset had already been inspected before the ten-split extension. Small demographic subgroup counts can make recall gaps unstable, and the stratified bootstrap fixes those counts. Economic values, acceptance, and offer outcomes are assumed; churn probability is not treatment effect, and a high-risk customer may not respond to contact. The constant-value payoff omits heterogeneous value, capacity constraints, heterogeneous response, and campaign interference.

The five-percentage-point tolerance is a chosen operational constraint, not a justified legal or ethical threshold. It covers only one binary age indicator and one error-rate dimension. The explanation analysis covers one fixed CatBoost model and split, so it cannot establish explanation stability across models or customers. The fixed hyperparameters and limited candidate pool also preclude claims of state-of-the-art prediction. Results on multiple independent datasets, a temporal holdout, and sensitivity to the fairness tolerance would strengthen external and methodological evidence. A randomized campaign or defensible treatment-effect design would be required to estimate actual incremental retention value.

## 5 Conclusion

On the supplied IBM telecom benchmark, a senior-group equal-opportunity constraint selected on validation data exceeded its five-percentage-point tolerance on seven of ten held-out test splits. Its scenario-profit effect changed sign across repetitions and depended on assumed economics. The study supports transparent separation of validation compliance, held-out fairness, and hypothetical campaign value. It does not establish a new fairness algorithm, causal retention gains, or deployment readiness.

## Declarations

Funding: [Insert verified funding statement and grant numbers, or explicitly confirm no funding.]

Competing interests: [Insert verified declaration for every author.]

Author contributions: [Identify each actual author and their contributions. Remove unused author placeholders.]

Ethics and consent: This analysis uses the public IBM benchmark and involves no newly recruited participants or intervention. [Authors must verify applicable institutional requirements and supply any required ethics or consent statement; no approval or exemption is asserted here.]

Data availability: The source benchmark is available from the IBM repository [8]. The supplied input hash and retrieval instructions accompany the reproducibility materials. No access to private telecom operational records is claimed.

Code availability: Source code, configuration, dependency versions, and measured result tables are included in the accompanying reproducibility package. [Insert the final public repository or archival DOI after author review and deposit; no public deposit is claimed at this stage.]

Acknowledgments: [Add verified acknowledgments or remove this paragraph.]

## References

[1] Verbraken T, Verbeke W, Baesens B. A Novel Profit Maximizing Metric for Measuring Classification Performance of Customer Churn Prediction Models. IEEE Transactions on Knowledge and Data Engineering. 2013;25:961-973. https://doi.org/10.1109/TKDE.2012.50

[2] Höppner S, Stripling E, Baesens B, Broucke Sv, Verdonck T. Profit driven decision trees for churn prediction. European Journal of Operational Research. 2020;284:920-933. https://doi.org/10.1016/j.ejor.2018.11.072

[3] Rahman S, Janssens B, Bogaert M. Profit-driven pre-processing in B2B customer churn modeling using fairness techniques. Journal of Business Research. 2025;189:115159. https://doi.org/10.1016/j.jbusres.2024.115159

[4] Maw M, Haw SC, Ho CK. Utilizing data sampling techniques on algorithmic fairness for customer churn prediction with data imbalance problems. F1000Research. 2022;10:988, version 2. https://doi.org/10.12688/f1000research.72929.2

[5] Vutla BA, Hasan R, Mahmood S. An explainable survival aware intelligence framework for customer retention decision support beyond static churn prediction. Discover Informatics. 2026;1:25. https://doi.org/10.1007/s44564-026-00025-y

[6] Fidan E, Aksoy S, Demircioglu P, Bogrekci I. Predictability Is Not Profitability: An Explainable, Cost-Sensitive Evaluation of Customer Churn Across Three Sectors. Information. 2026;17:880. https://doi.org/10.3390/info17090880

[7] Hardt M, Price E, Srebro N. Equality of Opportunity in Supervised Learning. Advances in Neural Information Processing Systems. 2016;29. https://arxiv.org/abs/1610.02413

[8] IBM. Telco customer churn on ICP for Data. Public repository and data/Telco-Customer-Churn.csv. Accessed 18 October 2026. https://github.com/IBM/telco-customer-churn-on-icp4d

[9] Guo C, Pleiss G, Sun Y, Weinberger KQ. On Calibration of Modern Neural Networks. Proceedings of Machine Learning Research. 2017;70:1321–1330. https://proceedings.mlr.press/v70/guo17a.html

[10] Chouldechova A. Fair Prediction with Disparate Impact: A Study of Bias in Recidivism Prediction Instruments. Big Data. 2017;5:153-163. https://doi.org/10.1089/big.2016.0047

[11] Lundberg SM, Erion G, Chen H, DeGrave A, Prutkin JM, Nair B, Katz R, Himmelfarb J, Bansal N, Lee S. From local explanations to global understanding with explainable AI for trees. Nature Machine Intelligence. 2020;2:56-67. https://doi.org/10.1038/s42256-019-0138-9
