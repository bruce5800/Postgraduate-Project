# Phase 3 Progress Report — MinPredictedDegree Increment

**Status:** first increment complete (foundation: predictions + 4 error models +
MPD + (MPD)-augmentation hooks). Choo/BEM adaptive frameworks deferred.
**Spec:** see [`docs/PHASE3_SPEC.md`](PHASE3_SPEC.md) (signed off).

## 1. What was built

| Component | File | Notes |
|---|---|---|
| CLV-B/Zipf type graph | `graphs/synthetic.py::clvb_zipf_bipartite` | heavy-tailed offline (R) degrees; ACI §7 (n=m=1000, C=n/2) |
| Degree predictors | `predictions/degree_truth.py` | `type_graph_degree` (MPD), `instance_degree` (MinDegree oracle) |
| Four error models | `predictions/error_models.py` | random_flip, systematic_bias, adversarial, distribution_drift; each returns `(μ', {l1, order_error})` |
| MinPredictedDegree | `algorithms/min_predicted_degree.py` | `mpd = greedy_with_permutation(rank)`, `rank = lexsort(μ, random tiebreak)` |
| (MPD) augmentations | `algorithms/feldman.py`, `algorithms/jaillet_lu.py` | `*_online_mpd`: fall back via MPD rule instead of arbitrary (ACI §7) |
| Tests | `tests/test_mpd_small.py` | 6 tests, all pass |
| RQ2 experiment | `scripts/run_mpd_error_spectrum.py` | ratio vs η, 4 models × 2 graphs |
| (MPD)-augmentation comparison | `scripts/run_mpd_augmentation.py` | base/(g)/(MPD) × Feldman/JailletLu, 2 graphs (§3.3) |
| Real-world loader + experiment | `graphs/realworld.py`, `scripts/run_realworld.py` | 6 Network Repository graphs, 2 conversions, Borodin Tables 3/4 + MPD (§3.4) |

**Unifying observation:** SimpleGreedy, Ranking, and MPD are now *one* online
primitive (`greedy_with_permutation`) with three rank sources — identity,
random, and degree-order. The whole Phase-2+3 greedy family collapses to one
loop. MPD added **zero** new online-stage code.

## 2. Verified anchors (tests)

- **MPD(constant μ) ≡ Ranking** — mean matching sizes 171.4 vs 171.6 over 200
  trials (|Δ| = 0.26).
- **MPD(true realized degree) = MinDegree** ≥ MPD(type-graph degree) ≥ Ranking
  on Zipf (158 ≥ 156 ≥ 149).
- **Systematic bias is order-invariant** — `μ·(1+η)` leaves MPD's output
  bit-identical for all η, with Kendall-τ order-error ≡ 0.
- random_flip at η=1 → order-error ≈ 0.50 (random ≈ half-reversed);
  adversarial at η=1 → order-error = 1.00 (full reversal). Same η, different
  structure.

## 3. Main results (n=1000, 100 trials)

### 3.1 Ratio vs error strength η

![MPD spectrum — Zipf](../results/mpd_spectrum_clvb_zipf.png)

| Model | Zipf η=0 → η=1 | Left-Regular η=0 → η=1 |
|---|---|---|
| systematic bias | 0.989 → **0.989** (flat) | 0.932 → **0.932** (flat) |
| distribution drift | 0.989 → 0.973 | 0.932 → 0.890 |
| random flip | 0.989 → 0.948 | 0.932 → 0.889 |
| adversarial | 0.989 → **0.908** | 0.932 → **0.853** |
| — anchors — | MinDegree 0.996 / Ranking 0.947 | MinDegree ~0.94 / Ranking 0.891 |

Every curve starts at the MPD operating point (η=0) and, except systematic bias,
descends toward (and adversarial *below*) the Ranking floor as η→1.

### 3.2 The methodological finding — ratio collapses onto order-error

![MPD methodological — Zipf](../results/mpd_methodological_clvb_zipf.png)

When the same competitive ratios are re-plotted against the predictor's
**Kendall-τ order-error** (instead of η or L1 magnitude), the four error models
**collapse onto a single monotone curve.** This is the headline result of the
increment:

> **MPD's competitive ratio is, to first order, a function of the Kendall-τ
> order-error of its degree predictor — nearly independent of which error model
> produced that order-error or of the predictor's L1 magnitude.**

Consequences, each a concrete instance of the proposal §5 thesis ("error
*structure*, not magnitude, drives impact"):

1. **Systematic bias is pinned at order-error 0** ⇒ zero impact, at *any*
   magnitude. A monotone mis-scaling of every degree by ×1.5 (large L1) hurts
   MPD exactly as much as no error at all: nothing.
2. **L1 magnitude is not predictive.** At a fixed order-error, random_flip and
   adversarial sit at wildly different L1 (the magnitude plot shows adversarial
   reaching L1≈130 while systematic bias never exceeds 1) yet land on the same
   ratio curve.
3. **The collapse is strong but not perfect.** Adversarial structure extracts
   modestly *more* damage per unit order-error: its points dip below the common
   curve and **below the Ranking floor** once order-error > 0.5 (Zipf 0.908,
   Left-Regular 0.853, both under their Ranking floors). A maximally-wrong
   predictor that prioritizes *high*-degree offline nodes is worse than random —
   which is exactly the failure mode that the deferred Choo/BEM test-and-fallback
   mechanisms exist to guard against.

This finding was not reported by ACI (they evaluated a single subsample-noise
model) and is novel to this study.

### 3.3 (MPD)-augmentation bridge to Phase 2 (Phase 3b)

`scripts/run_mpd_augmentation.py` compares, for FeldmanEtAl and JailletLu, the
base (non-greedy) / greedy `(g)` / `(MPD)` variants, with MPD, MinDegree, and
Ranking as references. The `(MPD)` variant applies the min-predicted-degree rule
(type-graph degrees) wherever the base algorithm would skip. Paired trials share
the JailletLu list-sampling and MPD tie-break randomness.

**ACI §7 claim — `(MPD) ≥ (g) ≥ base` — confirmed in all 4 cases (n=1000, 100 trials):**

| | base | (g) | (MPD) |
|---|---|---|---|
| FeldmanEtAl, Zipf | 0.886 | 0.977 | **0.981** |
| JailletLu, Zipf | 0.900 | 0.974 | **0.977** |
| FeldmanEtAl, Left-Regular | 0.759 | 0.899 | **0.904** |
| JailletLu, Left-Regular | 0.790 | 0.900 | **0.903** |

(The small-scale n=300 run showed one 0.0009 "violation" for JailletLu on
Left-Regular — pure noise; it resolves cleanly at n=1000.)

![(MPD)-augmentation — Zipf](../results/mpd_augment_clvb_zipf.png)

**Two narrative payoffs:**
1. The `(MPD)` lift over `(g)` is small but consistent (+0.003–0.005); the
   base→`(g)` greedy lift is the large one (e.g. Feldman 0.886→0.977 on Zipf).
   This re-confirms Borodin's "greediness is the dominant property", now with
   degree-aware tie-breaking as a second-order refinement.
2. **Plain MPD outranks every `(MPD)`-augmented complex algorithm** (Zipf:
   MPD 0.989 > FeldmanEtAl(MPD) 0.981; Left-Regular: MPD 0.933 >
   FeldmanEtAl(MPD) 0.904). The expensive LP / max-flow preprocessing of
   Feldman/JailletLu adds nothing beyond a simple degree ordering — echoing
   ACI's headline that first-order degree information alone suffices.

### 3.4 Real-world graphs — Borodin Tables 3/4 validation + MPD (Phase 3d)

`graphs/realworld.py` loads six Network Repository graphs (MatrixMarket `.mtx`
and `.edges`, weights/direction dropped, ids densified) and applies the two
Borodin §3.3 bipartite conversions: **random balanced partition** (→ Table 3)
and **duplicating / bipartite double cover** (→ Table 4).
`scripts/run_realworld.py` runs all six algorithms plus MPD/MinDegree and
compares to the paper's reported values (50 trials each).

**Random-partition: clean reproduction.** All six graphs match Borodin Table 3
with max per-cell deviation ≤ 0.058, algorithm ordering preserved.

| graph | SG ours/paper | Rk | F | Fg | J | Jg |
|---|---|---|---|---|---|---|
| Caltech36 | 0.914/0.87 | 0.913/0.86 | 0.751/0.78 | 0.939/0.91 | 0.785/0.81 | 0.941/0.91 |
| CE-PG | 0.882/0.94 | 0.882/0.94 | 0.790/0.81 | 0.943/0.96 | 0.817/0.82 | 0.944/0.96 |
| mbeaw | 0.980/0.95 | 0.978/0.95 | 0.734/0.74 | 0.980/0.95 | 0.766/0.77 | 0.980/0.96 |

**Duplicating: complex algorithms reproduce, greedy does not.** Feldman/JailletLu
(base and (g)) match Table 4 within ≤0.05 on all six graphs, but the *greedy*
algorithms (SimpleGreedy, Ranking) deviate in a **graph-dependent direction**:
socfb high (Caltech36 SG 0.93 vs 0.72, +0.21), bio low (CE-PG SG 0.80 vs 0.95,
−0.15), econ slightly high. Diagnostics ruled out an ordering artifact (SG under
duplicating is order-insensitive here: identity, random-relabel, and Ranking all
give ~0.93) and a uniform "too easy/hard" bias (the deviation flips sign across
families). This points to a structural difference between our bipartite
double-cover construction and the paper's that specifically affects greedy
(sensitive to fine local structure) but not the flow-based algorithms (robust to
it). Without the paper's source — and given Network Repository files have been
revised since 2018 — this is documented as an **open discrepancy**; the
random-partition method is taken as the validated real-world reproduction.

**MPD on real graphs (the Phase 3 payoff): top on every graph, both conversions.**
MPD and MinDegree rank **first on all six graphs under both conversions**
(0.95–1.00), reaching **1.000 on the econ graphs** (heavy-tailed offline degrees).
This reproduces ACI's headline that MPD — using only first-order degree
information — outperforms every online baseline on real data, and extends it to
the JailletLu/FeldmanEtAl known-i.i.d. baselines that ACI did not run head-to-head
in our exact framework.

## 4. Consistency / robustness read-off (RQ2)

For MPD the consistency→robustness interpolation is *automatic* (no engineered
fallback): MPD(perfect)=MinDegree is the consistency ceiling, MPD(random)=Ranking
is the robustness floor, and the η-curves are the empirical smoothness profiles
that theory only bounds. On Zipf the usable band is wide (0.947–0.996); on
Left-Regular it is narrow (0.891–~0.94) because offline degrees are less skewed,
so degree information helps less — consistent with ACI's note that ER (uniform
degrees) is MPD's worst case.

## 5. Limitations / not yet done

- **Choo (TestAndMatch) and BEM** — deferred. They require the type-histogram
  prediction object (object B), a predicted-matching construction, and a
  test-and-fallback (or practical surrogate). The collapse finding above
  motivates them: they are the engineered robustness that MPD lacks.
- **Zipf exponent sweep** (ACI §7 varies it 0.2–2.0) not yet run; we fixed
  exponent=1.0. A sweep would show how MPD's usable band widens with skew.
- **Duplicating-conversion greedy discrepancy** (§3.4) — an unresolved open
  question; the random-partition method is the validated real-world reproduction.

## 6. Reproducibility

```bash
python3 tests/test_mpd_small.py                  # 6 tests
python3 scripts/run_mpd_error_spectrum.py        # ~11s; n=1000, 100 trials
python3 scripts/run_mpd_augmentation.py          # ~22s; (MPD) vs (g) vs base
python3 scripts/run_realworld.py                 # ~6min; 6 graphs × 2 conversions
```
Seed 0; outputs `results/mpd_spectrum_*.{json,png}`, `results/mpd_augment_*.png`,
`results/realworld.json`. Real-world graphs are downloaded from Network Repository
into `data/realworld/` (not committed). Tested on numpy 1.26.4, scipy 1.13.1.
