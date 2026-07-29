from __future__ import annotations

from collections import Counter
from typing import Any

from tools._shared import domain, terms


def _clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def _source_name(item: dict[str, Any], index: int) -> str:
    return _clean(item.get("source")) or domain(_clean(item.get("url"))) or f"source_{index + 1}"


def compare_sources(
    items: list[dict[str, Any]] | None = None,
    focus: str = "",
    max_sources: int = 5,
) -> dict[str, Any]:
    source_items = [item for item in (items or []) if isinstance(item, dict)]
    try:
        limit = max(2, min(int(max_sources or 5), 10))
    except (TypeError, ValueError):
        limit = 5
    source_items = source_items[:limit]

    if len(source_items) < 2:
        return {
            "tool": "compare_sources",
            "source_count": len(source_items),
            "sources": [],
            "common_terms": [],
            "comparisons": [],
            "limitations": ["At least two source items are required."],
        }

    source_terms: list[set[str]] = []
    sources: list[dict[str, Any]] = []
    for index, item in enumerate(source_items):
        title = _clean(item.get("title"))
        summary = _clean(item.get("summary"))
        text_terms = terms(" ".join([title, summary, _clean(focus)]))
        source_terms.append(text_terms)
        url = _clean(item.get("url"))
        sources.append({
            "index": index + 1,
            "name": _source_name(item, index),
            "title": title or None,
            "url": url or None,
            "date": _clean(item.get("date")) or None,
            "term_count": len(text_terms),
            "has_summary": bool(summary),
        })

    term_counts = Counter(term for item_terms in source_terms for term in item_terms)
    common_terms = [
        term for term, count in sorted(term_counts.items(), key=lambda pair: (-pair[1], pair[0]))
        if count >= 2
    ][:20]

    comparisons: list[dict[str, Any]] = []
    for index, source in enumerate(sources):
        others = set().union(*(source_terms[j] for j in range(len(source_terms)) if j != index))
        comparisons.append({
            "source": source["name"],
            "shared_terms": sorted(source_terms[index] & set(common_terms))[:20],
            "unique_terms": sorted(source_terms[index] - others)[:20],
            "coverage": "has_summary" if source["has_summary"] else "metadata_only",
        })

    limitations: list[str] = [
        "Term overlap is lexical and does not establish factual agreement."
    ]
    if any(not source["has_summary"] for source in sources):
        limitations.append("One or more sources have no summary; comparison coverage is incomplete.")
    if any(not source["url"] for source in sources):
        limitations.append("One or more sources have no URL; citations require manual review.")

    return {
        "tool": "compare_sources",
        "focus": _clean(focus),
        "source_count": len(sources),
        "sources": sources,
        "common_terms": common_terms,
        "comparisons": comparisons,
        "limitations": limitations,
    }
