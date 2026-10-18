# Telecom churn research project

Start with [the manuscript](publication/Manuscript.docx) and [publication instructions](publication/README.md). This organized project has one current experiment: **ten splits, eleven configurations per split, 110 fitted models**. Earlier three-split reports and superseded drafts are archived and are not the final results.

The central measured finding is that the five-percentage-point senior recall constraint held on validation in every split but was exceeded on test data in seven of ten splits. Campaign economics are assumed currency units, not observed revenue or causal retention benefits. This is a retrospective single-benchmark study.

## Where things belong

| Location | Contents |
|---|---|
| `01_Data/` | One authoritative raw IBM CSV; cleaning happens in code |
| `config/study.json` | Current ten-split experiment configuration |
| `src/` | Training, validation, publication analysis, document building and packaging |
| `tests/` | Five focused methodological tests |
| `results/` | Current fitted models, predictions, metrics, provenance and training log |
| `publication/` | Manuscript, cover letter, author checklist, literature review and supplement |
| `publication/tables/` and `publication/figures/` | Generated current summaries and figures |
| `audit/` | Historical original-submission audit and retained local Python environment |
| `archive/` | Clearly labeled original submission and superseded work |

## Run and verify

The retained environment is `audit/.venv`; use its Python directly. It is a local dependency environment, not a research artifact. For a fresh installation, create `.venv` and install `requirements.txt` (direct research dependencies). `requirements-lock.txt` records the full tested macOS environment. The recorded run used Python 3.14.6; other environments have not been verified.

```sh
audit/.venv/bin/python -m unittest discover -s tests -v
audit/.venv/bin/python src/validate_results.py
audit/.venv/bin/python src/analyze_publication.py
```

To retrain all ten splits, run `audit/.venv/bin/python src/churn_study.py`. Its defaults now resolve to the current `config/study.json` and `results/`. To retrieve missing source data, run `audit/.venv/bin/python src/fetch_data.py`; it verifies the input hash and refuses a mismatch. Retraining overwrites generated results, so preserve a separate run if changing the protocol.

After intentional narrative edits, rebuild Word files with `src/build_documents.py` using a Python environment with `python-docx`, and visually check rendered pages. The editable narrative source is `publication/Manuscript.md`; the cover-letter text resides in the builder. Do not regenerate narrative claims automatically from an old draft generator. Run `src/package_supplement.py` after validation to refresh the supplement.

## Status and limitations

See [cleanup record](CLEANUP_REPORT.md), [protocol](PROTOCOL.md), and [current verification](publication/VERIFICATION.json). Internal checks do not establish external validity, statistically significant improvement, or publication acceptance. Author identity and declarations remain intentional placeholders. Nothing has been submitted.
