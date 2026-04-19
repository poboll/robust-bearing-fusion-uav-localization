# Submission Package Readme

## Recommended Final Package Structure

```text
submission/
  mdpi_manuscript/
    manuscript_mdpi.tex
    manuscript_mdpi.pdf
    references_curated.bib
  figures/
    figure_regime_comparison.png
    figure_ablation_mixed.png
    figure_formation_generalization.png
    figure_runtime_comparison.png
  tables/
    tables_final.md
  cover_letter/
    cover_letter_final.md
  supplementary/
    experiment_notes.md
    data_availability.md
```

## Current Source Materials

### Canonical Manuscript Source
- `submission/mdpi_manuscript/manuscript_mdpi.tex`
- `submission/mdpi_manuscript/references_curated.bib`

### Journal Positioning
- `docs/journal_scope_notes.md`
- `docs/frontier_and_submission_strategy.md`

### Tables and Captions
- `submission/tables/tables_final.tex`
- `docs/figure_captions_v1.md`

### Experimental Assets
- `experiments/regime_comparison.json`
- `experiments/ablation_summary.json`
- `experiments/formation_result.json`
- `experiments/runtime_result.json`
- `experiments/figure_*.png`

## Best Immediate Packaging Sequence

1. choose target journal
2. finalize author block and affiliations
3. update the canonical MDPI manuscript directly
4. regenerate figures and tables if numbers change
5. add cover letter
6. freeze experiment outputs
