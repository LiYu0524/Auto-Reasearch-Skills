#!/usr/bin/env python3
import argparse
import json
import os
import re
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple


ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def _text(el: Optional[ET.Element]) -> Optional[str]:
    if el is None or el.text is None:
        return None
    return el.text.strip()


def _normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _arxiv_id_from_abs_url(abs_url: str) -> str:
    # Examples:
    # - http(s)://arxiv.org/abs/2401.01234v2
    # - http(s)://arxiv.org/abs/hep-th/9901001v1
    m = re.search(r"/abs/([^?#]+)", abs_url)
    if not m:
        return abs_url.rstrip("/").split("/")[-1]
    return m.group(1)


def _safe_filename(arxiv_id: str) -> str:
    return arxiv_id.replace("/", "_")


def build_or_query(terms: List[str]) -> str:
    parts = []
    for t in terms:
        t = t.strip()
        if not t:
            continue
        parts.append(f'all:"{t}"')
    if not parts:
        raise SystemExit("No non-empty terms provided.")
    if len(parts) == 1:
        return parts[0]
    return " OR ".join(parts)


def fetch_atom(search_query: str, start: int, max_results: int, timeout_s: int = 60, retries: int = 3) -> bytes:
    params = {
        "search_query": search_query,
        "start": str(start),
        "max_results": str(max_results),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "paper-research/0.1 (mailto:local)"})
    last_err: Optional[BaseException] = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                return resp.read()
        except (socket.timeout, urllib.error.URLError) as e:  # type: ignore[attr-defined]
            last_err = e
            if attempt >= retries:
                break

            # arXiv may rate-limit (HTTP 429). Prefer a longer backoff in that case.
            backoff_s = 1.0 * (2**attempt)
            if isinstance(e, urllib.error.HTTPError) and getattr(e, "code", None) == 429:
                retry_after = None
                try:
                    retry_after = e.headers.get("Retry-After")
                except Exception:
                    retry_after = None
                if retry_after:
                    try:
                        backoff_s = max(backoff_s, float(retry_after))
                    except Exception:
                        backoff_s = max(backoff_s, 15.0 * (2**attempt))
                else:
                    backoff_s = max(backoff_s, 15.0 * (2**attempt))
            time.sleep(backoff_s)
    raise RuntimeError(f"Failed to fetch arXiv feed after {retries + 1} attempts: {last_err}")


def parse_feed(xml_bytes: bytes) -> Tuple[List[Dict], int]:
    root = ET.fromstring(xml_bytes)
    total = _text(root.find("atom:totalResults", ATOM_NS))
    total_i = int(total) if total and total.isdigit() else -1

    items: List[Dict] = []
    for entry in root.findall("atom:entry", ATOM_NS):
        abs_url = _text(entry.find("atom:id", ATOM_NS)) or ""
        arxiv_id = _arxiv_id_from_abs_url(abs_url)

        title = _normalize_whitespace(_text(entry.find("atom:title", ATOM_NS)) or "")
        summary = _normalize_whitespace(_text(entry.find("atom:summary", ATOM_NS)) or "")
        published = _text(entry.find("atom:published", ATOM_NS))
        updated = _text(entry.find("atom:updated", ATOM_NS))

        authors = []
        for a in entry.findall("atom:author", ATOM_NS):
            name = _text(a.find("atom:name", ATOM_NS))
            if name:
                authors.append(name)

        categories = [c.attrib.get("term", "") for c in entry.findall("atom:category", ATOM_NS)]
        categories = [c for c in categories if c]
        primary_category = None
        pc = entry.find("arxiv:primary_category", ATOM_NS)
        if pc is not None:
            primary_category = pc.attrib.get("term")

        pdf_url = None
        for link in entry.findall("atom:link", ATOM_NS):
            href = link.attrib.get("href")
            title_attr = (link.attrib.get("title") or "").lower()
            rel = (link.attrib.get("rel") or "").lower()
            if href and ("pdf" in title_attr or href.endswith(".pdf") or (rel == "related" and "/pdf/" in href)):
                pdf_url = href
                break
        if not pdf_url and arxiv_id:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        doi = _text(entry.find("arxiv:doi", ATOM_NS))
        journal_ref = _text(entry.find("arxiv:journal_ref", ATOM_NS))
        comment = _text(entry.find("arxiv:comment", ATOM_NS))

        items.append(
            {
                "arxiv_id": arxiv_id,
                "title": title,
                "summary": summary,
                "authors": authors,
                "published": published,
                "updated": updated,
                "categories": categories,
                "primary_category": primary_category,
                "abs_url": abs_url,
                "pdf_url": pdf_url,
                "doi": doi,
                "journal_ref": journal_ref,
                "comment": comment,
            }
        )
    return items, total_i


def maybe_download_pdf(item: Dict, pdf_dir: str, timeout_s: int = 60) -> Optional[str]:
    url = item.get("pdf_url")
    arxiv_id = item.get("arxiv_id")
    if not url or not arxiv_id:
        return None
    os.makedirs(pdf_dir, exist_ok=True)
    out_path = os.path.join(pdf_dir, _safe_filename(arxiv_id) + ".pdf")
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        return out_path
    req = urllib.request.Request(url, headers={"User-Agent": "paper-research/0.1 (mailto:local)"})
    with urllib.request.urlopen(req, timeout=timeout_s) as resp, open(out_path, "wb") as f:
        f.write(resp.read())
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description="Search arXiv via Atom API and write results to JSONL.")
    q = ap.add_mutually_exclusive_group(required=True)
    q.add_argument("--query", help='Raw arXiv query string, e.g. \'cat:cs.CL AND all:"multilingual"\'.')
    q.add_argument("--terms", nargs="+", help="Convenience terms; turned into all:\"term\" OR ...")

    ap.add_argument("--max-results", type=int, default=100, help="Total number of results to fetch (default: 100).")
    ap.add_argument("--batch-size", type=int, default=100, help="Batch size per request (default: 100).")
    ap.add_argument("--sleep", type=float, default=3.0, help="Seconds to sleep between requests (default: 3).")
    ap.add_argument("--timeout", type=int, default=60, help="HTTP timeout seconds (default: 60).")
    ap.add_argument("--retries", type=int, default=3, help="Fetch retries per batch (default: 3).")
    ap.add_argument("--out", required=True, help="Output JSONL path.")

    ap.add_argument("--download-pdfs", action="store_true", help="Download PDFs for each entry.")
    ap.add_argument("--pdf-dir", default="./pdfs", help="Directory for downloaded PDFs (default: ./pdfs).")
    args = ap.parse_args()

    search_query = args.query if args.query else build_or_query(args.terms)

    max_results = max(0, int(args.max_results))
    batch_size = max(1, min(2000, int(args.batch_size)))
    start = 0

    seen = set()
    written = 0
    with open(args.out, "w", encoding="utf-8") as out_f:
        while start < max_results:
            take = min(batch_size, max_results - start)
            try:
                xml_bytes = fetch_atom(
                    search_query,
                    start=start,
                    max_results=take,
                    timeout_s=args.timeout,
                    retries=args.retries,
                )
            except Exception as e:
                print(f"ERROR: fetch failed at start={start}: {e}")
                break
            items, _total = parse_feed(xml_bytes)
            if not items:
                break
            for item in items:
                arxiv_id = item.get("arxiv_id")
                if not arxiv_id or arxiv_id in seen:
                    continue
                seen.add(arxiv_id)

                if args.download_pdfs:
                    try:
                        item["downloaded_pdf"] = maybe_download_pdf(item, args.pdf_dir, timeout_s=max(60, args.timeout))
                    except Exception as e:
                        item["downloaded_pdf_error"] = str(e)

                out_f.write(json.dumps(item, ensure_ascii=False) + "\n")
                written += 1

            start += take
            if start < max_results:
                time.sleep(max(0.0, float(args.sleep)))

    print(f"Wrote {written} entries to {args.out}")


if __name__ == "__main__":
    main()
