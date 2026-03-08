---
name: paper-reviewer
description: Review research papers (especially PDFs). Use when the user asks to read/通读/讲解/总结/审稿 a paper and wants a Chinese-first explanation of what it does, what is novel (创新点), plus reviewer-style strengths/weaknesses, major/minor concerns, and questions to authors.
---

# Paper Reviewer

## Overview

Read a paper end-to-end (prefer PDF), then produce a teachable explanation and a reviewer-style critique: content summary, innovation points, evidence quality, and actionable concerns.

## Quick Start (Inputs)

- Paper: local PDF path (preferred), or arXiv/DOI/citation.
- Audience: beginner / familiar-with-field / expert.
- Focus: method / experiments / critique / implementation.
- Depth: 10-min / 30-min / 90-min talk notes (default: 30-min).
- Target venue (optional): e.g., NeurIPS/ICLR/ACL, or "internal reading group".

If the user does not specify, assume: audience="熟悉基础 ML", focus="method + experiments + critique", depth="30-min", language="Chinese".

## Workflow

### 1) Identify the paper

- If multiple PDFs exist, ask which one to review.
- Record title/authors/venue/year (as shown), and page count.

### 2) Extract text and render pages (prefer visual skim)

- Use the helper script to extract per-page text and (optionally) render pages to PNG for figure/table inspection:
  - `python3 skills/paper-reviewer/scripts/dump_paper_pdf.py --pdf "<PATH>" --out-dir "tmp/paper-review/<slug>" --render`
- If rendering fails (missing `fitz`/PyMuPDF), rerun without `--render` and continue.

### 3) First pass: map the paper (10-20 min)

- Identify:
  - Problem setting, inputs/outputs, assumptions.
  - 3-5 core contributions (claimed novelty).
  - The "main loop" of the method in one paragraph.
  - Which experiments are intended to support which claims.

### 4) Second pass: teach the method

- Explain in this order (even if the paper orders differently):
  1. Problem + why it matters.
  2. Baseline mental model (what a reasonable approach would do).
  3. What is new (the delta vs baselines/prior work).
  4. Method (step-by-step; pseudocode-level).
  5. Complexity and failure modes.
- For equations: explain what each term does, not just restate symbols.
- When referencing results, cite section/figure/table numbers (and page numbers if helpful).

### 5) Third pass: experiments and evidence

- For each experiment:
  - State the claim being tested.
  - Describe the setup (data, metrics, protocol, baselines).
  - Interpret the result: what it supports; what it does not.
  - Call out confounds: data leakage, unfair tuning, missing ablations, weak baselines, small sample, cherry-picking.

### 6) Innovation analysis (创新点核验)

- For each claimed innovation, answer:
  - What is new?
  - Why does it matter (what capability improves)?
  - What prior work is it closest to (most plausible "already known" baseline)?
  - What evidence supports the claim?
  - What experiment/ablation would falsify it?

### 7) Reviewer-style critique

- Use `references/review_rubric.md` as a checklist.
- Avoid long verbatim quotes; paraphrase.

## Output Format (Recommended)

- `一句话结论 (TL;DR)`
- `这篇论文在做什么` (problem + setting)
- `方法概览` (core idea + main loop)
- `贡献/创新点` (3-6 bullets; claimed vs assessed)
- `方法细讲` (module-by-module; pseudocode-level)
- `实验解读` (what each supports)
- `优点 (Strengths)`
- `主要问题 (Major concerns)` (actionable: why it matters + what to add/change)
- `次要问题 (Minor concerns)`
- `给作者的问题` (questions to clarify)
- `可复现性清单` (data/code/hparams/eval)
- If asked: `评分 + 信心`

## Script: `scripts/dump_paper_pdf.py`

- Purpose: extract per-page text and (optionally) render pages to PNGs.
- Outputs (under `--out-dir`):
  - `metadata.json`
  - `text_by_page.txt`
  - `headings_guess.txt`
  - `captions_guess.txt`
  - `render/` (PNG pages if `--render`)
