# Paper Review Rubric (Checklist)

Use this rubric to generate reviewer-style output: strengths, major/minor concerns, and questions to authors.

## 1) Core Claims and Evidence Mapping

- What are the paper's 3-5 central claims?
- Which figure/table/experiment supports each claim?
- Does any experiment test multiple claims at once (confounded evidence)?

## 2) Novelty (创新点) Checklist

- Clearly state the delta: what changes vs the closest prior work/baseline?
- Verify whether the "new" part is:
  - A new objective / learning signal
  - A new model/module/architecture
  - A new training recipe or data
  - A new evaluation protocol/benchmark
  - A new theoretical result
- Ask: would a strong baseline + tuning plausibly reach the same result?
- Ask: what minimal ablation isolates the contribution?

## 3) Technical Correctness

- Definitions are precise; assumptions are explicit.
- Optimization objective matches the intended behavior (no mismatch).
- Algorithm is fully specified (not hand-wavy).
- Claims are consistent with equations and implementation details.
- Edge cases and failure modes are acknowledged.

## 4) Experimental Rigor

- Baselines are appropriate and strong (not strawman).
- Hyperparameter tuning budget is comparable across methods.
- Metrics match the claims (and are not gamed).
- Ablations cover: each component, each loss term, each data source.
- Results include variance/seeds or statistical confidence where applicable.
- Generalization is tested: more than one dataset/task/setting when claims are broad.

## 5) Reproducibility

- Training/eval details: datasets, splits, prompts, seeds, hardware, batch sizes.
- Clear evaluation protocol; no hidden filtering/post-processing.
- Code availability and licensing (if claimed).
- Compute costs are reported (or at least roughly bounded).

## 6) Safety / Ethics (If Applicable)

- For agent/LLM safety: define the threat model and the safety objective clearly.
- Evaluate against realistic adversaries or failure modes, not only benign settings.
- Check for reward hacking / specification gaming.
- Consider distribution shift and long-horizon behavior.

## 7) Output Structure (Recommended)

- TL;DR (1-3 sentences)
- What problem + setting
- Method overview + main loop
- Contributions/innovation points (claimed vs assessed)
- Experiments: claim-by-claim evidence
- Strengths
- Major concerns (actionable)
- Minor concerns
- Questions to authors
- Reproducibility checklist
- Optional: score + confidence (only if user asks)

