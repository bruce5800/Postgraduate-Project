# Paper Outline — COMBINED (experimental study + impossibility theorem)

**Structure decided:** ONE paper — experimental study as the main line, Direction C
(the impossibility theorem T1) as a theory section that *explains* the empirical wall.
The arc: **the experiments discover a wall (predictions are robustness insurance, not
performance); the theory proves the wall is necessary.**

**Working title:** *The Limits of Predictions for Online Bipartite Matching: A Unified
Experimental Study and an Impossibility Theorem* (alt: *Robustness Insurance: Why
Sublinear Test-and-Fallback Cannot Beat the Baseline on Average-Case Matching*).

**Target venue:** a venue that welcomes experiment+theory — ACM JEA / SEA / ALENEX
(experimental-algorithms, theory-friendly). If the theorem lands cleanly and the
advisor agrees, an alternative is to split the theory to SODA/ESA/ITCS and keep the
experimental paper for JEA — but the DEFAULT is the combined paper.
**Format precedent:** Chłędowski, Polak, Szabucki & Żołna, *Robust Learning-Augmented
Caching: An Experimental Study* (ICML 2021) — the experimental-study template we match
and whose combiner we benchmark.

**One-line pitch:** The learning-augmented online-matching algorithms (ACI's MPD,
Choo/BEM's test-and-fallback) and the classical baselines were each studied in
isolation. We put them on one harness and show, with confidence intervals and on real
data, that on average-case inputs their value is **robustness insurance, not a
performance lift** — then we **prove why**: no sublinear-test test-and-fallback can be
both consistent and robust on strong-baseline matching, because the structure that makes
the test feasible is the structure that makes the baseline near-optimal.

**⚠️ Writing-order caveat (theory section):** write the experimental sections and the
theory section's *framing / statement* now, but keep the **proof** of T1 marked
"to finalize" until (a) the last routine step (witness-instance match) is closed and
(b) the advisor signs off on the tolerant-testing reduction. Do not typeset T1 as a
finished theorem before both.

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
- **C5 — The impossibility theorem (the theory contribution).** The empirical wall is
  necessary: **no test-and-fallback algorithm with a sublinear test can be both
  (1−o(1))-consistent and robust on strong-baseline matching** — the structure that
  makes the prefix distribution-test feasible (few high-count types) is exactly the
  structure that makes the baseline near-optimal, so "wherever you can test, you don't
  need to." Proven via a master consistency/robustness inequality + a reduction to
  *tolerant* distribution testing (Θ̃(n/log n), Canonne et al. 2022), with the
  advice-loss↔L1 conversion an exact affine law. *(Direction C; `docs/T1_PROOF_SKELETON.md`,
  `T1_W1_single_cell.md`, `T1_W3_construction.md`, `T1_W2_W3a_closeout.md`.)*
  **⚠️ proof to finalize + advisor sign-off before typesetting as a theorem.**

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

### §6.5 Does *learning* the predictor help? A negative result *(M0–M3, optional subsection)*
- Because MPD consumes the predictor only through its order (§4), one might train it
  with an order-aware (rank) loss instead of regression. It helps *only* when features
  induce an order/magnitude divergence; on real temporal features it does not
  (rank-training ≡ MSE-training, identical Kendall-τ). Honest negative that reinforces
  F3. **Figure** (`results/rank_when_it_matters.png` or the M3 trace figure).
  *(`docs/RANK_LEARNING_M0_M3.md`.)* — include as a short subsection or an appendix.

### §7 THE IMPOSSIBILITY THEOREM — why the wall is necessary *(C5, the theory section — NEW centerpiece)*
- **The framing:** every experiment above hit the same wall (F3). Here we prove it is
  forced, not incidental — the theoretical payoff that turns an experimental study into
  an experiment+theory paper.
- **§7.1 Model & the test-and-fallback class**; consistency, robustness, baseline
  strength ρ_base, sublinear test budget k.
- **§7.2 The master tradeoff (Lemma 1, rigorous):** (1−η_c) ≤ η_r + γ_k — a Le Cam
  two-point argument; the clean two-sided core.
- **§7.3 The reduction (Lemma 2):** a consistent+robust algorithm ⟹ a tolerant
  distribution tester (the prefix *is* i.i.d. samples) — makes it "any rule", not just
  Choo's threshold. This is the differentiator from Choo's constructive β-in-threshold.
- **§7.4 The construction (W1 + W3):** rare-resource cells; the advice-loss↔L1
  conversion is an **exact affine law** (`follow-ratio = ρ_perfect − ½L1`, verified);
  r=Θ(n) → invoke the tolerant-testing lower bound (Canonne et al. 2022, Θ̃(n/log n)) →
  sublinear k insufficient. The good side is a Θ(1) ball (a>0) → provably tolerant.
- **§7.5 Theorem T1** (statement) + the scissors **Figure 7**
  (`results/impossibility_frontier.png`) as the numerical face of the theorem.
- **Over-claim guardrails:** credit Choo's constructive coupling; state the r=Θ(n)
  scope; the one remaining routine step (witness-instance match) — present honestly.
- *(Docs: `T1_PROOF_SKELETON.md`, `T1_W1_single_cell.md`, `T1_W3_construction.md`,
  `T1_W2_W3a_closeout.md`.)*

### §8 Application case study: AI-inference serving *(optional, clearly demoted)*
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
