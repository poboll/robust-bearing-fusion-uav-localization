# Submission Closeout Checklist

## Completed in This Package

- Manuscript title, abstract, figures, tables, and validation narrative are synchronized to the current `robust front-end` story.
- The MDPI manuscript builds successfully from `submission/mdpi_manuscript/manuscript_mdpi.tex` and currently produces a 36-page PDF.
- The measured-data replay, deadline-aware replay, pseudo-physical replay, and PyBullet replay layers are all referenced in the manuscript and archived in the supplementary package.
- Frozen JSON artifacts now include `public_dataset3_replay_*` and `deadline_replay_*` result bundles, along with the updated manifest.
- The cover letter, submission README, audit note, highlights, and data-availability text now describe the same validation chain and paper title.

## Final Manual Items Before Portal Upload

- Confirm the exact target journal and replace `[Target Journal]` in the cover letter.
- Insert the final author affiliations, emails, and contribution metadata in the MDPI front matter and portal fields.
- Decide whether the current public repository is acceptable for the venue or whether an anonymized archive is required.
- Do one last visual proofread of the compiled PDF for float placement, caption wording, and author metadata before upload.

## Core Files

- Manuscript PDF: `submission/mdpi_manuscript/manuscript_mdpi.pdf`
- Cover letter: `submission/cover_letter/cover_letter_final.md`
- Audit note: `submission/pre_submission_audit.md`
- Supplementary ZIP: `submission/supplementary/reproducibility_package.zip`
- Frozen manifest: `submission/supplementary/frozen_results/manifest.json`
