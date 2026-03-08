#!/usr/bin/env python3
"""
Dump a paper PDF into review-friendly artifacts:
- Per-page text extraction (pypdf)
- Optional page rendering to PNG (PyMuPDF / fitz)
- Simple heuristics for section headings and figure/table captions
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DumpResult:
    page_count: int
    out_dir: Path
    rendered_pages: int


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_slug(text: str) -> str:
    slug = text.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    return slug or "paper"


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _coerce_metadata(metadata: Any) -> dict[str, Any]:
    if metadata is None:
        return {}
    if isinstance(metadata, dict):
        return {str(k): (str(v) if v is not None else None) for k, v in metadata.items()}
    try:
        # pypdf's DocumentInformation is dict-like
        items = dict(metadata.items())
        return {str(k): (str(v) if v is not None else None) for k, v in items.items()}
    except Exception:
        return {"raw": str(metadata)}


def _extract_text_by_page(pdf_path: Path, max_pages: int | None) -> tuple[list[str], dict[str, Any]]:
    try:
        from pypdf import PdfReader
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Missing dependency: pypdf. Install via `python3 -m pip install pypdf`.") from exc

    reader = PdfReader(str(pdf_path))
    page_count = len(reader.pages)
    limit = page_count if max_pages is None else min(page_count, max_pages)

    texts: list[str] = []
    for index in range(limit):
        page = reader.pages[index]
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        texts.append(text)

    return texts, _coerce_metadata(getattr(reader, "metadata", None))


def _render_pages(
    pdf_path: Path,
    render_dir: Path,
    dpi: int,
    max_pages: int | None,
) -> int:
    try:
        import fitz  # PyMuPDF
    except Exception as exc:
        raise RuntimeError(
            "Missing dependency: PyMuPDF (fitz). Install via `python3 -m pip install pymupdf`."
        ) from exc

    _ensure_dir(render_dir)
    doc = fitz.open(str(pdf_path))
    page_count = doc.page_count
    limit = page_count if max_pages is None else min(page_count, max_pages)

    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    rendered = 0
    for index in range(limit):
        page = doc.load_page(index)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        out_path = render_dir / f"page_{index + 1:03d}.png"
        pix.save(str(out_path))
        rendered += 1

    return rendered


def _guess_headings(text_by_page: list[str]) -> list[str]:
    headings: list[str] = []
    seen: set[str] = set()

    numbered = re.compile(r"^\s*(\d+(\.\d+)*)\s+([A-Za-z].+)$")
    keywords = {"abstract", "introduction", "related work", "method", "experiments", "conclusion", "references"}

    for page_index, text in enumerate(text_by_page):
        for raw_line in (text or "").splitlines():
            line = " ".join(raw_line.strip().split())
            if not line:
                continue

            m = numbered.match(line)
            if m:
                normalized = f"{m.group(1)} {m.group(3)}"
                key = normalized.lower()
                if key not in seen:
                    headings.append(f"p{page_index + 1}: {normalized}")
                    seen.add(key)
                continue

            lower = line.lower()
            if lower in keywords and lower not in seen:
                headings.append(f"p{page_index + 1}: {line}")
                seen.add(lower)

    return headings


def _guess_captions(text_by_page: list[str]) -> list[str]:
    captions: list[str] = []
    seen: set[str] = set()

    caption_re = re.compile(r"^\s*(figure|fig\.|table)\s*\d+[:.\s-]+(.+)$", re.IGNORECASE)
    for page_index, text in enumerate(text_by_page):
        for raw_line in (text or "").splitlines():
            line = " ".join(raw_line.strip().split())
            if not line:
                continue
            m = caption_re.match(line)
            if not m:
                continue

            kind = m.group(1).lower().replace("fig.", "fig")
            rest = m.group(2).strip()
            normalized = f"{kind} {rest}".lower()
            if normalized in seen:
                continue
            captions.append(f"p{page_index + 1}: {line}")
            seen.add(normalized)

    return captions


def dump_paper_pdf(
    pdf_path: Path,
    out_dir: Path,
    render: bool,
    dpi: int,
    max_pages: int | None,
    max_render_pages: int | None,
) -> DumpResult:
    _ensure_dir(out_dir)

    text_by_page, metadata = _extract_text_by_page(pdf_path, max_pages=max_pages)
    page_count = len(text_by_page)

    rendered_pages = 0
    if render:
        render_dir = out_dir / "render"
        rendered_pages = _render_pages(
            pdf_path,
            render_dir=render_dir,
            dpi=dpi,
            max_pages=max_render_pages,
        )

    headings = _guess_headings(text_by_page)
    captions = _guess_captions(text_by_page)

    (out_dir / "text_by_page.txt").write_text(
        "\n\n".join(
            f"===== Page {i + 1} =====\n\n{(text or '').strip()}"
            for i, text in enumerate(text_by_page)
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "headings_guess.txt").write_text("\n".join(headings).strip() + "\n", encoding="utf-8")
    (out_dir / "captions_guess.txt").write_text("\n".join(captions).strip() + "\n", encoding="utf-8")

    meta_out = {
        "pdf_path": str(pdf_path),
        "extracted_at_utc": _utc_now_iso(),
        "page_count": page_count,
        "pypdf_metadata": metadata,
        "rendered_pages": rendered_pages,
        "dpi": dpi if render else None,
    }
    (out_dir / "metadata.json").write_text(json.dumps(meta_out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return DumpResult(page_count=page_count, out_dir=out_dir, rendered_pages=rendered_pages)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract text and (optionally) render pages from a paper PDF.")
    parser.add_argument("--pdf", required=True, help="Path to the input PDF")
    parser.add_argument(
        "--out-dir",
        default="",
        help="Output directory (default: ./tmp/paper-review/<pdf-basename-slug>)",
    )
    parser.add_argument("--render", action="store_true", help="Render pages to PNG using PyMuPDF (fitz)")
    parser.add_argument("--dpi", type=int, default=150, help="DPI for rendering (default: 150)")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=0,
        help="Max pages to extract text from (default: 0 = all)",
    )
    parser.add_argument(
        "--max-render-pages",
        type=int,
        default=0,
        help="Max pages to render if --render is set (default: 0 = all)",
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        print(f"[ERROR] PDF not found: {pdf_path}", file=sys.stderr)
        return 2
    if pdf_path.suffix.lower() != ".pdf":
        print(f"[ERROR] Not a PDF: {pdf_path}", file=sys.stderr)
        return 2

    base_slug = _safe_slug(pdf_path.stem)
    if args.out_dir.strip():
        out_dir = Path(args.out_dir).expanduser().resolve()
    else:
        out_dir = (Path.cwd() / "tmp" / "paper-review" / base_slug).resolve()

    max_pages = None if int(args.max_pages) <= 0 else int(args.max_pages)
    max_render_pages = None if int(args.max_render_pages) <= 0 else int(args.max_render_pages)

    try:
        result = dump_paper_pdf(
            pdf_path=pdf_path,
            out_dir=out_dir,
            render=bool(args.render),
            dpi=int(args.dpi),
            max_pages=max_pages,
            max_render_pages=max_render_pages,
        )
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    print("[OK] Extracted paper PDF")
    print(f"  PDF: {pdf_path}")
    print(f"  Pages: {result.page_count}")
    print(f"  Out: {result.out_dir}")
    if args.render:
        print(f"  Rendered pages: {result.rendered_pages}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

