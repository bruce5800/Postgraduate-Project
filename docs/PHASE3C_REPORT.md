# Phase 3c Report — Adaptive Test-and-Fallback (Choo 2024 / BEM 2026)

**Status:** complete. This is the last prediction-based algorithm family in the
plan — the *adaptive* ones that detect whether advice is trustworthy and fall
back to a safe baseline if not.
**Spec:** docs/PHASE3_SPEC.md §3.2 (Choo / TestAndMatch), §3.3 (BEM / Test-and-Match+).

## 1. What was built

| Component | File | Notes |
|---|---|---|
| Few-types graph | `graphs/synthetic.py::few_types_bipartite` | r distinct high-count types over n offline nodes, near-perfect-matchable (n̂/n ≈ 1) — the regime the Choo/BEM prefix test is calibrated for |
| Type-histogram advice (object B) | `predictions/type_advice.py` | `true_type_counts`, `build_advice_matching` (M̂ + per-type partners via HK), `perturb_counts` (L1-parameterized, blends toward a spiky Dirichlet target) |
| FollowPrediction (blind trust) | `algorithms/test_and_match.py::follow_prediction` | Mimic (Algorithm 2) on every arrival; no test, no fallback |
| TestAndMatch (Choo & BEM) | `algorithms/test_and_match.py::test_and_match` | Mimic a sublinear prefix, empirical-L1 test, then continue Mimic or fall back to Ranking. `variant='choo'`/`'bem'` differ in early-exit condition and threshold |
| Tests | `tests/test_choo_bem_small.py` | 6 tests, all pass |
| Experiment | `scripts/run_choo_bem.py` | robustness envelope + RQ3 prefix sweep |

**Faithfulness note.** The papers' L1 estimator (Jiao et al. distribution
tester) has no off-the-shelf implementation — Choo §5 says so explicitly and the
authors themselves fall back to an **empirical-L1 proof-of-concept**. We do the
same: empirical L1 of the prefix vs the advice distribution, against the papers'
threshold τ. This is the planned, documented deviation (proposal §9).

The two variants implement the documented differences exactly:
- early-exit: Choo `n̂/n ≤ β` (β=0.696) → BEM `n̂/n < α` (α small);
- threshold: Choo `τ = 2(n̂/n − β)` → BEM `τ = 2(n̂/n)(1−β)/(1+β)`;
- Mimic (Algorithm 2) is identical in both.

## 2. Verified anchors (tests)

- **Perfect advice (ĉ = c*) ⇒ Mimic is optimal.** M̂ on the advice graph equals an
  optimal matching of the realized instance, so blindly following it achieves OPT
  exactly (follow = OPT = 397/397 on the small case).
- **Consistency.** TestAndMatch with perfect advice passes the test and reaches
  ratio 1.000.
- **Robustness.** With garbage advice (L1 = 0.82), blindly following crashes to
  0.592 (below Ranking's 0.985), but TestAndMatch detects it (`followed=False`),
  falls back, and lands at 0.953 — comfortably above the β≈0.696 floor.
- Threshold formulas for both variants verified against the papers.

## 3. Main result — the robustness envelope

![Choo/BEM envelope](../results/choo_bem_envelope.png)

n=2000, r=8 types, 40 trials, prefix k=200. Competitive ratio vs advice error
L1(p,q):

| L1 | FollowPrediction | TestAndMatch (BEM) | TestAndMatch (Choo) | Ranking floor |
|---:|---:|---:|---:|---:|
| 0.00 | 1.000 | 0.998 | 1.000 | 0.991 |
| 0.31 | 0.843 | 0.987 | 0.977 | 0.990 |
| 0.57 | 0.716 | 0.989 | 0.989 | 0.991 |
| 0.82 | 0.591 | 0.988 | 0.990 | 0.991 |
| 1.09 | 0.453 | 0.969 | 0.991 | 0.992 |

**The textbook consistency/robustness picture, and the engineered robustness MPD
lacked.** Blindly following advice (`FollowPrediction`) degrades *linearly* from
1.00 to 0.45 as the advice worsens — well below the advice-free floor. The
adaptive `TestAndMatch` instead stays on the **upper envelope**: it captures the
benefit when advice is good and, when advice is bad, its prefix test rejects it
and falls back to Ranking — never crashing. Contrast Phase 3a: there, MPD had no
such mechanism, and adversarial predictions pushed it *below* the Ranking floor.
Choo/BEM is exactly the fix.

(Honest detail: in the L1 ≈ 0.1–0.2 "confusion zone" the BEM/Choo curves dip
slightly to ~0.95–0.97, because borderline advice is genuinely hard to classify —
see §5.)

## 4. The unifying finding — consistency lift is small on average-case inputs

A striking thing in the table above: even with **perfect** advice, the benefit
over the advice-free baseline is tiny (FollowPrediction 1.000 vs Ranking 0.991).
We confirmed this is structural, not a tuning artifact: across block sizes,
overlaps, and deliberately "contested" few-type structures, **Ranking already
achieves ≈OPT** on these average-case i.i.d. instances (gap ≤ 0.01).

This is not a disappointment — it is the **central thesis of the whole project**,
now demonstrated for the adaptive algorithms too:

> On average-case / i.i.d. inputs the advice-free baseline is already near-optimal,
> so the *consistency* upside of learning-augmented matching is small. Their real
> practical value is **robustness-insurance**: preventing the catastrophic
> downside of trusting bad advice (which the envelope shows dramatically).

This threads Phase 2 (Borodin: simple greedy ≈ complex on average-case) → Phase 3a
(MPD helps only on skewed graphs; Ranking is the floor) → Phase 3c (the adaptive
robustness mechanism earns its keep on the *downside*, not the upside).

## 5. RQ3 — testing cost, and a threshold-miscalibration finding

![Choo/BEM prefix sweep](../results/choo_bem_prefix.png)

RQ3 asks what the "test then maybe fall back" machinery costs in practice. We
sweep the prefix (testing) size k at **borderline** advice (η=0.15, true
L1 ≈ 0.16) — the regime where the test must work hardest; clearly-good or
clearly-bad advice is decided correctly even with a tiny prefix.

| prefix k | ratio (BEM) | misjudgement vs empirical oracle |
|---:|---:|---:|
| 25 | 0.992 | 0.00 |
| 100 | 0.981 | 0.13 |
| 200 | 0.969 | 0.33 |
| 800 | 0.956 | 0.60 |

**Counter-intuitively, a larger (more accurate) test makes the *worse* decision
here.** The mechanism is a real and reportable finding:

- The BEM/Choo acceptance threshold τ is calibrated for the **worst-case**
  baseline β ≈ 0.696. On these average-case instances the baseline is ≈0.99, so
  the *empirical* break-even point (where following advice stops beating the
  baseline) sits at L1 ≈ 0, far below τ−ε ≈ 0.18.
- A small, noisy prefix over-estimates L1 (upward sampling bias) and so
  *accidentally rejects* the borderline advice — landing on the strong Ranking
  floor (0.992).
- A large, accurate prefix correctly estimates L1 ≈ 0.16 < τ−ε, so it **accepts**
  the mildly-bad advice the worst-case threshold deems acceptable — and
  underperforms the baseline (0.956).

So on average-case inputs the worst-case-calibrated threshold is **too lenient**:
it admits advice a practitioner should reject, and improving the test's accuracy
only makes it follow that miscalibrated threshold more faithfully. This connects
RQ3 (testing cost) directly to RQ1 (theory-calibrated vs practice-optimal
behavior) and reinforces §4. A practical fix — recalibrating τ to the *measured*
baseline rather than the worst-case β — is a natural next experiment.

(Note the misjudgement metric is measured against an *empirical* oracle —
"should we have followed, given that following actually underperformed the
baseline on this instance?" — which is precisely why it grows as the test
faithfully tracks the theory-calibrated, but empirically-lenient, threshold.)

## 6. Threshold recalibration — fixing the miscalibration

`scripts/run_recalibration.py` tests the §5 fix directly: replace the worst-case
β=0.696 in the Choo threshold τ = 2(n̂/n − β) with a **measured** baseline β̂ —
the mean empirical Ranking ratio over a small calibration sample (β̂ = 0.986
here). Both thresholds are run on the *same* instances (HK paid once), so the
comparison is exact. N=1200, r=8.

![Recalibration prefix](../results/recalibration_prefix.png)

**The pathology is eliminated.** At borderline advice (η=0.15), the worst-case
threshold's misjudgement climbs 0.03 → 0.63 → 0.87 → 1.00 as the prefix grows,
and its ratio drops 0.986 → 0.920. The recalibrated threshold holds
**misjudgement = 0.00 at every prefix size** and ratio ≈ 0.986 throughout — a
larger prefix no longer hurts.

![Recalibration envelope](../results/recalibration_envelope.png)

**It also closes the confusion-zone dip.** Across the full L1 envelope the
recalibrated curve is flat at ~0.985–0.989, whereas the worst-case curve dips to
0.948–0.977 in the L1 ≈ 0.1–0.3 band (where it follows mildly-bad advice).

**But recalibration reveals a deeper, honest limit.** At L1 = 0 (perfect advice)
the worst-case threshold scores 1.000 — it accepts and follows the perfect advice
— while the recalibrated one scores only 0.987. The recalibrated threshold
(τ ≈ 2(1 − 0.986) ≈ 0.028) is *smaller than the empirical-L1 estimator's noise
floor* (≈0.05–0.13 for r=8 types at this prefix), so the test can never
confidently *accept* advice — it rejects everything, including perfect advice,
and effectively always plays the baseline. So:

> On strong-baseline (average-case) instances, no practical empirical-L1
> threshold can both capture the consistency upside and stay safe: the upside is
> tiny (the baseline is already ≈OPT) and sits *below the estimator's resolution*.
> The worst-case threshold over-accepts (and a better tester then follows bad
> advice); the recalibrated threshold over-rejects (the tester can't resolve good
> advice). This is the empirical face of Choo's own Ω(r/ε²) sample-complexity
> caveat, and a sharper restatement of §4: when the baseline is near-optimal, the
> safe and the optimal action coincide on *rejecting* — there is simply little for
> advice to add.

## 7. Limitations / not yet done

- **Empirical-L1 surrogate**, not the Jiao et al. tester (documented; the authors
  do the same).
- Experiments use the **few-types** regime (the calibrated regime); a sweep over
  the number of types r — showing the prefix cost grow as types diversify — would
  round out RQ3.
- Choo/BEM run inside our Known-IID harness (valid: Known-IID ≤ Random-Order, so
  their guarantees carry); a dedicated random-order sampler is optional future work.

## 8. Reproducibility

```bash
python3 tests/test_choo_bem_small.py            # 6 tests
python3 scripts/run_choo_bem.py                 # ~20 min (HK-bound); envelope + RQ3
python3 scripts/run_recalibration.py            # ~1.5 min (N=1200); §6 recalibration
```
Seed 0/1/2; outputs `results/choo_bem.{json,*.png}` and
`results/recalibration.{json,*.png}`. Runtime is dominated by NetworkX
Hopcroft–Karp (one OPT + one advice-matching per trial); a faster max-matching
(SciPy LAP / numba) would cut it substantially.
