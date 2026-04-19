#!/usr/bin/env python3
"""Build a traceable literature pool for the passive-localization SCI package.

This script combines:
1. OpenAlex title-search results for precise, DOI-backed journal/conference papers.
2. The existing literature-pdf-ocr-library raw query results already generated in
   `.pipeline/literature/passive-localization-2026-sci/raw_queries/`.

Outputs:
- `.pipeline/literature/passive-localization-2026-sci/library_index.json`
- `.pipeline/literature/passive-localization-2026-sci/library_index.jsonl`
- `.pipeline/literature/passive-localization-2026-sci/papers/*/metadata.json`
- `docs/literature_pool_master.md`
"""

from __future__ import annotations

import json
import math
import re
import subprocess
import urllib.parse
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DOCS_ROOT = PROJECT_ROOT / "docs"
CORPUS_ROOT = PROJECT_ROOT / ".pipeline" / "literature" / "passive-localization-2026-sci"
RAW_QUERY_ROOT = CORPUS_ROOT / "raw_queries"
PAPERS_ROOT = CORPUS_ROOT / "papers"

OPENALEX_BASE = "https://api.openalex.org/works"
MIN_YEAR = 2018
TARGET_COUNT = 80


QUERY_SPECS = [
    {
        "slug": "survey_uav_localization",
        "phrase": "uav localization survey",
        "theme": "survey_and_scope",
        "limit": 10,
        "must_groups": [["survey", "review"], ["uav", "unmanned aerial vehicle", "drone"], ["localization", "positioning", "navigation"]],
        "purpose": "Provides the macro context on UAV localization technology, application pressure, and system-level positioning constraints.",
    },
    {
        "slug": "bearing_only_localization",
        "phrase": "bearing-only localization",
        "theme": "bearing_only_core",
        "limit": 14,
        "must_groups": [["bearing", "aoa", "angle of arrival", "direction of arrival"], ["localization", "positioning", "target", "motion analysis"]],
        "purpose": "Anchors the core bearing-only localization problem formulation and mainstream estimator families.",
    },
    {
        "slug": "bearing_only_target",
        "phrase": "bearing-only target localization",
        "theme": "bearing_only_core",
        "limit": 12,
        "must_groups": [["bearing", "aoa", "angle of arrival"], ["target", "localization", "circumnavigation", "motion analysis"]],
        "purpose": "Adds target-centric bearing-only localization papers, including motion analysis and circumnavigation settings.",
    },
    {
        "slug": "passive_uav_localization",
        "phrase": "passive localization uav",
        "theme": "passive_uav_systems",
        "limit": 12,
        "must_groups": [["passive"], ["uav", "swarm", "formation", "drone"], ["localization", "positioning", "adjustment", "geolocation"]],
        "purpose": "Captures passive or electromagnetically silent UAV formation localization papers closest to the current paper's application story.",
    },
    {
        "slug": "passive_target_localization",
        "phrase": "passive target localization",
        "theme": "passive_uav_systems",
        "limit": 12,
        "must_groups": [["passive"], ["target"], ["localization", "positioning", "geolocation"]],
        "purpose": "Adds passive target-localization papers that are not always UAV-specific but still support the sensing story and metric choices.",
    },
    {
        "slug": "aoa_uav_localization",
        "phrase": "angle of arrival localization uav",
        "theme": "passive_uav_systems",
        "limit": 12,
        "must_groups": [["angle of arrival", "aoa", "doa", "azimuth"], ["uav", "swarm", "formation", "drone"], ["localization", "positioning", "estimation"]],
        "purpose": "Tracks the AOA/DOA UAV branch that overlaps strongly with passive bearing-only formation localization.",
    },
    {
        "slug": "cooperative_uav_localization",
        "phrase": "cooperative localization uav",
        "theme": "cooperative_and_distributed",
        "limit": 12,
        "must_groups": [["cooperative", "collaborative", "distributed", "relative localization", "multi-uav"], ["localization", "navigation", "positioning"], ["uav", "swarm", "drone"]],
        "purpose": "Places the work inside the broader cooperative multi-UAV localization literature.",
    },
    {
        "slug": "relative_uav_localization",
        "phrase": "relative localization uav",
        "theme": "cooperative_and_distributed",
        "limit": 12,
        "must_groups": [["relative localization", "cooperative", "distributed", "collaborative"], ["uav", "swarm", "drone"], ["localization", "navigation", "positioning"]],
        "purpose": "Extends the cooperative branch toward relative-localization and GNSS-denied swarm positioning papers.",
    },
    {
        "slug": "factor_graph_uav_localization",
        "phrase": "factor graph localization uav",
        "theme": "factor_graph_and_graph_optimization",
        "limit": 10,
        "must_groups": [["factor graph", "graph optimization", "graph-based"], ["uav", "drone", "navigation", "localization"]],
        "purpose": "Covers the graph/factor-graph line that represents the stronger systems baseline family we should discuss but not overclaim against.",
    },
    {
        "slug": "robust_bearing_localization",
        "phrase": "bearing-only localization outlier",
        "theme": "robustness_and_bias",
        "limit": 12,
        "must_groups": [["bearing", "aoa", "angle of arrival"], ["outlier", "robust", "bias", "noise", "uncertain"], ["localization", "estimation", "target"]],
        "purpose": "Supports the robust-estimation angle and helps judge whether our current method is actually novel or just a lightweight variant.",
    },
    {
        "slug": "sensor_bias_bearing_localization",
        "phrase": "sensor bias bearing-only localization",
        "theme": "robustness_and_bias",
        "limit": 10,
        "must_groups": [["bearing", "aoa", "angle of arrival"], ["bias", "calibration", "uncertain"], ["localization", "target", "estimation"]],
        "purpose": "Complements the robustness branch with papers centered on bias calibration and sensor inconsistency.",
    },
    {
        "slug": "observability_bearing_localization",
        "phrase": "bearing-only localization observability",
        "theme": "geometry_and_observability",
        "limit": 10,
        "must_groups": [["bearing", "aoa", "angle of arrival"], ["observability", "geometry", "geometric", "sensor bias", "information"], ["localization", "target"]],
        "purpose": "Connects geometry quality, observability, and bias-estimation arguments to the interpretation section.",
    },
    {
        "slug": "trajectory_bearing_localization",
        "phrase": "bearing-only localization trajectory optimization",
        "theme": "active_sensing_and_path_planning",
        "limit": 12,
        "must_groups": [["bearing", "aoa", "angle of arrival"], ["trajectory", "path planning", "active sensing", "circumnavigation"], ["localization", "target"]],
        "purpose": "Tracks the newer active-sensing/path-planning branch that can make the paper more computer-oriented if we upgrade the method.",
    },
    {
        "slug": "bearing_target_motion_analysis",
        "phrase": "bearing-only target motion analysis",
        "theme": "active_sensing_and_path_planning",
        "limit": 10,
        "must_groups": [["bearing", "aoa", "angle of arrival"], ["target motion analysis", "motion analysis", "circumnavigation", "moving-target"], ["localization", "estimation", "target"]],
        "purpose": "Adds the target-motion-analysis line, which often overlaps with recursive estimation, maneuver design, and observability-aware sensing.",
    },
]

SKILL_QUERY_THEME_MAP = {
    "q1_bearing_only": "bearing_only_core",
    "q2_aoa_swarm": "passive_uav_systems",
    "q3_cooperative_factor_graph": "cooperative_and_distributed",
    "q4_robust_outlier": "robustness_and_bias",
    "q5_observability": "geometry_and_observability",
}

SKILL_QUERY_MUST_GROUPS = {
    "q1_bearing_only": [["bearing", "aoa", "angle of arrival", "direction of arrival"], ["localization", "positioning", "target", "circumnavigation", "motion"]],
    "q2_aoa_swarm": [["aoa", "doa", "angle of arrival", "azimuth", "passive"], ["uav", "swarm", "formation", "drone"], ["localization", "positioning", "target"]],
    "q3_cooperative_factor_graph": [["cooperative", "distributed", "factor graph", "graph"], ["uav", "swarm", "drone", "localization", "navigation"]],
    "q4_robust_outlier": [["bearing", "aoa", "angle of arrival", "localization"], ["robust", "outlier", "bias", "noise", "uncertainty"]],
    "q5_observability": [["bearing", "aoa", "angle of arrival", "localization"], ["observability", "geometry", "geometric", "sensor bias", "information"]],
}

THEME_TITLES = {
    "survey_and_scope": "Survey and Scope",
    "bearing_only_core": "Bearing-Only Core",
    "passive_uav_systems": "Passive UAV Systems",
    "cooperative_and_distributed": "Cooperative and Distributed Localization",
    "factor_graph_and_graph_optimization": "Factor Graph and Graph Optimization",
    "robustness_and_bias": "Robustness, Bias, and Corruption Handling",
    "geometry_and_observability": "Geometry and Observability",
    "active_sensing_and_path_planning": "Active Sensing and Path Planning",
}

THEME_SHORT_ROLE = {
    "survey_and_scope": "宏观背景和选题合理性",
    "bearing_only_core": "问题定义、经典模型和近年核心方法",
    "passive_uav_systems": "最贴近本文应用故事的无人机无源定位分支",
    "cooperative_and_distributed": "多机协同定位与系统化扩展路线",
    "factor_graph_and_graph_optimization": "更强系统基线和后续升级方向",
    "robustness_and_bias": "鲁棒估计、偏差和异常值处理证据",
    "geometry_and_observability": "几何解释、可观测性和误差趋势解释",
    "active_sensing_and_path_planning": "更偏计算机/智能决策的升级故事",
}

ALLOWED_TYPES = {"article", "preprint", "proceedings-article", "journal-article"}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def slugify(text: str, limit: int = 96) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text[:limit] or "paper"


def normalize_title(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def clean_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    doi = doi.strip()
    doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
    doi = doi.replace("https://dx.doi.org/", "").replace("http://dx.doi.org/", "")
    return doi or None


def doi_url(doi: str | None) -> str | None:
    return f"https://doi.org/{doi}" if doi else None


def curl_json(url: str) -> dict:
    result = subprocess.run(
        ["curl", "-sS", "--max-time", "45", url],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def title_matches(title: str, must_groups: list[list[str]]) -> bool:
    lowered = normalize_title(title)
    if not lowered:
        return False
    for group in must_groups:
        if not any(token in lowered for token in group):
            return False
    return True


def openalex_search(spec: dict) -> tuple[list[dict], dict]:
    params = {
        "filter": f"title.search:{spec['phrase']},from_publication_date:{MIN_YEAR}-01-01",
        "per-page": spec["limit"],
        "sort": "publication_date:desc",
    }
    url = f"{OPENALEX_BASE}?{urllib.parse.urlencode(params)}"
    body = curl_json(url)
    records: list[dict] = []

    for item in body.get("results", []):
        title = item.get("display_name") or item.get("title")
        if not title_matches(title or "", spec["must_groups"]):
            continue

        work_type = item.get("type")
        type_crossref = item.get("type_crossref")
        if work_type not in ALLOWED_TYPES and type_crossref not in ALLOWED_TYPES:
            continue

        year = item.get("publication_year")
        if year and year < MIN_YEAR:
            continue

        primary_location = item.get("primary_location") or {}
        source = primary_location.get("source") or {}
        authors = []
        for authorship in item.get("authorships", []):
            name = (authorship.get("author") or {}).get("display_name")
            if name:
                authors.append(name)

        doi = clean_doi(item.get("doi") or (item.get("ids") or {}).get("doi"))
        landing_page = primary_location.get("landing_page_url") or doi_url(doi) or item.get("id")
        pdf_url = primary_location.get("pdf_url") or (item.get("open_access") or {}).get("oa_url")

        records.append(
            {
                "title": title,
                "authors": authors,
                "year": year,
                "venue": source.get("display_name"),
                "doi": doi,
                "url": landing_page,
                "pdf_url": pdf_url,
                "source": "openalex",
                "source_detail": "openalex_title_search",
                "theme": spec["theme"],
                "query_slug": spec["slug"],
                "selection_reason": spec["purpose"],
                "citation_count": item.get("cited_by_count") or 0,
                "is_open_access": (item.get("open_access") or {}).get("is_oa"),
            }
        )

    return records, body


def load_skill_query_records() -> list[dict]:
    records: list[dict] = []
    for path in sorted(RAW_QUERY_ROOT.glob("*/search_results.json")):
        query_slug = path.parent.name
        theme = SKILL_QUERY_THEME_MAP.get(query_slug)
        if not theme:
            continue

        payload = json.loads(path.read_text(encoding="utf-8"))
        for row in payload.get("records", []):
            title = row.get("title")
            if not title:
                continue
            must_groups = SKILL_QUERY_MUST_GROUPS.get(query_slug, [])
            if must_groups and not title_matches(title, must_groups):
                continue

            record = {
                "title": title,
                "authors": row.get("authors", []),
                "year": row.get("year"),
                "venue": row.get("venue"),
                "doi": clean_doi(row.get("doi")),
                "url": row.get("landing_page"),
                "pdf_url": row.get("pdf_url"),
                "source": "skill_raw_query",
                "source_detail": query_slug,
                "theme": theme,
                "query_slug": query_slug,
                "selection_reason": f"Supplemented from literature-pdf-ocr-library raw query `{query_slug}` to capture newer preprints and open-access frontier items.",
                "citation_count": 0,
                "is_open_access": row.get("pdf_url") is not None,
                "arxiv_id": row.get("arxiv_id"),
            }
            records.append(record)
    return records


def merge_records(records: list[dict]) -> list[dict]:
    merged: dict[str, dict] = {}

    for record in records:
        doi_key = record.get("doi")
        title_key = normalize_title(record.get("title"))
        existing_key = None
        for candidate in (doi_key, title_key):
            if candidate and candidate in merged:
                existing_key = candidate
                break

        key = existing_key or doi_key or title_key
        if not key:
            continue

        if existing_key is None:
            merged[key] = {
                **record,
                "themes": [record["theme"]],
                "query_slugs": [record["query_slug"]],
                "sources": [record["source"]],
                "selection_reasons": [record["selection_reason"]],
            }
            continue

        existing = merged[key]
        for field in ("title", "venue", "year", "doi", "url", "pdf_url", "arxiv_id"):
            if not existing.get(field) and record.get(field):
                existing[field] = record[field]

        if len(existing.get("authors", [])) < len(record.get("authors", [])):
            existing["authors"] = record["authors"]

        existing["citation_count"] = max(existing.get("citation_count", 0), record.get("citation_count", 0))
        existing["is_open_access"] = existing.get("is_open_access") or record.get("is_open_access")

        for field, value in (
            ("themes", record["theme"]),
            ("query_slugs", record["query_slug"]),
            ("sources", record["source"]),
            ("selection_reasons", record["selection_reason"]),
        ):
            if value not in existing[field]:
                existing[field].append(value)

    rows = list(merged.values())
    deduped: dict[str, dict] = {}
    for row in rows:
        title_key = normalize_title(row.get("title"))
        key = title_key or row.get("doi")
        if not key:
            continue
        existing = deduped.get(key)
        if existing is None:
            deduped[key] = row
            continue

        if row.get("doi") and not existing.get("doi"):
            existing["doi"] = row["doi"]
        if row.get("url") and not existing.get("url"):
            existing["url"] = row["url"]
        if row.get("pdf_url") and not existing.get("pdf_url"):
            existing["pdf_url"] = row["pdf_url"]
        existing["citation_count"] = max(existing.get("citation_count", 0), row.get("citation_count", 0))
        for field in ("themes", "query_slugs", "sources", "selection_reasons"):
            for value in row.get(field, []):
                if value not in existing[field]:
                    existing[field].append(value)
        if len(existing.get("authors", [])) < len(row.get("authors", [])):
            existing["authors"] = row["authors"]

    for row in deduped.values():
        row["themes"] = sorted(row["themes"])
        row["query_slugs"] = sorted(row["query_slugs"])
        row["sources"] = sorted(row["sources"])
        row["selection_reasons"] = sorted(row["selection_reasons"])
    return list(deduped.values())


def score_record(record: dict) -> float:
    year = record.get("year") or MIN_YEAR
    citations = record.get("citation_count") or 0
    year_score = max(0, year - 2017) * 2.8
    citation_score = math.log1p(citations) * 3.2
    theme_score = len(record.get("themes", [])) * 2.5
    doi_score = 2.0 if record.get("doi") else 0.0
    oa_score = 0.8 if record.get("is_open_access") else 0.0
    return round(year_score + citation_score + theme_score + doi_score + oa_score, 3)


def select_records(records: list[dict], target_count: int) -> list[dict]:
    by_theme: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        record["priority_score"] = score_record(record)
        for theme in record.get("themes", []):
            by_theme[theme].append(record)

    for theme_records in by_theme.values():
        theme_records.sort(key=lambda row: (row["priority_score"], row.get("citation_count", 0), row.get("year") or 0), reverse=True)

    selected: list[dict] = []
    seen_titles: set[str] = set()

    def maybe_take(record: dict) -> None:
        key = record.get("doi") or normalize_title(record.get("title"))
        if key in seen_titles:
            return
        seen_titles.add(key)
        selected.append(record)

    for theme in THEME_TITLES:
        for record in by_theme.get(theme, [])[:8]:
            maybe_take(record)

    leftovers = sorted(
        records,
        key=lambda row: (row["priority_score"], row.get("citation_count", 0), row.get("year") or 0),
        reverse=True,
    )
    for record in leftovers:
        if len(selected) >= target_count:
            break
        maybe_take(record)

    selected.sort(key=lambda row: (row.get("year") or 0, row["priority_score"]), reverse=True)
    return selected[:target_count]


def write_json(path: Path, data: object) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def persist_corpus(raw_openalex: dict[str, dict], selected_records: list[dict]) -> None:
    ensure_dir(CORPUS_ROOT / "raw_openalex")
    ensure_dir(PAPERS_ROOT)

    for slug, payload in raw_openalex.items():
        write_json(CORPUS_ROOT / "raw_openalex" / f"{slug}.json", payload)

    for record in selected_records:
        paper_slug = slugify(f"{record.get('year', 'na')}-{record['title']}")
        paper_dir = PAPERS_ROOT / paper_slug
        ensure_dir(paper_dir)
        metadata = {
            **record,
            "paper_slug": paper_slug,
            "landing_page": record.get("url"),
            "pdf_status": "metadata_only",
            "local_pdf_path": None,
            "markdown_paths": [],
            "image_paths": [],
        }
        write_json(paper_dir / "metadata.json", metadata)

    library_rows = []
    for record in selected_records:
        paper_slug = slugify(f"{record.get('year', 'na')}-{record['title']}")
        metadata_path = PAPERS_ROOT / paper_slug / "metadata.json"
        library_rows.append(
            {
                "paper_slug": paper_slug,
                "title": record.get("title"),
                "authors": record.get("authors", []),
                "year": record.get("year"),
                "venue": record.get("venue"),
                "source": record.get("source"),
                "merged_sources": record.get("sources", []),
                "doi": record.get("doi"),
                "landing_page": record.get("url"),
                "pdf_url": record.get("pdf_url"),
                "local_pdf_path": None,
                "markdown_paths": [],
                "image_paths": [],
                "pdf_status": "metadata_only",
                "metadata_path": str(metadata_path),
                "themes": record.get("themes", []),
                "priority_score": record.get("priority_score"),
                "citation_count": record.get("citation_count", 0),
            }
        )

    write_json(CORPUS_ROOT / "library_index.json", {"papers": library_rows})
    write_jsonl(CORPUS_ROOT / "library_index.jsonl", library_rows)
    write_json(
        CORPUS_ROOT / "build_manifest.json",
        {
            "selected_count": len(selected_records),
            "min_year": MIN_YEAR,
            "queries": QUERY_SPECS,
            "themes": THEME_TITLES,
        },
    )


def write_markdown(selected_records: list[dict]) -> None:
    by_theme: dict[str, list[dict]] = defaultdict(list)
    for record in selected_records:
        for theme in record.get("themes", []):
            by_theme[theme].append(record)

    shortlist = sorted(selected_records, key=lambda row: (row["priority_score"], row.get("citation_count", 0), row.get("year") or 0), reverse=True)[:18]

    lines = [
        "# Passive Localization Literature Pool",
        "",
        "## Overview",
        "",
        f"- Total selected papers: `{len(selected_records)}`",
        f"- Coverage window: `{MIN_YEAR}-2026`",
        "- Sources: `OpenAlex title-search` + `literature-pdf-ocr-library raw queries`",
        "- Selection rule: relevance to passive / bearing-only / cooperative UAV localization, story support value, DOI traceability, and recency.",
        "",
        "## Cite-First Shortlist",
        "",
    ]

    for idx, record in enumerate(shortlist, start=1):
        url = record.get("url") or doi_url(record.get("doi")) or ""
        doi = record.get("doi") or "N/A"
        venue = record.get("venue") or "Unknown venue"
        lines.append(
            f"{idx}. {record['title']} ({record.get('year')}, {venue}). DOI: {doi}. URL: {url}. Use for: {' / '.join(THEME_TITLES[theme] for theme in record.get('themes', [])[:2])}."
        )

    for theme, heading in THEME_TITLES.items():
        theme_records = sorted(
            by_theme.get(theme, []),
            key=lambda row: (row["priority_score"], row.get("citation_count", 0), row.get("year") or 0),
            reverse=True,
        )
        lines.extend(
            [
                "",
                f"## {heading}",
                "",
                f"- Role in our paper: {THEME_SHORT_ROLE[theme]}",
                "",
            ]
        )
        for record in theme_records:
            doi = record.get("doi") or "N/A"
            url = record.get("url") or doi_url(record.get("doi")) or ""
            venue = record.get("venue") or "Unknown venue"
            citations = record.get("citation_count", 0)
            lines.append(
                f"- {record['title']} ({record.get('year')}, {venue}; citations={citations}; DOI={doi}). URL: {url}. Why relevant: {record['selection_reasons'][0]}"
            )

    DOCS_ROOT.mkdir(parents=True, exist_ok=True)
    (DOCS_ROOT / "literature_pool_master.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ensure_dir(CORPUS_ROOT)
    raw_openalex: dict[str, dict] = {}
    all_records: list[dict] = []

    for spec in QUERY_SPECS:
        records, raw_payload = openalex_search(spec)
        raw_openalex[spec["slug"]] = raw_payload
        all_records.extend(records)

    all_records.extend(load_skill_query_records())
    merged_records = merge_records(all_records)
    selected_records = select_records(merged_records, TARGET_COUNT)
    persist_corpus(raw_openalex, selected_records)
    write_markdown(selected_records)

    print(
        json.dumps(
            {
                "selected_count": len(selected_records),
                "corpus_root": str(CORPUS_ROOT),
                "markdown": str(DOCS_ROOT / "literature_pool_master.md"),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
