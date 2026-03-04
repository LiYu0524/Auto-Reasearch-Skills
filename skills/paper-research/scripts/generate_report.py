#!/usr/bin/env python3
import argparse
import datetime as dt
from collections import defaultdict
from typing import Dict, List, Tuple

from _jsonl import read_jsonl


def _fmt_date(s: str) -> str:
    if not s:
        return ""
    try:
        # Atom timestamps are usually RFC3339 like 2024-01-01T00:00:00Z
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return dt.datetime.fromisoformat(s).date().isoformat()
    except Exception:
        return s


def _md_escape(s: str) -> str:
    return (s or "").replace("\n", " ").replace("|", "\\|").strip()


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate a Markdown report from arXiv JSONL.")
    ap.add_argument("--jsonl", required=True, help="Input JSONL produced by arxiv_survey.py.")
    ap.add_argument("--out", required=True, help="Output Markdown path.")
    ap.add_argument("--max-rows", type=int, default=200, help="Max rows in the main table (default: 200).")
    args = ap.parse_args()

    items: List[Dict] = []
    seen = set()
    for item in read_jsonl(args.jsonl):
        arxiv_id = item.get("arxiv_id")
        if not arxiv_id or arxiv_id in seen:
            continue
        seen.add(arxiv_id)
        items.append(item)

    # Sort by published desc when available.
    def sort_key(it: Dict) -> Tuple[str, str]:
        return (it.get("published") or "", it.get("arxiv_id") or "")

    items.sort(key=sort_key, reverse=True)

    by_cat = defaultdict(list)
    for it in items:
        cat = it.get("primary_category") or (it.get("categories") or ["uncategorized"])[0]
        by_cat[str(cat)].append(it)

    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines: List[str] = []
    lines.append(f"# arXiv Survey Report\n")
    lines.append(f"- Generated: {now}\n")
    lines.append(f"- Entries: {len(items)}\n")
    lines.append("\n")

    lines.append("## Table (scan list)\n")
    lines.append("| Paper | Date | Categories | Links |\n")
    lines.append("|---|---:|---|---|\n")
    for it in items[: max(0, int(args.max_rows))]:
        title = _md_escape(it.get("title") or "")
        arxiv_id = it.get("arxiv_id") or ""
        date = _fmt_date(it.get("published") or "")
        cats = _md_escape(", ".join(it.get("categories") or []))
        abs_url = it.get("abs_url") or ""
        pdf_url = it.get("pdf_url") or ""
        links = []
        if abs_url:
            links.append(f"[abs]({abs_url})")
        if pdf_url:
            links.append(f"[pdf]({pdf_url})")
        link_s = " ".join(links) if links else ""
        lines.append(f"| **{title}** (`{arxiv_id}`) | {date} | {cats} | {link_s} |\n")

    lines.append("\n")
    lines.append("## Clusters (by primary category)\n")
    for cat in sorted(by_cat.keys()):
        lines.append(f"\n### {cat} ({len(by_cat[cat])})\n")
        for it in by_cat[cat][:30]:
            title = _md_escape(it.get("title") or "")
            arxiv_id = it.get("arxiv_id") or ""
            lines.append(f"- {title} (`{arxiv_id}`)\n")
        if len(by_cat[cat]) > 30:
            lines.append(f"- … and {len(by_cat[cat]) - 30} more\n")

    lines.append("\n")
    lines.append("## Notes TODOs\n")
    lines.append("- [ ] Which papers have reusable code (eval harness / probing / training recipe)?\n")
    lines.append("- [ ] Which benchmarks best test the core hypothesis?\n")
    lines.append("- [ ] What are the strongest alternative explanations / confounds?\n")
    lines.append("\n")

    with open(args.out, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"Wrote report with {len(items)} entries to {args.out}")


if __name__ == "__main__":
    main()

