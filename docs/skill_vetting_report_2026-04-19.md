# Skill Vetting Report (2026-04-19)

## WILLOSCAR/research-units-pipeline-skills

- Stars: 410
- Last updated: 2026-04-18T13:48:56Z
- Files reviewed locally: 945
- Potential pattern hits: 261
- Risk level: 🟡 MEDIUM
- Verdict: ⚠️ INSTALL WITH CAUTION
- Notes: Repository contains many local .codex skills and workflow tooling. No obvious credential scraping or destructive shell patterns were found in the inspected thesis-related skills. One helper skill (`global-reviewer`) includes a local Python script, but it performs file-based review generation rather than exfiltration.
- Representative matches:
  - `README.md` -> `https://`
  - `README.zh-CN.md` -> `https://`
  - `tooling/tutorial_workflows.py` -> `token`
  - `tooling/review_text.py` -> `token`
  - `tooling/common.py` -> `token`
  - `tooling/quality_gate.py` -> `token`
  - `tooling/quality_gate.py` -> `subprocess`
  - `tooling/review_workflows.py` -> `token`
- Installed locally into `~/.codex/skills`: `thesis-style-polisher`, `thesis-compile-review`, `thesis-tex-writeback`, `global-reviewer`.
- These newly installed skills require a future session restart to appear in the active skill list.

## InternScience/Awesome-Scientific-Skills

- Stars: 307
- Last updated: 2026-04-18T06:52:03Z
- Files reviewed locally: 12
- Potential pattern hits: 10
- Risk level: 🟢 LOW
- Verdict: ✅ SAFE TO CLONE / INDEX ONLY
- Notes: Repository is primarily an awesome-list and evaluation index, not an executable skill pack. It is useful as a discovery directory but not as a directly installable Codex skill.
- Representative matches:
  - `fig.jpg` -> `http://`
  - `.gitmodules` -> `https://`
  - `readme.md` -> `https://`
  - `readme_CN.md` -> `https://`
  - `skills-metric/README.md` -> `https://`
  - `skills-metric/results_all_skills.csv` -> `token`
  - `skills-metric/results_all_skills.csv` -> `api-key`
  - `skills-metric/assets/repo_comparison.png` -> `https://`
