#!/usr/bin/env python3
import argparse
import json
import os
import re
from typing import Dict, Iterable, List, Optional, Tuple


def _iter_pdfs(pdf_dir: str) -> Iterable[str]:
    for name in sorted(os.listdir(pdf_dir)):
        if name.lower().endswith(".pdf"):
            yield os.path.join(pdf_dir, name)


def _load_extractor():
    try:
        import pypdf  # type: ignore

        def extract(path: str) -> str:
            reader = pypdf.PdfReader(path)
            chunks = []
            for page in reader.pages:
                chunks.append(page.extract_text() or "")
            return "\n".join(chunks)

        return extract
    except Exception:
        pass

    try:
        import PyPDF2  # type: ignore

        def extract(path: str) -> str:
            reader = PyPDF2.PdfReader(path)
            chunks = []
            for page in reader.pages:
                chunks.append(page.extract_text() or "")
            return "\n".join(chunks)

        return extract
    except Exception:
        pass

    return None


HEADING_RE = re.compile(r"^\s*((\d+(\.\d+)*)\s+)?([A-Z][A-Z0-9 ,:/\\-]{5,})\s*$")


def split_sections(text: str) -> List[Dict]:
    lines = [ln.rstrip() for ln in text.splitlines()]
    headings: List[Tuple[int, str]] = []
    for i, ln in enumerate(lines):
        if len(ln) < 6 or len(ln) > 120:
            continue
        m = HEADING_RE.match(ln)
        if not m:
            continue
        title = (m.group(0) or "").strip()
        if title:
            headings.append((i, title))

    if not headings:
        return []

    sections: List[Dict] = []
    for idx, (line_i, title) in enumerate(headings):
        start = line_i
        end = (headings[idx + 1][0] - 1) if idx + 1 < len(headings) else (len(lines) - 1)
        if end <= start:
            continue
        sections.append({"heading": title, "line_start": start, "line_end": end})
    return sections


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract text from PDFs to .txt (optional: rough section splits).")
    ap.add_argument("--pdf-dir", required=True, help="Directory containing PDFs.")
    ap.add_argument("--out-dir", required=True, help="Output directory for extracted text.")
    ap.add_argument("--sections", action="store_true", help="Also write a .sections.json file per PDF.")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing outputs.")
    args = ap.parse_args()

    extractor = _load_extractor()
    if extractor is None:
        raise SystemExit(
            "No PDF text extractor found. Install one of:\n"
            "  - pip install pypdf\n"
            "  - pip install PyPDF2\n"
        )

    os.makedirs(args.out_dir, exist_ok=True)

    n_ok = 0
    n_err = 0
    for pdf_path in _iter_pdfs(args.pdf_dir):
        base = os.path.splitext(os.path.basename(pdf_path))[0]
        txt_path = os.path.join(args.out_dir, base + ".txt")
        sec_path = os.path.join(args.out_dir, base + ".sections.json")
        if not args.overwrite and os.path.exists(txt_path) and os.path.getsize(txt_path) > 0:
            continue
        try:
            text = extractor(pdf_path)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)

            if args.sections:
                secs = split_sections(text)
                with open(sec_path, "w", encoding="utf-8") as f:
                    json.dump({"pdf": pdf_path, "sections": secs}, f, ensure_ascii=False, indent=2)
            n_ok += 1
        except Exception as e:
            n_err += 1
            err_path = os.path.join(args.out_dir, base + ".error.txt")
            with open(err_path, "w", encoding="utf-8") as f:
                f.write(str(e) + "\n")

    print(f"Extracted {n_ok} PDFs to {args.out_dir} ({n_err} errors)")


if __name__ == "__main__":
    main()

