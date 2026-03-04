#!/usr/bin/env python3
import argparse
import html
import re
import urllib.request
from typing import Iterable, List, Optional

from _jsonl import read_jsonl


def _extract_pre(html_text: str) -> Optional[str]:
    m = re.search(r"<pre[^>]*>(.*?)</pre>", html_text, flags=re.DOTALL | re.IGNORECASE)
    if not m:
        return None
    return html.unescape(m.group(1)).strip()


def fetch_bibtex(arxiv_id: str, timeout_s: int = 30) -> str:
    url = f"https://arxiv.org/bibtex/{arxiv_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "paper-research/0.1 (mailto:local)"})
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        page = resp.read().decode("utf-8", errors="replace")
    bib = _extract_pre(page)
    if not bib:
        raise RuntimeError(f"Could not find BibTeX in response for {arxiv_id}")
    return bib


def iter_ids(args) -> Iterable[str]:
    if args.ids:
        for x in args.ids:
            x = x.strip()
            if x:
                yield x
        return
    for item in read_jsonl(args.from_jsonl):
        arxiv_id = item.get("arxiv_id")
        if arxiv_id:
            yield str(arxiv_id)


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch BibTeX from arxiv.org for arXiv IDs.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--ids", nargs="+", help="List of arXiv IDs.")
    src.add_argument("--from-jsonl", help="JSONL file produced by arxiv_survey.py.")

    ap.add_argument("--timeout", type=int, default=30, help="HTTP timeout seconds (default: 30).")
    ap.add_argument("--out", required=True, help="Output .bib path.")
    args = ap.parse_args()

    ids: List[str] = []
    seen = set()
    for arxiv_id in iter_ids(args):
        if arxiv_id in seen:
            continue
        seen.add(arxiv_id)
        ids.append(arxiv_id)

    out_chunks = []
    for arxiv_id in ids:
        try:
            out_chunks.append(fetch_bibtex(arxiv_id, timeout_s=args.timeout))
        except Exception as e:
            out_chunks.append(f"% ERROR: {arxiv_id}: {e}")

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n\n".join(out_chunks).rstrip() + "\n")
    print(f"Wrote BibTeX for {len(ids)} ids to {args.out}")


if __name__ == "__main__":
    main()

