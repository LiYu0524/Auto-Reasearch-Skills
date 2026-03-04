#!/usr/bin/env python3
import argparse
import json
import re
from difflib import SequenceMatcher
from typing import Dict, List, Tuple

from _jsonl import read_jsonl


def norm_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r"[^a-z0-9]+", " ", title)
    return re.sub(r"\s+", " ", title).strip()


def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def main() -> None:
    ap = argparse.ArgumentParser(description="Dedupe a JSONL (arXiv) file by arxiv_id and near-duplicate titles.")
    ap.add_argument("--in", dest="in_path", required=True, help="Input JSONL.")
    ap.add_argument("--out", required=True, help="Output JSONL.")
    ap.add_argument("--title-threshold", type=float, default=0.97, help="Similarity ratio for title dedupe.")
    args = ap.parse_args()

    seen_ids = set()
    seen_titles: List[Tuple[str, str]] = []  # (norm_title, arxiv_id)

    kept: List[Dict] = []
    dropped = 0
    for item in read_jsonl(args.in_path):
        arxiv_id = str(item.get("arxiv_id") or "")
        if arxiv_id and arxiv_id in seen_ids:
            dropped += 1
            continue
        title = norm_title(str(item.get("title") or ""))
        if title:
            dup = None
            for t2, id2 in seen_titles:
                if similar(title, t2) >= args.title_threshold:
                    dup = id2
                    break
            if dup is not None:
                item["dedupe_note"] = f"near-duplicate title of {dup}"
                dropped += 1
                continue
            seen_titles.append((title, arxiv_id))
        if arxiv_id:
            seen_ids.add(arxiv_id)
        kept.append(item)

    with open(args.out, "w", encoding="utf-8") as f:
        for item in kept:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Kept {len(kept)}; dropped {dropped}; wrote {args.out}")


if __name__ == "__main__":
    main()

