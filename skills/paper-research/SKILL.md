---
name: paper-research
description: End-to-end paper research support for arXiv/literature surveys, reproducibility-focused paper shortlisting, and experiment design. Use when you need to (1) search arXiv with complex queries, (2) download PDFs, extract text/sections, and fetch BibTeX, (3) dedupe/cluster results into a structured report, and (4) turn findings into a lit-review plan, benchmark/evaluation suite, and representation/probing experiment checklist (e.g., implicit reasoning, hidden-CoT, multilingual reasoning, cross-lingual alignment).
---

# Paper Research

## Overview

Run a fast, reproducible “survey → shortlist → synthesize” loop for research topics, backed by small scripts that fetch arXiv metadata/PDFs/BibTeX, extract text, and generate structured Markdown briefs.

## Quick start (recommended workflow)

1. Create a topic workspace directory (keep everything together):
   - Example: `notes/implicit-reasoning-survey/`
2. Search arXiv and (optionally) download PDFs:
   - Run: `python3 scripts/arxiv_survey.py --terms "implicit reasoning" "hidden chain-of-thought" "multilingual reasoning" --max-results 100 --download-pdfs --pdf-dir ./pdfs --out ./arxiv.jsonl`
3. Extract text (+ rough sections) from PDFs:
   - Run: `python3 scripts/pdf_extract.py --pdf-dir ./pdfs --out-dir ./texts --sections`
4. Fetch BibTeX for the found arXiv IDs:
   - Run: `python3 scripts/arxiv_bibtex.py --from-jsonl ./arxiv.jsonl --out ./refs.bib`
5. Generate a structured research brief (table + clusters + TODO slots for notes):
   - Run: `python3 scripts/generate_report.py --jsonl ./arxiv.jsonl --out ./REPORT.md`

Then ask Codex to synthesize (taxonomy/benchmarks/experiments) using `REPORT.md` + your notes.

## Workflow decision tree

### A) “I need a lit review plan + paper outline”

Do this:
1. Use the scripts to produce `REPORT.md` (table + clusters) and `refs.bib`.
2. Build a survey plan as a *set of falsifiable questions* + “what evidence would change my mind”.
3. Output deliverables (in this order):
   - Lit review plan (subtopics → why → representative papers to read first)
   - Benchmarks/metrics (existing + proposed) aligned to the hypothesis
   - Validation experiments (including representation/probing/interventions)
   - Paper outline + expected contributions

When relevant, include “fastest path to reproduce” (datasets, eval harnesses, probing code).

### B) “I need a reproducibility-first shortlist”

Prioritize:
- Open-source repos (training recipe, evaluation harness, probing code)
- Clear protocol (hyperparams, seeds, compute, preprocessing)
- Reusable artifacts (scripts, configs, checkpoints, datasets)

Do this:
1. Run `arxiv_survey.py` with stricter terms and fewer results (e.g., 30–80).
2. Ask Codex to rank papers in `REPORT.md` by reproducibility criteria:
   - Code availability, license clarity, dataset accessibility, protocol completeness
3. Produce:
   - Ranked shortlist with repo links (if available)
   - “Reusable parts” per paper (eval harness / probing / training recipe)
   - Minimal reproduction plan (timeboxed: 2h / 1d / 1w)

### C) “I need an evaluation suite + detection experiments (multilingual latent reasoning)”

Use this structure:
1. Hypothesis → operational definition (what counts as “English latent reasoning”)
2. Tasks:
   - Multi-step reasoning across languages (same semantics, different surface forms)
   - Translation-free reasoning (language-neutral, symbol-heavy, or synthetic)
   - Controlled prompts enforcing target-language output
3. Metrics that separate reasoning vs fluency:
   - Task accuracy, step-consistency proxies, calibration, controllability, latency
4. Representation-level detection:
   - Layer-wise language ID / probing on activations
   - Activation patching/interventions (swap “language subspace” signals)
   - Forced-language and mixed-language ablations
5. Expected signatures + failure modes (confounds: translation, tokenization, data mixture)

Use `assets/experiment_checklist.md` as the backbone checklist.

## Templates (assets/)

Copy and fill these as working docs:
- `assets/research_brief.md` → one-topic brief (taxonomy + top papers + open questions)
- `assets/paper_comparison_table.md` → consistent per-paper extraction fields
- `assets/experiment_checklist.md` → step-by-step experimental checklist

## Scripts

All scripts are pure-Python (stdlib) where possible. `pdf_extract.py` supports optional extractors; if none are available, it prints a clear install hint.

### `scripts/arxiv_survey.py`
Search arXiv via the official Atom API, write results to JSONL, and optionally download PDFs.

### `scripts/arxiv_bibtex.py`
Fetch BibTeX from arxiv.org for a list of arXiv IDs or a JSONL produced by `arxiv_survey.py`.

### `scripts/pdf_extract.py`
Extract text from PDFs into `.txt` and optionally produce rough section splits (heuristics).

### `scripts/dedupe_jsonl.py`
Dedupe a JSONL file by `arxiv_id` and near-duplicate titles (useful when iterating queries).

### `scripts/generate_report.py`
Generate a structured Markdown report (table + clusters + TODO note slots) from `arxiv.jsonl`.

## References

Read when you need query patterns or a report schema:
- `references/arxiv_query_guide.md`
- `references/report_fields.md`

---

### Output quality bar (what “good” looks like)
- Prefer explicit assumptions + failure modes over broad claims.
- Prefer checklists and protocols over vague “future work”.
- Always separate: (1) claim, (2) evidence, (3) test that could falsify it.
