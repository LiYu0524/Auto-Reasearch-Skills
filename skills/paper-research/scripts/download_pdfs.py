#!/usr/bin/env python3
import argparse
import os
import socket
import time
import urllib.error
import urllib.request
from typing import Dict, Iterable, List, Optional, Set

from _jsonl import read_jsonl


def _safe_filename(arxiv_id: str) -> str:
    return arxiv_id.replace("/", "_")


def _download(url: str, out_path: str, timeout_s: int, retries: int) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "paper-research/0.1 (mailto:local)"})
    last_err: Optional[BaseException] = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp, open(out_path, "wb") as f:
                f.write(resp.read())
            return
        except (socket.timeout, urllib.error.URLError) as e:
            last_err = e
            if attempt >= retries:
                break
            time.sleep(1.0 * (2**attempt))
    raise RuntimeError(f"download failed: {last_err}")


def iter_items(jsonl_path: str) -> Iterable[Dict]:
    for it in read_jsonl(jsonl_path):
        yield it


def main() -> None:
    ap = argparse.ArgumentParser(description="Download PDFs for entries in an arXiv JSONL.")
    ap.add_argument("--jsonl", required=True, help="Input JSONL from arxiv_survey.py (or filtered subset).")
    ap.add_argument("--pdf-dir", required=True, help="Output directory for PDFs.")
    ap.add_argument("--limit", type=int, default=0, help="If >0, download only first N items.")
    ap.add_argument("--only-ids", nargs="*", help="Optional allowlist of arXiv IDs to download.")
    ap.add_argument("--timeout", type=int, default=90, help="HTTP timeout seconds (default: 90).")
    ap.add_argument("--retries", type=int, default=2, help="Retries per PDF (default: 2).")
    ap.add_argument("--sleep", type=float, default=0.5, help="Seconds to sleep between downloads (default: 0.5).")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing PDFs.")
    args = ap.parse_args()

    allow: Optional[Set[str]] = set(args.only_ids) if args.only_ids else None

    os.makedirs(args.pdf_dir, exist_ok=True)
    n_ok = 0
    n_skip = 0
    n_err = 0
    n_seen = 0

    for it in iter_items(args.jsonl):
        arxiv_id = str(it.get("arxiv_id") or "")
        if not arxiv_id:
            continue
        if allow is not None and arxiv_id not in allow:
            continue

        n_seen += 1
        if args.limit and n_seen > args.limit:
            break

        url = it.get("pdf_url") or f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        out_path = os.path.join(args.pdf_dir, _safe_filename(arxiv_id) + ".pdf")
        if not args.overwrite and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            n_skip += 1
            continue
        try:
            _download(url, out_path, timeout_s=args.timeout, retries=args.retries)
            n_ok += 1
            time.sleep(max(0.0, float(args.sleep)))
        except Exception as e:
            n_err += 1
            err_path = out_path + ".error.txt"
            with open(err_path, "w", encoding="utf-8") as f:
                f.write(f"{arxiv_id}\n{url}\n{e}\n")

    print(f"Downloaded {n_ok}, skipped {n_skip}, errors {n_err} into {args.pdf_dir}")


if __name__ == "__main__":
    main()

