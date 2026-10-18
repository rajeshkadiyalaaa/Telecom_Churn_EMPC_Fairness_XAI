# Reproducibility supplement

This archive contains the corrected source, measured ten-split evidence, configuration, and publication analysis scripts. It excludes the original student submission, source data, fitted joblib estimators, and local environments. Per-customer predictions and split identifiers refer to the public IBM sample. Source retrieval and its expected SHA-256 are recorded, rather than asserting a new dataset license.

Extract into a new directory and run commands from its root. Python 3.14.6 and package versions in results/manifest.json were used. requirements-lock.txt records the complete macOS research environment; requirements.txt contains the direct computational dependencies for a leaner install. Other operating systems or Python versions may require compatible wheels and may yield small numeric differences.

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/fetch_data.py
.venv/bin/python -m unittest discover -s tests
.venv/bin/python src/churn_study.py --config config/study.json --output results
.venv/bin/python src/validate_results.py --output results --skip-original-archive
.venv/bin/python src/analyze_publication.py
```

Training regenerates all 110 estimators required by replay validation. The --skip-original-archive flag omits only the historical student-file preservation check, which is unrelated to the publication experiment; prediction, metric, provenance and group checks still run. Without training, the exported CSV evidence can already be summarized with analyze_publication.py. A missing estimator now causes replay validation to fail explicitly.

validation.json is the recorded check of the original complete run, not a claim that validation was performed on an extracted archive before models were regenerated. PACKAGE_SHA256.json permits integrity checks of the archive contents. No code license is assigned on behalf of an author; finalize rights and licensing before public deposit.

Important interpretation limits: economics are assumed, partitions overlap, the extension is retrospective, confidence intervals condition on fitted policies and fixed demographic/outcome counts, SHAP is descriptive, and there is no independent dataset or intervention validation. Read publication/EXTENSION_PROTOCOL.md and the manuscript for full methods and limitations.
