# Cleanup and accuracy corrections

18 October 2026

The active project now has one ten-split configuration, one results directory, one narrative source, and one publication package. The raw input and training implementation are unchanged; moving files did not create new experiments.

## Corrected problems

- The root README, default configuration, and three-split reports previously conflicted with the ten-split manuscript. The ten-split configuration and results now occupy the standard config/study.json and results/ paths used by the training CLI. All three-split artifacts are archived.
- Word exports predated later Markdown edits. The current Word files are rebuilt from the retained Markdown, tables and figures. A build manifest records their input/output hashes.
- The old prepare_text.py contained a second hardcoded manuscript and could overwrite subsequent edits. It is archived. The manuscript now owns its bibliography; redundant references.json is archived too.
- The later readiness report claimed a five-agent swarm and “100%” scientific and statistical verification without supporting evidence here. It also described Brier improvements as significant without a reported significance analysis. The report is archived as unsupported, and replaced by specific verification results and explicit limits.
- The initial cleaned CSV and blank-charge workbook were competing data artifacts. They are archived; the raw CSV is authoritative and cleaning occurs in the tested pipeline.
- Older figure/table copies, notebook outputs, audit extraction text, old ZIP, outdated reports and document render images were removed from the active layout. Historical files are preserved in a verified ZIP; disposable render images and caches are regenerated only when needed.
- Publication scripts now live in src/. Derived summaries live in publication/tables/. References to the new paths were updated across active instructions and tools.
- The original submission remains separately preserved under archive/original_submission/, with hash verification. The existing audit/.venv environment remains usable and is excluded from deliverables.

## Remaining intentional limits

Author identity, affiliations, funding, conflicts, ethics requirements, prior-publication status and repository deposit are not supplied. They remain clearly marked, not invented. Campaign economics are assumed. There is one public benchmark, overlapping repeated splits and conditional uncertainty; no independent operational or causal validation was added. Journal acceptance is not established.

See publication/VERIFICATION.json for the checks actually performed. Historical statements within archive files and the original audit are not current completion claims.
