# Focused literature review and contribution boundary

Search/review date: 18 October 2026. This is a focused, non-systematic review, not a PRISMA review or proof that no related study exists. Queries covered “profit fairness telecom churn calibration”, “profit driven preprocessing fairness churn”, “equal opportunity churn threshold”, and recent explainable profit-sensitive churn research. Foundational references were followed from primary article citations. Primary publisher pages, author manuscripts, official proceedings, and repository sources were preferred. Crossref metadata was saved separately; one F1000 version-2 request was rate-limited, so its bibliographic details use the article/version record rather than a successful Crossref response.

| Source | Relevant evidence | Distinction from this study | Review basis |
|---|---|---|---|
| Verbraken et al., 2013, https://doi.org/10.1109/TKDE.2012.50 | Profit-sensitive churn evaluation and expected maximum profit | Foundational metric; our frozen-policy profit is kept separate from an oracle diagnostic | Primary author repository and metadata |
| Höppner et al., 2020, https://doi.org/10.1016/j.ejor.2018.11.072 | Profit-driven decision trees and churn payoff formulation | Our classifiers are conventional; contribution concerns demographic constraint transfer | Publisher abstract and author preprint |
| Rahman et al., 2025, https://doi.org/10.1016/j.jbusres.2024.115159 | Fairness-inspired preprocessing for customer-value groups in two B2B cases | High/low customer value differs from the binary senior-group recall constraint here | Full author manuscript |
| Maw et al., revised 2022, https://doi.org/10.12688/f1000research.72929.2 | Telecom imbalance, sampling and gender fairness auditing | Prevalence variants of one underlying dataset are not independent external datasets; our endpoint is frozen-threshold transfer | Primary article text/version record |
| Vutla et al., 2026, https://doi.org/10.1007/s44564-026-00025-y | Integrated survival, explainability, profit and fairness retention framework across datasets | Prior integration directly limits broad novelty claims; present work focuses on validation-selected constraint transfer | Full publisher article |
| Predictability Is Not Profitability, 2026, https://doi.org/10.3390/info17090880 | Explainable cost-sensitive churn evaluation across sectors | Stronger dataset breadth than this study; no claim that combining explainability and economics is novel | Publisher search abstract and Crossref; full text not reliably accessible |
| e-profits, 2026, https://doi.org/10.1007/s41060-026-01044-6 | Business-aligned profit-sensitive churn metric | Additional recent metric context; no unsupported claim about absence of demographic methods | Publisher abstract and metadata; not used as central manuscript evidence |
| Hardt et al., 2016, https://arxiv.org/abs/1610.02413 | Equal opportunity and postprocessing | Our deterministic exhaustive threshold search is not the full randomized construction | Primary preprint |
| Guo et al., 2017, https://proceedings.mlr.press/v70/guo17a.html | Probability calibration | General calibration reference, not evidence that calibration always improves telecom models | Official proceedings |
| Chouldechova, 2017, https://doi.org/10.1089/big.2016.0047 | Tensions between fairness criteria | Equal recall alone is not comprehensive fairness | Primary preprint and metadata |
| Lundberg et al., 2020, https://doi.org/10.1038/s42256-019-0138-9 | Tree-based additive explanation methods | Numerical additivity does not imply causal explanation | Publisher article and CatBoost method documentation |

## Defensible research gap

The specific question examined here is whether a validation-selected, profit-maximizing deterministic age-group recall constraint remains within tolerance on the held-out parts of this public benchmark, across explicitly recorded repeated partitions and economic assumptions. This is a local empirical question. The review does not establish a field-wide absence of similar evaluations, and the manuscript makes no “first” claim.

## Contribution and limits

The package provides a four-part data separation, real retraining and calibration, customer-level reproducibility evidence, conditional paired uncertainty, and an honestly negative transfer result. It does not provide new algorithmic theory, a causal retention intervention, externally validated fairness, or observed campaign value. A second independently sourced dataset and temporal or prospective evaluation would strengthen a later extension. The current results should not be rewritten to imply that those validations occurred.
