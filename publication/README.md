# Current publication materials

The nine-page Word manuscript and cover letter are author-review drafts based on the ten-split study in ../results/. They contain deliberate author/declaration placeholders. Nothing has been submitted or accepted.

## Read or edit

- `Manuscript.docx`: current editable Word export, with measured tables and figures.
- `Manuscript.md`: authoritative narrative and bibliography source. Table/figure markers are expanded by ../src/build_documents.py.
- `Cover_Letter.docx`: current covering letter; its source text is in the same builder.
- `AUTHOR_COMPLETION.md`: real author information and declarations still required.
- `LITERATURE_REVIEW.md`: focused review and bounded contribution.
- `EXTENSION_PROTOCOL.md`: retrospective extension from three to ten splits.
- `tables/` and `figures/`: current generated summaries and standalone graphics.
- `Reproducibility_Supplement.zip`: generated code/results package. See SUPPLEMENT_README.md for exclusions and commands.
- `document_build.json`: source/output hashes to detect stale Word exports.
- `VERIFICATION.json`: specific completed checks and limitations; not a publication certification.

## Proposed venue

SN Computer Science is the proposed target for this applied machine-learning evaluation. Its subscription route has no APC according to the official publishing page checked on 18 October 2026. Open access is optional and charged. This is a proposal, not a selected option in a submitted application; verify current terms and any funder requirements before submission. Single-dataset scope and limited methodological novelty remain acceptance risks.

- Publishing routes: https://link.springer.com/journal/42979/how-to-publish-with-us
- Scope: https://link.springer.com/journal/42979/aims-and-scope
- Author instructions: https://link.springer.com/journal/42979/submission-guidelines

The draft has a 203-word structured abstract, six keywords, numbered references and declarations. Replace administrative placeholders with verified information, obtain author agreement, review the scientific content and finalize any code deposit before uploading.

## Rebuild

From the project root, run src/analyze_publication.py to generate tables/figures, then src/build_documents.py with python-docx to build Word exports. Render and inspect the changed documents. Run src/package_supplement.py after validation. Do not edit generated table values manually. The old hardcoded narrative generator has been archived so it cannot overwrite current prose.
