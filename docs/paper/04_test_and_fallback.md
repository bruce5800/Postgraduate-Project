<!--
Draft §5 — test-and-fallback in depth (C4). Numbers from scripts/run_choo_bem.py,
run_recalibration.py, tests/test_combiner_small.py (docs/PHASE3C_REPORT.md, UNIFIED_BENCHMARK.md §3).
Figures: choo_bem_envelope.png (Fig 3), choo_bem_prefix.png (Fig 4), recalibration_*.png.
Guardrails: empirical-L1 surrogate (already flagged in §2); combiner benchmarked not claimed.
This section is the EMPIRICAL bridge to §7 — §5.3's resolution limit is what §7 proves is necessary.
-->

# 5. Test-and-Fallback in Depth

The test-and-fallback algorithms are the paper's adaptive robustness mechanism, and the
object of the theory in Section 7. This section gives their first empirical study: the
robustness envelope they achieve, a counter-intuitive failure of the acceptance threshold,
its recalibration, and the resolution limit that recalibration exposes — the empirical
face of the impossibility we prove in Section 7. Throughout, the $\ell_1$ test is the
empirical-$\ell_1$ proof-of-concept the original authors also fall back to (Section 2.2).

## 5.1 The robustness envelope

We sweep advice error $\ell_1(p,q)$ on few-types instances ($n=2000$, $r=8$, prefix
$k=200$, 40 trials) and compare blind FollowPrediction, TestAndMatch (Choo and BEM
variants), and the Ranking floor (**Figure 3**). The picture is textbook.
FollowPrediction degrades *linearly*, from $1.000$ at perfect advice to $0.453$ at
$\ell_1\!\approx\!1.1$ — well *below* the advice-free floor ($\approx 0.99$). TestAndMatch
instead stays on the **upper envelope**: it captures the benefit when advice is good and,
when advice is bad, its prefix test rejects it and it falls back to Ranking, never
crashing (BEM $0.998\to0.969$; Choo $1.000\to0.991$ across the same sweep). This is the
adaptive counterpart of the structural robustness of Section 3: the engineered mechanism
that MPD lacked.

## 5.2 A threshold that is too lenient on average-case inputs

What does the "test then maybe fall back" machinery cost, and does a better test make a
better decision? We sweep the prefix (testing) size $k$ at *borderline* advice
($\eta=0.15$, true $\ell_1\!\approx\!0.16$) — the regime where the test must work hardest
(**Figure 4**). Counter-intuitively, **a larger, more accurate test makes the *worse*
decision**: as $k$ grows $25\to100\to200\to800$, the ratio *falls* $0.992\to0.981\to
0.969\to0.956$ and the misjudgement rate (against an empirical oracle: should we have
followed, given that following actually underperformed the baseline here?) *rises*
$0.00\to0.13\to0.33\to0.60$.

The mechanism is a real and reportable finding. The Choo/BEM acceptance threshold $\tau$
is calibrated to the *worst-case* baseline $\beta\approx0.696$. But on these average-case
instances the baseline is $\approx0.99$ (Section 3, F3), so the *empirical* break-even —
the advice error at which following stops beating the baseline — sits at $\ell_1\approx0$,
far below $\tau$. A small, noisy prefix over-estimates $\ell_1$ and *accidentally rejects*
the borderline advice, landing on the strong Ranking floor; a large, accurate prefix
correctly measures $\ell_1\approx0.16<\tau$ and so **accepts** the mildly-bad advice the
worst-case threshold deems acceptable — and underperforms the baseline. On strong-baseline
inputs the worst-case-calibrated threshold is too *lenient*, and improving the test's
accuracy only makes the algorithm follow that miscalibrated threshold more faithfully.

## 5.3 Recalibration, and the resolution limit it exposes

The natural fix is to recalibrate $\tau$ to the *measured* baseline $\hat\beta$ (the mean
empirical Ranking ratio on a small calibration sample) rather than the worst-case $\beta$.
On the same instances this eliminates the pathology: at borderline advice the worst-case
threshold's misjudgement climbs $0.03\to1.00$ as the prefix grows and its ratio drops to
$0.920$, whereas the recalibrated threshold holds misjudgement $=0.00$ at every prefix size
and ratio $\approx0.986$ — a larger prefix no longer hurts.

But recalibration exposes a deeper, honest limit. At *perfect* advice ($\ell_1=0$) the
worst-case threshold scores $1.000$ (it accepts and follows), while the recalibrated one
scores only $0.987$: the recalibrated threshold $\tau\approx 2(1-\hat\beta)\approx 0.028$ is
*smaller than the empirical-$\ell_1$ estimator's own noise floor* ($\approx 0.05$–$0.13$ at
this prefix and support), so the test can never confidently *accept* — it rejects
everything, including perfect advice, and effectively always plays the baseline. In other
words:

> On strong-baseline instances, no practical empirical-$\ell_1$ threshold can both capture
> the consistency upside and stay safe: the upside is tiny (the baseline is already
> $\approx\mathrm{OPT}$) and sits *below the estimator's resolution*. The worst-case
> threshold over-accepts (§5.2); the recalibrated threshold over-rejects; and a better
> tester only follows whichever threshold more faithfully.

This is exactly the phenomenon Section 7 proves is unavoidable — there, for *any* test on a
sublinear prefix, not only the empirical-$\ell_1$ threshold. Section 5 is its empirical
shadow; Section 7 is the theorem.

## 5.4 The dynamic combiner is dominated, and shows why matching needs test-then-commit

Finally we benchmark the Chłędowski-style dynamic combiner (Section 2.2) to contextualize
the *commit-once* structure of test-and-fallback. In its intended robust tuning the
combiner sits exactly on the floor ($0.990$ across all advice quality on few-types): it
never crashes, but captures *none* of the consistency upside — strictly dominated by
TestAndMatch on the good-advice side and equal to it on the bad side.

More instructively, an *eager* combiner that switches experts mid-stream reveals a penalty
specific to irrevocable problems. With perfect advice, eager switching scores $0.927$ —
*below both* the pure follower ($1.000$) and the pure baseline ($0.958$; verified in
`tests/test_combiner_small.py`) — because switching from Ranking to Mimic mid-run lands the
committed matching in an *incompatible hybrid*: the Mimic plan's slots are already
half-consumed by the Ranking phase, and the Ranking progress is abandoned. In an
irrevocable problem the follow/fallback decision must be made *before* the bulk of the
commitments, not adapted across them — which is precisely why Choo/BEM test on a prefix and
then *commit*, rather than switching dynamically as the caching-style combiner does. The
dynamic combiner that is cheap worst-case insurance for caching does not port cleanly to
matching, and the unified benchmark shows why.
