#!/usr/bin/env python3
"""
Save papers to Zotero via the Web API.

Usage:
    python zotero_save.py --arxiv 2301.12345 --collection "[ACM MM2026]Ego"
    python zotero_save.py --doi 10.1234/example --collection "Survey"
    python zotero_save.py --url https://arxiv.org/abs/2301.12345
    python zotero_save.py --from-jsonl ./arxiv.jsonl --collection "Survey"
    python zotero_save.py --list-collections
    python zotero_save.py --setup

Environment variables required:
    ZOTERO_API_KEY     - Your Zotero API key (get from https://www.zotero.org/settings/keys)
    ZOTERO_LIBRARY_ID  - Your Zotero user library ID (visible on the same page)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from typing import Optional, List

ZOTERO_API_BASE = "https://api.zotero.org"
ZOTERO_API_KEY = os.environ.get("ZOTERO_API_KEY", "")
ZOTERO_LIBRARY_ID = os.environ.get("ZOTERO_LIBRARY_ID", "")


def check_credentials():
    """Check that API credentials are configured. Exit with help message if not."""
    if ZOTERO_API_KEY and ZOTERO_LIBRARY_ID:
        return
    missing = []
    if not ZOTERO_API_KEY:
        missing.append("ZOTERO_API_KEY")
    if not ZOTERO_LIBRARY_ID:
        missing.append("ZOTERO_LIBRARY_ID")
    print("Error: Missing required environment variables:", ", ".join(missing), file=sys.stderr)
    print(file=sys.stderr)
    print("To configure, run:  python zotero_save.py --setup", file=sys.stderr)
    print("Or set them directly:", file=sys.stderr)
    print('  export ZOTERO_API_KEY="your-api-key"', file=sys.stderr)
    print('  export ZOTERO_LIBRARY_ID="your-library-id"', file=sys.stderr)
    sys.exit(1)


def setup_guide():
    """Print setup instructions for Zotero API credentials."""
    print("""
=== Zotero API Setup Guide ===

1. Go to https://www.zotero.org/settings/keys
2. Click "Create new private key"
3. Give it a name (e.g., "claude-zotero")
4. Grant permissions:
   - Allow library access (read/write)
   - Allow write access
5. Save the key

Your Library ID is shown on the same page (a numeric ID).

Then set environment variables:

  # Add to your ~/.zshrc or ~/.bashrc:
  export ZOTERO_API_KEY="your-api-key-here"
  export ZOTERO_LIBRARY_ID="your-library-id-here"

  # Or for Claude Code, add to ~/.claude/settings.json under env:
  # "env": { "ZOTERO_API_KEY": "...", "ZOTERO_LIBRARY_ID": "..." }

After setting, verify with:
  python zotero_save.py --list-collections
""")


def web_api_request(method: str, path: str, data=None, version: Optional[int] = None):
    """Call Zotero Web API. Returns parsed JSON or HTTP status code for no-content responses."""
    url = f"{ZOTERO_API_BASE}/users/{ZOTERO_LIBRARY_ID}{path}"
    headers = {
        "Zotero-API-Key": ZOTERO_API_KEY,
        "Content-Type": "application/json",
    }
    if version is not None:
        headers["If-Unmodified-Since-Version"] = str(version)

    payload = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {"_status": resp.status}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        print(f"API error {e.code}: {body}", file=sys.stderr)
        return None


# ── Metadata fetchers ────────────────────────────────────────────────────

def fetch_arxiv_metadata(arxiv_id: str) -> dict:
    """Fetch paper metadata from arXiv API."""
    arxiv_id = arxiv_id.strip()
    arxiv_id = re.sub(r'^(https?://)?arxiv\.org/(abs|pdf)/', '', arxiv_id)
    arxiv_id = arxiv_id.rstrip('.pdf').rstrip('/')
    base_id = re.sub(r'v\d+$', '', arxiv_id)

    url = f"http://export.arxiv.org/api/query?id_list={base_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "zotero-save/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        xml_data = resp.read().decode("utf-8")

    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(xml_data)
    entry = root.find("atom:entry", ns)
    if entry is None:
        raise ValueError(f"No entry found for arXiv ID: {arxiv_id}")

    title = re.sub(r'\s+', ' ', entry.findtext("atom:title", "", ns).strip())
    abstract = entry.findtext("atom:summary", "", ns).strip()
    published = entry.findtext("atom:published", "", ns)[:10]

    authors = []
    for author in entry.findall("atom:author", ns):
        name = author.findtext("atom:name", "", ns).strip()
        if name:
            parts = name.rsplit(" ", 1)
            if len(parts) == 2:
                authors.append({"firstName": parts[0], "lastName": parts[1], "creatorType": "author"})
            else:
                authors.append({"firstName": "", "lastName": name, "creatorType": "author"})

    categories = [cat.get("term", "") for cat in entry.findall("atom:category", ns) if cat.get("term")]
    doi_el = entry.find("arxiv:doi", ns)
    doi = doi_el.text.strip() if doi_el is not None and doi_el.text else ""

    return {
        "itemType": "preprint",
        "title": title,
        "creators": authors,
        "abstractNote": abstract,
        "date": published,
        "url": f"https://arxiv.org/abs/{base_id}",
        "DOI": doi,
        "repository": "arXiv",
        "archiveID": f"arXiv:{base_id}",
        "tags": [{"tag": c} for c in categories],
    }


def fetch_doi_metadata(doi: str) -> dict:
    """Fetch paper metadata from CrossRef API."""
    doi = doi.strip()
    url = f"https://api.crossref.org/works/{doi}"
    req = urllib.request.Request(url, headers={"User-Agent": "zotero-save/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    item = data["message"]
    title = item.get("title", [""])[0]
    authors = [
        {"firstName": a.get("given", ""), "lastName": a.get("family", ""), "creatorType": "author"}
        for a in item.get("author", [])
    ]
    date_parts = item.get("published-print", item.get("published-online", {})).get("date-parts", [[]])
    date = "-".join(str(p) for p in date_parts[0]) if date_parts[0] else ""

    return {
        "itemType": "journalArticle",
        "title": title,
        "creators": authors,
        "abstractNote": item.get("abstract", ""),
        "date": date,
        "DOI": doi,
        "publicationTitle": item.get("container-title", [""])[0],
        "url": item.get("URL", f"https://doi.org/{doi}"),
        "tags": [],
    }


# ── Collection helpers ───────────────────────────────────────────────────

def get_collections() -> list:
    """Get all collections."""
    result = web_api_request("GET", "/collections?limit=100")
    return result if isinstance(result, list) else []


def find_collection_key(name: str) -> Optional[str]:
    """Find collection key by name (case-insensitive)."""
    for c in get_collections():
        if c["data"]["name"].lower() == name.lower():
            return c["key"]
    return None


def list_collections_cmd():
    """Print all collections."""
    collections = get_collections()
    if not collections:
        print("No collections found.")
        return

    parent_map = {c["key"]: c["data"].get("parentCollection", False) for c in collections}

    def get_level(key):
        level, current = 0, key
        while parent_map.get(current):
            level += 1
            current = parent_map[current]
        return level

    sorted_cols = sorted(collections, key=lambda c: (get_level(c["key"]), c["data"]["name"].lower()))
    print(f"{'Name':<50} {'Key':<12} {'Items'}")
    print("-" * 70)
    for c in sorted_cols:
        indent = "  " * get_level(c["key"])
        name = f"{indent}{c['data']['name']}"
        print(f"{name:<50} {c['key']:<12} {c['meta'].get('numItems', 0)}")


# ── Save logic ───────────────────────────────────────────────────────────

def save_item(metadata: dict, collection_name: Optional[str] = None, extra_tags: Optional[List[str]] = None) -> bool:
    """Save a paper to Zotero via Web API."""

    # Add extra tags
    if extra_tags:
        existing = {t["tag"] for t in metadata.get("tags", [])}
        for t in extra_tags:
            if t not in existing:
                metadata.setdefault("tags", []).append({"tag": t})

    # Resolve collection
    if collection_name:
        col_key = find_collection_key(collection_name)
        if not col_key:
            print(f"Error: collection '{collection_name}' not found.", file=sys.stderr)
            list_collections_cmd()
            return False
        metadata["collections"] = [col_key]

    # Create via Web API POST
    resp = web_api_request("POST", "/items", [metadata])
    if not resp:
        return False

    if resp.get("successful"):
        item = list(resp["successful"].values())[0]
        print(f"Saved: {metadata['title']}")
        print(f"  Key: {item['key']}")
        if collection_name:
            print(f"  Collection: {collection_name}")
        return True

    if resp.get("failed"):
        for k, v in resp["failed"].items():
            print(f"Failed: {v.get('message', v)}", file=sys.stderr)
    return False


def save_from_jsonl(jsonl_path: str, collection_name: Optional[str] = None, extra_tags: Optional[List[str]] = None):
    """Batch save from JSONL (arxiv_survey.py output)."""
    saved = failed = skipped = 0
    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            arxiv_id = entry.get("arxiv_id", "")
            if not arxiv_id:
                skipped += 1
                continue
            try:
                metadata = fetch_arxiv_metadata(arxiv_id)
                if save_item(metadata, collection_name, extra_tags):
                    saved += 1
                else:
                    failed += 1
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Error saving {arxiv_id}: {e}", file=sys.stderr)
                failed += 1

    print(f"\nBatch: {saved} saved, {skipped} skipped, {failed} failed")


def main():
    parser = argparse.ArgumentParser(description="Save papers to Zotero via Web API")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--arxiv", help="arXiv ID")
    source.add_argument("--doi", help="DOI")
    source.add_argument("--url", help="Paper URL (auto-detect arXiv/DOI)")
    source.add_argument("--from-jsonl", help="JSONL file from arxiv_survey.py")
    parser.add_argument("--title", help="Manual title")
    parser.add_argument("--authors", help="Authors (semicolon-separated)")
    parser.add_argument("--year", help="Publication year")
    parser.add_argument("--collection", help="Target collection name")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--list-collections", action="store_true")
    parser.add_argument("--setup", action="store_true", help="Show setup instructions")

    args = parser.parse_args()

    if args.setup:
        setup_guide()
        return

    # Check credentials for all operations except --setup
    check_credentials()

    extra_tags = [t.strip() for t in args.tags.split(",")] if args.tags else None

    if args.list_collections:
        list_collections_cmd()
        return

    if args.from_jsonl:
        save_from_jsonl(args.from_jsonl, args.collection, extra_tags)
        return

    metadata = None
    if args.arxiv:
        metadata = fetch_arxiv_metadata(args.arxiv)
    elif args.doi:
        metadata = fetch_doi_metadata(args.doi)
    elif args.url:
        url = args.url
        arxiv_match = re.search(r'arxiv\.org/(abs|pdf)/(\d{4}\.\d{4,5})', url)
        doi_match = re.search(r'doi\.org/(10\.\d{4,}/.+)', url)
        if arxiv_match:
            metadata = fetch_arxiv_metadata(arxiv_match.group(2))
        elif doi_match:
            metadata = fetch_doi_metadata(doi_match.group(1))
        else:
            print(f"Cannot detect paper type from URL: {url}", file=sys.stderr)
            sys.exit(1)
    elif args.title:
        creators = []
        if args.authors:
            for a in args.authors.split(";"):
                a = a.strip()
                parts = a.rsplit(" ", 1)
                creators.append(
                    {"firstName": parts[0], "lastName": parts[1], "creatorType": "author"} if len(parts) == 2
                    else {"firstName": "", "lastName": a, "creatorType": "author"}
                )
        metadata = {
            "itemType": "journalArticle", "title": args.title, "creators": creators,
            "date": args.year or "", "url": args.url or "", "tags": [],
        }
    else:
        parser.print_help()
        sys.exit(1)

    if metadata:
        save_item(metadata, args.collection, extra_tags)


if __name__ == "__main__":
    main()
