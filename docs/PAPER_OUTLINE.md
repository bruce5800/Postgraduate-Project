# Paper Outline — Learning-Augmented Online Bipartite Matching: A Unified Experimental Study

**Working title:** *An Experimental Study of Learning-Augmented Algorithms for
Online Bipartite Matching* (alt: *Robustness Insurance: A Unified Benchmark of
Prediction-Based Online Matching*).

**Target venue:** ALENEX / ACM JEA / SEA (experimental-algorithms track).
**Format precedent:** Chłędowski, Polak, Szabucki & Żołna, *Robust
Learning-Augmented Caching: An Experimental Study* (ICML 2021) — same shape, in
caching; we are the matching counterpart, and we engage their combiner directly.

**One-line pitch:** The learning-augmented online-matching algorithms (ACI's MPD,
Choo/BEM's test-and-fallback) and the classical baselines were each studied in
isolation. We put them on one harness and show, with confidence intervals and on
real data, that on average-case inputs their value is **robustness insurance, not a
performance lift** — and we characterise *why*, *how much*, and *at what cost*.

---

## Contributions (state these verbatim in §1)

- **C1 — The unified benchmark.** The first head-to-head experimental comparison of
  all three families (advice-free baselines; MinPredictedDegree + its
  Feldman/JailletLu augmentations; Follow/Choo/BEM test-and-fallback) under one
  harness — common graphs, a common prediction-quality knob, common OPT, common 95%
  CIs. *(★2; `docs/UNIFIED_BENCHMARK.md`.)*
- **C2 — The robustness-insurance characterisation (F1–F4).** Naive followers crash
  *below* the advice-free floor under bad predictions (F1); two distinct robustness
  mechanisms — structural (augmentations) vs adaptive (test-and-fallback) — buy
  safety with different consistency/robustness trade-offs (F2); the consistency
  upside is small on average-case inputs, so the value is downside protection (F3);
  the augmentation rescues structurally-weak base algorithms (F4). Validated on
  synthetic graphs, **6 real graphs**, and a **real trace**.
- **C3 — Engaging the order-error theory.** ACI's Appendix-D `n−LIS` bound is correct
  but **~20–75× loose and saturates**; **Kendall-τ** is the order measure that
  actually predicts the realised MPD loss, and four error models collapse onto it.
  *(★1; `scripts/run_order_vs_theory.py`.)*
- **C4 — The first empirical study of test-and-fallback.** Testing-cost / threshold
  calibration / misjudgement on Choo/BEM: a worst-case-calibrated threshold is **too
  lenient on average-case inputs** (a more accurate test makes a *worse* decision);
  recalibrating to the measured baseline fixes it but reveals a resolution limit; and
  a Chłędowski-style **dynamic combiner is dominated** because mid-stream switching in
  an *irrevocable* problem incurs a hybrid-state penalty — explaining *why*
  test-then-commit is the right structure. *(Phase 3c + combiner; `docs/PHASE3C_REPORT.md`.)*

**Honest scope (state in §1 too):** the families consume different prediction
objects (degree vectors μ vs type-count histograms ĉ); we unify on a per-family
corruption knob and report in parallel panels — the heterogeneity is exactly why no
unified benchmark existed. The serving instantiation is presented as an *application
case study*, not a novelty claim.

---

## Section-by-section

### §1 Introduction
- Online bipartite matching under known-i.i.d.; the algorithms-with-predictions
  lens; consistency vs robustness.
- The gap: fragmented, single-algorithm, mostly-theoretical evidence; no common
  benchmark; theory (ACI) and the test-and-fallback papers each evaluate in
  isolation with their own anchors.
- Contributions C1–C4 + the honest-scope paragraph.

### §2 Setup
- Model: known-i.i.d., competitive ratio ALG/OPT, Hopcroft–Karp OPT.
- Algorithms (one paragraph each): SimpleGreedy, Ranking (floor), Feldman,
  JailletLu (baselines); MinPredictedDegree + (MPD)-augmentations; FollowPrediction,
  TestAndMatch (Choo/BEM); the Chłędowski-style combiner (a benchmarked baseline).
- Prediction objects and the **structured error models** (the four μ models +
  the ĉ η-blend); the order-error vs magnitude distinction up front.
- Reproducibility: Python harness, paired RNG streams, seeds. *(Reproduces a subset
  of Borodin et al. 2018 — cite as the foundation; `docs/PHASE2_REPORT.md`.)*

### §3 The unified benchmark *(C1, C2 — the lead)*
- **Table 1** (3 panels, 95% CIs): Panel A clvb_zipf, Panel B left_regular,
  Panel C few_types. *(from `results/unified_benchmark_tables.md`.)*
- **Figure 1**: grouped bars, three panels. *(`results/unified_benchmark.png`.)*
- F1–F4 walked through with the numbers (MPD adversarial 0.908 < Ranking 0.948;
  Follow 1.000→0.472; Feldman(MPD) flat 0.981→0.976; Feldman base 0.758 rescued).
- Lands the robustness-insurance thesis.

### §4 What governs the loss: order-error and ACI's bound *(C3)*
- MPD depends on μ only through induced order ⇒ order-error, not magnitude.
- **Figure 2** (two panels): actual loss vs ACI `n−LIS` (loose + saturates); loss
  collapses onto Kendall-τ across four models. *(`results/order_vs_theory.png`.)*
- Explicitly credit ACI Cor. D.2 for order-dependence + monotone-zero; our
  contribution is the *tightness/saturation characterisation* and *Kendall-τ as the
  governing measure*. **(Over-claim guardrail — do NOT say "we discovered order
  matters".)**

### §5 Test-and-fallback in depth *(C4)*
- The robustness envelope (ratio vs advice L1): Follow crashes, TestAndMatch holds
  the upper envelope. **Figure 3** (`results/choo_bem_envelope.png`).
- **The miscalibration finding (RQ3):** a larger/more-accurate prefix test makes a
  *worse* decision because the worst-case threshold is too lenient on average-case
  inputs. **Figure 4** (`results/choo_bem_prefix.png`).
- **The recalibration fix** and its resolution-limit honesty (`results/recalibration_*`).
- **The combiner result:** in robust tuning it is dominated (= floor, no upside);
  eager switching dips *below both experts* (0.927) — the irrevocability hybrid
  penalty, which is *why* Choo/BEM test-then-commit. Connects to the Chłędowski
  precedent. *(tests: `tests/test_combiner_small.py`.)*
- Caveat (one line): empirical-L1 surrogate, same as the papers' own authors.

### §6 External validity *(C2 support — the part that answers "is any of this real?")*
- **§6.1 A real, cheap predictor (★3).** Wikipedia trace, historical-window
  forecast. **Figure 5** (`results/real_predictor.png`): topology aggregation halves
  the order error; a stale forecast captures 27–68% of the oracle gap, never below
  baseline; cost = 2% of OPT (a count, not ML). Blind histogram-following collapses
  on the same forecast. *(`docs/REAL_PREDICTOR.md`.)*
- **§6.2 Six real graphs (★4).** F1 holds 6/6; F3 universal and smallest where the
  baseline is strongest; F2 clean on social/bio, partial on near-trivial dense econ
  graphs (instructive boundary). **Figure 6** (`results/realworld_robustness.png`).
  *(`docs/REALWORLD_ROBUSTNESS.md`.)*

### §7 Application case study: AI-inference serving *(optional, clearly demoted)*
- Online b-matching for request routing; capacity-c, traffic forecasts, dynamic
  service times, prefix-cache routing; on three real traces.
- **Framed explicitly as a case study** showing the framework instantiates a
  contemporary systems problem — *not* a novelty claim (the systems results are
  established). One figure max. *(`docs/PHASE4_SERVING_REPORT.md`.)*
- *Decision flag:* include only if page budget allows; otherwise cut to a paragraph
  + appendix. (Lit review Q3 verdict: re-derivation risk.)

### §8 Related work
- ACI (MPD), Choo (2024), BEM (2026) — single-algorithm/theoretical; we benchmark
  them together and engage ACI's appendix empirically.
- Chłędowski et al. (2021) — the format template and the combiner we benchmark.
- Borodin et al. (2018) — the advice-free experimental foundation we extend.
- Serving prior art (Preble, Mooncake, SageServe, …) — for §7 only.

### §9 Limitations & conclusion
- Known-i.i.d. harness (Known-IID ≤ Random-Order, so guarantees carry); empirical-L1
  surrogate; degree-prediction families don't all map to every graph; one trace per
  modality.
- Conclusion: restate robustness-insurance + the four contributions.

---

## Figures / tables manifest (all already generated)

| # | Asset | Source | Section |
|---|---|---|---|
| Table 1 | unified benchmark (3 panels, CIs) | `results/unified_benchmark_tables.md` | §3 |
| Fig 1 | unified benchmark grouped bars | `results/unified_benchmark.png` | §3 |
| Fig 2 | order-error vs ACI `n−LIS` + Kendall-τ collapse | `results/order_vs_theory.png` | §4 |
| Fig 3 | test-and-fallback envelope | `results/choo_bem_envelope.png` | §5 |
| Fig 4 | prefix/testing-cost miscalibration | `results/choo_bem_prefix.png` | §5 |
| Fig 4b | recalibration (optional) | `results/recalibration_*.png` | §5 |
| Fig 5 | real predictor (Wikipedia) | `results/real_predictor.png` | §6.1 |
| Fig 6 | F1–F3 on 6 real graphs | `results/realworld_robustness.png` | §6.2 |
| Fig 7 | serving case study (optional) | `results/serving_*.png` | §7 |

## Over-claim guardrails (the reviewer-proofing checklist)

1. **Order-error**: cite ACI Cor. D.2; claim only tightness/saturation + Kendall-τ.
2. **Combiner**: benchmarked baseline, Chłędowski-credited, never "novel".
3. **Unified scope**: state the prediction-object heterogeneity openly.
4. **Serving**: case study, not a result; the with-predictions framing is new but
   the systems facts are established.
5. **F2 on real graphs**: "qualitatively 6/6, strictly ≤½ on 4/6" — don't round up.
6. **Empirical-L1**: documented deviation, matches the papers' own proof-of-concept.
7. **Consistency upside small**: report it as *the finding*, not a disappointment.

## Suggested abstract (draft skeleton)

> Learning-augmented algorithms for online bipartite matching have been proposed
> across several papers — MinPredictedDegree, test-and-fallback schemes — each
> evaluated in isolation against its own baselines. We present the first unified
> experimental benchmark of these algorithms under a common harness and a common
> structured prediction-error model, with confidence intervals. Across synthetic
> graphs, six real-world graphs, and a real request trace, we find that on
> average-case inputs the value of predictions is **robustness insurance rather than
> a performance lift**: unguarded prediction-following crashes below the
> advice-free baseline under adversarial predictions, while two distinct mechanisms —
> structural augmentation and adaptive test-and-fallback — restore safety with
> different consistency/robustness trade-offs. We connect the empirics to theory,
> showing that the governing quantity is a Kendall-τ order error (and that the known
> `n−LIS` bound is loose and saturating); we give the first empirical study of the
> test-and-fallback threshold, exposing a worst-case-calibration pathology and its
> fix; and we show a realistic, near-free historical predictor captures a meaningful
> fraction of the achievable gap. [venue], [year].

## Status / what's left before submission

- All experiments run; all figures generated; all findings documented.
- **Optional remaining experiment** (★3-orig): testing-cost sub-linearity (k vs n)
  + read Choo Appendix E — would deepen §5 but is not load-bearing.
- Writing: prose the sections above; finalise title/venue; decide §7 inclusion by
  page budget.
- The proposal docx (`毕业设计提案_v3.docx`) is the thesis-side artifact; this
  outline is the paper-side artifact.
