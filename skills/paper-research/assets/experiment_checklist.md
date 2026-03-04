# Experiment Checklist: Detect latent-language switching (e.g., English latent reasoning)

## 0) Hypothesis → operational definition
- [ ] Write the hypothesis in one sentence.
- [ ] Define what counts as “latent language” (token-level? subspace? probe label?).
- [ ] Define what counts as “switching” (layer/time/attention-head signature).
- [ ] List confounds (translation, tokenization, training mixture, script differences).

## 1) Task suite design
- [ ] Pick 3–5 reasoning task families (math, logic, QA, code, symbolic).
- [ ] For each, define multilingual variants (same semantics, different surface).
- [ ] Add translation-free tasks (language-neutral symbols or synthetic).
- [ ] Add prompt controls enforcing target-language output.
- [ ] Decide the evaluation split: reasoning vs fluency.

## 2) Metrics
- [ ] Task accuracy / exact match.
- [ ] Robustness across paraphrases and languages.
- [ ] Calibration (confidence vs correctness, if available).
- [ ] Consistency checks (invariance to language surface when semantics fixed).
- [ ] Fluency/grammar only as a *separate* axis (avoid conflation).

## 3) Representation-level measurement
### 3.1 Layer-wise probing
- [ ] Choose layers / timepoints to probe (early/mid/late; pre/post attention).
- [ ] Train a language-ID probe on activations (balanced across languages).
- [ ] Validate probe: held-out languages + adversarial controls.
- [ ] Report probe confidence curves vs layer/time.

### 3.2 Intervention ideas
- [ ] Activation patching: swap activations between language conditions.
- [ ] Feature ablation: remove “English subspace” components (project-out).
- [ ] Prompt ablations: forced target-language vs mixed-language vs free.
- [ ] Expected signature: where does performance change most?

## 4) Controls and ablations
- [ ] Match token budgets across languages.
- [ ] Control for translation difficulty (use parallel data when possible).
- [ ] Control for script (Latin vs non-Latin) and tokenization artifacts.
- [ ] Include “nonsense language” or cipher baselines (to stress semantics).

## 5) Reporting
- [ ] Plot: performance vs layer-probe Englishness (or other latent-language score).
- [ ] Provide failure modes and alternative explanations.
- [ ] Provide minimal reproduction steps + scripts/configs.

