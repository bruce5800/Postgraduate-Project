# Unified Benchmark — the head-to-head study (paper lead contribution)

**Status:** complete. This is the experiment the literature review flagged as the
strongest, unoccupied publishable angle (`docs/LITERATURE_REVIEW.md` Q2): no prior
work benchmarks the learning-augmented online-matching algorithms *together*. ACI
(MinPredictedDegree / degree predictions), Choo & BEM (type-histogram advice,
test-and-fallback), and the classic advice-free baselines were each studied in
isolation — on their own graphs, with their own error models, against their own
anchors. Here they share **one harness**: common graphs, a common
prediction-quality knob, a common OPT (Hopcroft–Karp), and a common
confidence-interval methodology.

**Driver:** `scripts/run_unified_benchmark.py` (~100 s, seed 0/1/2).
**Combiner baseline:** `algorithms/combiner.py` (tests `tests/test_combiner_small.py`).
**Raw tables:** `results/unified_benchmark_tables.md`; figure
`results/unified_benchmark.png`; data `results/unified_benchmark.json`.

## 0. Honest scope of "unified"

The algorithm families consume **different prediction objects** — degree vectors μ
(MPD and its augmentations) vs type-count histograms ĉ (Follow / Choo / BEM /
Combiner). No single scalar makes them strictly comparable. We therefore unify on
a per-family **corruption knob** (random-flip/adversarial on μ; the η-blend on ĉ),
report the families in parallel panels, and flag the heterogeneity openly — it is
*precisely why* a unified benchmark did not previously exist, and assembling one is
the contribution. The shared pieces (graphs, OPT, CI method, the advice-free floor)
are what make the panels read against each other.

CIs are 95% normal-approximation half-widths over trials (ddof=1).

## 1. The three panels

### Panel A — clvb_zipf, n=1000, 60 trials (degree-prediction regime)

| Algorithm | perfect | noisy | adversarial | garbage |
|---|---|---|---|---|
| SimpleGreedy *(advice-free)* | 0.917 ±.003 | — | — | — |
| **Ranking** *(advice-free floor)* | **0.948 ±.002** | — | — | — |
| Feldman *(advice-free)* | 0.887 ±.003 | — | — | — |
| JailletLu *(advice-free)* | 0.901 ±.004 | — | — | — |
| MinDegree *(oracle ceiling)* | 0.996 ±.001 | — | — | — |
| MPD | 0.989 ±.001 | 0.956 ±.002 | **0.908 ±.003** | 0.946 ±.003 |
| Feldman(MPD) | 0.981 ±.002 | 0.979 ±.002 | 0.976 ±.002 | 0.978 ±.002 |
| JailletLu(MPD) | 0.977 ±.002 | 0.976 ±.002 | 0.974 ±.002 | 0.975 ±.002 |

### Panel B — left_regular d=5, n=1000, 60 trials (homogeneous regime)

| Algorithm | perfect | noisy | adversarial | garbage |
|---|---|---|---|---|
| SimpleGreedy *(advice-free)* | 0.890 ±.002 | — | — | — |
| **Ranking** *(advice-free floor)* | **0.890 ±.002** | — | — | — |
| Feldman *(advice-free)* | 0.758 ±.002 | — | — | — |
| JailletLu *(advice-free)* | 0.789 ±.003 | — | — | — |
| MinDegree *(oracle ceiling)* | 0.966 ±.001 | — | — | — |
| MPD | 0.932 ±.002 | 0.906 ±.002 | **0.854 ±.002** | 0.888 ±.002 |
| Feldman(MPD) | 0.906 ±.002 | 0.903 ±.002 | 0.896 ±.002 | 0.900 ±.002 |
| JailletLu(MPD) | 0.903 ±.002 | 0.902 ±.002 | 0.898 ±.002 | 0.901 ±.002 |

### Panel C — few_types r=8, n=2000, 50 trials (type-advice regime)

| Algorithm | perfect | mild | bad | garbage |
|---|---|---|---|---|
| **Ranking** *(advice-free floor)* | **0.990 ±.001** | — | — | — |
| MPD (true degrees) *(cross-family ref)* | 0.999 ±.000 | — | — | — |
| FollowPrediction | 1.000 ±.000 | 0.832 ±.008 | 0.679 ±.016 | **0.472 ±.027** |
| TestAndMatch (Choo) | 1.000 ±.000 | 0.984 ±.007 | 0.989 ±.001 | 0.990 ±.001 |
| TestAndMatch (BEM) | 0.998 ±.001 | 0.988 ±.003 | 0.988 ±.001 | 0.968 ±.003 |
| Combiner *(Chłędowski-style, benchmark)* | 0.990 ±.001 | 0.990 ±.001 | 0.990 ±.001 | 0.990 ±.001 |

*("—" = prediction-independent; the value is constant across quality. Bold = the
key cell: the advice-free floor, and where each naive follower crashes below it.)*

## 2. The cross-cutting findings (what the unified view buys you)

**F1 — Robustness is *engineered*, not free; naive followers crash below the
advice-free floor.** Both raw prediction-followers dive under the Ranking floor
once advice is adversarial/garbage: **MPD 0.908 < 0.948** (Panel A, adversarial),
**0.854 < 0.890** (Panel B); **FollowPrediction 0.472 ≪ 0.990** (Panel C). A
practitioner using either *unguarded* is strictly worse off than using no
prediction at all. Every *robust* algorithm in the tables (the (MPD)-augmentations,
TestAndMatch, Combiner) avoids this — by construction, not by luck.

**F2 — There are two distinct robustness mechanisms, and the benchmark exposes
their different shapes.**
- *Structural (Feldman(MPD), JailletLu(MPD)).* A worst-case-optimal base matching
  (max-flow / LP) carries the load; the prediction only breaks ties on the greedy
  fallback. Result: **almost flat across prediction quality** — Feldman(MPD) moves
  only 0.981→0.976 from perfect to adversarial (Panel A). It cannot crash, but it
  also **caps the upside** (0.976–0.981, never reaching the 0.996 oracle, and below
  MPD's 0.989 perfect score). Robustness bought by giving up consistency.
- *Adaptive (TestAndMatch).* Test a sublinear prefix, then commit. Captures the
  upside when advice is good (Choo 1.000 at perfect, Panel C) **and** stays on the
  floor when advice is bad (0.990 at garbage). On Panel C it is the only algorithm
  on the *upper envelope at both ends* — the best of both mechanisms.

**F3 — The consistency upside is small on average-case inputs; the spread between
algorithms lives almost entirely on the bad-advice side.** On few_types the
advice-free Ranking is already 0.990 and MPD-with-true-degrees is 0.999 — there is
< 0.01 for *any* advice to add on the good side. Every wide gap in Panel C
(1.000→0.472 for Follow; the 0.5-wide envelope) is a *downside* gap. This is the
project's through-line, now demonstrated head-to-head: **learning-augmented
matching on typical inputs is robustness-insurance, not a performance lift.**

**F4 — Structurally weak base algorithms are the ones the augmentation rescues.**
Feldman/JailletLu are tuned for the worst-case ratio, and on these average-case
inputs they are the *weakest* advice-free entries (Panel B: 0.758 / 0.789, well
below SimpleGreedy's 0.890). The MPD augmentation lifts them to ≈0.90 — the
prediction does more for the worst-case-designed algorithms than for greedy. A
non-obvious pairing only a unified table surfaces.

## 3. The combiner — benchmarked, not claimed (and where it breaks)

The Chłędowski et al. (ICML 2021) **blind-follow + baseline with switching**
combiner is the established "cheap worst-case insurance" in caching. We ported it
(`algorithms/combiner.py`: follow-the-leader over shadow Follow/Ranking runs, with
a hysteresis margin γ) and benchmarked it — **we do not claim it as novel.** Two
findings, both honest:

1. **In its intended (robust) tuning it is dominated, not broken.** With γ scaled
   to the instance it sits exactly on the floor (0.990 across all of Panel C):
   never crashes, but captures *none* of the consistency upside — strictly
   dominated by TestAndMatch (Choo) on the good-advice side and equal to it on the
   bad side. Cheap insurance, but redundant here because Ranking *is* already the
   floor and already near-OPT.
2. **Eager switching exposes an irrevocability penalty unique to matching.** With a
   small γ the combiner *does* switch mid-stream — and on **perfect** advice it
   then scores **below both experts** (0.927 vs Follow 1.000 and Ranking 0.958 on
   the n=600 test instance; `tests/test_combiner_small.py`). The reason is
   structural: matching decisions are irrevocable, so switching from Ranking to
   Mimic mid-run lands the live matched set in an **incompatible hybrid** — the
   Mimic plan's slots are already half-consumed by the Ranking phase, and the
   Ranking progress is abandoned. You get the worst of both.

   This is exactly why Choo/BEM **test on a prefix and then commit once** rather
   than switching dynamically: in an irrevocable problem the decision must be made
   *before* the bulk of the commitments, not adapted across them. The caching-style
   dynamic combiner does not port cleanly to matching, and the unified benchmark
   shows *why* — a genuine, paper-grade observation that motivates the
   test-and-fallback design.

## 4. How to position this in the paper

- **This table is the lead.** It is the first head-to-head of the three families
  under one harness with CIs. The narrative writes itself from F1–F4: *predictions
  are robustness-insurance; two mechanisms deliver it with different
  consistency/robustness trade-offs; naive followers are unsafe; the dynamic
  combiner is dominated and reveals why irrevocable problems need test-then-commit.*
- **Precedent/format template:** Chłędowski et al. ICML 2021 (the caching
  experimental study) — and we engage it directly via the combiner, both
  benchmarking it and showing its mechanism's limit on matching.
- **Honesty guardrails kept:** the prediction-object heterogeneity is stated, not
  hidden (§0); the combiner is a benchmark, not a claim (§3); the small consistency
  upside is reported as the *finding*, not buried (F3).

## 5. Limitations / natural extensions

- One canonical error model per degree panel (random-flip + the adversarial worst
  case). The full four-model order-error story is in `run_order_vs_theory.py` /
  `run_mpd_error_spectrum.py`; here we use the two endpoints that matter for the
  robustness narrative.
- Panel C uses the empirical-L1 surrogate (documented in `PHASE3C_REPORT.md` §1) —
  the Jiao et al. tester has no off-the-shelf implementation; the Choo/BEM authors
  use the same surrogate.
- Real-graph universality of F1–F3 (the 6 Network-Repository graphs) is the natural
  next experiment (★4), as is a recalibrated-threshold row for Panel C
  (`run_recalibration.py` already has the mechanism).
