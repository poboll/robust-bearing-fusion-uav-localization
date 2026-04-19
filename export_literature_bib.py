#!/usr/bin/env python3
"""Export the curated literature pool into a minimal BibTeX file."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
POOL_PATH = PROJECT_ROOT / ".pipeline" / "literature" / "passive-localization-2026-sci" / "library_index.json"
OUT_PATH = PROJECT_ROOT / "submission" / "manuscript" / "references_curated.bib"


def clean(text: str) -> str:
    text = text.replace("{", "").replace("}", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def ascii_slug(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^A-Za-z0-9]+", "", normalized)
    return normalized or "anon"


def latex_escape(text: str) -> str:
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "_": r"\_",
        "#": r"\#",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def bib_key(record: dict) -> str:
    authors = record.get("authors", [])
    first_author = ascii_slug(authors[0].split()[-1].lower()) if authors else "anon"
    year = str(record.get("year") or "na")
    title = clean(record.get("title") or "")
    tokens = re.findall(r"[A-Za-z0-9]+", title.lower())
    token = next((tok for tok in tokens if tok not in {"a", "an", "the", "of", "for", "and", "with", "using"}), "paper")
    return ascii_slug(f"{first_author}{year}{token}")


def entry_type(record: dict) -> str:
    venue = (record.get("venue") or "").lower()
    doi = record.get("doi") or ""
    if "arxiv" in venue or "techrxiv" in doi or "hal-" in (record.get("url") or "").lower():
        return "misc"
    return "article"


def format_authors(authors: list[str]) -> str:
    return " and ".join(clean(author) for author in authors if author.strip())


def build_entry(record: dict) -> str:
    kind = entry_type(record)
    key = bib_key(record)
    title = latex_escape(clean(record.get("title") or "Untitled"))
    authors = format_authors(record.get("authors", [])) or "Unknown"
    year = str(record.get("year") or "")
    venue = latex_escape(clean(record.get("venue") or "Unknown venue"))
    doi = record.get("doi")
    url = record.get("landing_page") or record.get("url")

    lines = [f"@{kind}{{{key},"]
    lines.append(f"  author = {{{authors}}},")
    lines.append(f"  title = {{{title}}},")
    if kind == "article":
        lines.append(f"  journal = {{{venue}}},")
    else:
        lines.append(f"  howpublished = {{{venue}}},")
    if year:
        lines.append(f"  year = {{{year}}},")
    if doi:
        lines.append(f"  doi = {{{doi}}},")
    if url:
        lines.append(f"  url = {{{url}}},")
    lines.append("}")
    return "\n".join(lines)


def main() -> int:
    payload = json.loads(POOL_PATH.read_text(encoding="utf-8"))
    records = payload["papers"]
    seen_keys: set[str] = set()
    entries: list[str] = []
    for record in records:
        key = bib_key(record)
        suffix = 1
        while key in seen_keys:
            suffix += 1
            key = f"{bib_key(record)}{suffix}"
        seen_keys.add(key)

        entry = build_entry(record)
        if entry.startswith("@"):
            entry = re.sub(r"@\w+\{[^,]+,", lambda m: m.group(0).split("{", 1)[0] + "{" + key + ",", entry, count=1)
        entries.append(entry)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n\n".join(entries) + "\n", encoding="utf-8")
    print(f"wrote {len(entries)} entries to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
