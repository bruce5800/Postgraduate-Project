<!--
Thesis Ch 6 — Test-and-Fallback in Depth. Adapted from paper/04 §5 (numbers: run_choo_bem.py,
run_recalibration.py, test_combiner_small.py). Cross-refs fixed (§3→Ch4, §7→Ch9). §6.3 is the
empirical bridge to Ch 9. Figures 6.1 = envelope, 6.2 = prefix sweep.
-->

# Chapter 6. Test-and-Fallback in Depth

The test-and-fallback algorithms are the adaptive robustness mechanism of Chapter 4 and the
object of the theory in Chapter 9. This chapter gives their first empirical study: the
robustness envelope they achieve (§6.1), a counter-intuitive failure of the acceptance
threshold (§6.2), its recalibration and the resolution limit that recalibration exposes
(§6.3) — the empirical face of the impossibility we prove in Chapter 9 — and a benchmark of
the dynamic combiner that explains the *commit-once* structure (§6.4). Throughout, the
$\ell_1$ test is the empirical surrogate the original authors also fall back to (Chapter 3).

## 6.1 The robustness envelope

Sweeping advice error $\ell_1(p,q)$ on few-types instances ($n=2000$, $r=8$, prefix $k=200$,
40 trials; **Figure 6.1**), FollowPrediction degrades *linearly* from $1.000$ at perfect
advice to $0.453$ at $\ell_1\!\approx\!1.1$ — well *below* the advice-free floor
($\approx0.99$). TestAndMatch instead stays on the **upper envelope**: it captures the
benefit when advice is good and, when advice is bad, its prefix test rejects it and it falls
back to Ranking, never crashing (BEM $0.998\to0.969$; Choo $1.000\to0.991$). This is the
adaptive counterpart of the structural robustness of Chapter 4.

![The robustness envelope: blind FollowPrediction crashes below the advice-free floor as advice error grows; TestAndMatch stays on the upper envelope.](../../results/choo_bem_envelope.png){width=50%}

## 6.2 A threshold that is too lenient on average-case inputs

Sweeping the prefix (testing) size $k$ at *borderline* advice ($\eta=0.15$, true
$\ell_1\!\approx\!0.16$) — where the test works hardest (**Figure 6.2**) — a larger, more
accurate test makes the *worse* decision: as $k$ grows $25\to800$, the ratio *falls*
$0.992\to0.956$ and the misjudgement rate *rises* $0.00\to0.60$. The mechanism: the Choo/BEM
threshold $\tau$ is calibrated to the worst-case baseline $\beta\approx0.696$, but on these
instances the baseline is $\approx0.99$ (F3), so the empirical break-even sits at
$\ell_1\approx0$, far below $\tau$. A small noisy prefix over-estimates $\ell_1$ and
*accidentally rejects* the borderline advice (landing safely on the floor); a large accurate
prefix correctly measures $\ell_1\approx0.16<\tau$ and *accepts* the mildly-bad advice the
worst-case threshold deems acceptable — underperforming the baseline. On strong-baseline
inputs the worst-case threshold is too lenient, and a more accurate test only follows it more
faithfully.

![Testing cost at borderline advice: a larger, more accurate prefix test makes the *worse* decision under the worst-case-calibrated threshold.](../../results/choo_bem_prefix.png){width=50%}

## 6.3 Recalibration, and the resolution limit it exposes

Recalibrating $\tau$ to the *measured* baseline $\hat\beta$ eliminates the pathology
(**Figure 6.3**): at borderline advice the worst-case threshold's misjudgement climbs
$0.03\to1.00$ as the prefix grows and its ratio drops to $0.920$, while the recalibrated
threshold holds misjudgement $0.00$ at every prefix and ratio $\approx0.986$. But
recalibration exposes a deeper limit.
At perfect advice the worst-case threshold scores $1.000$ while the recalibrated one scores
only $0.987$: the recalibrated $\tau\approx2(1-\hat\beta)\approx0.028$ is *smaller than the
empirical-$\ell_1$ estimator's noise floor* ($\approx0.05$–$0.13$), so it can never
confidently *accept* — it rejects everything, including perfect advice, and always plays the
baseline. In short:

> On strong-baseline instances, no practical empirical-$\ell_1$ threshold can both capture
> the consistency upside and stay safe: the upside is tiny and sits *below the estimator's
> resolution*. The worst-case threshold over-accepts; the recalibrated one over-rejects; a
> better tester only follows whichever threshold more faithfully.

![Recalibration removes the threshold pathology: misjudgement holds at zero at every prefix size, versus climbing toward $1.0$ under the worst-case threshold.](../../results/recalibration_prefix.png){width=50%}

This is exactly the phenomenon Chapter 9 proves unavoidable — there, for *any* test on a
sublinear prefix, not only the empirical-$\ell_1$ threshold. This chapter is its empirical
shadow; Chapter 9 is the theorem.

## 6.4 The dynamic combiner is dominated, and shows why matching needs test-then-commit

We benchmark the Chłędowski-style dynamic combiner to contextualize the commit-once structure
of test-and-fallback. In its robust tuning the combiner sits exactly on the floor ($0.990$
across all advice quality): it never crashes but captures none of the consistency upside,
strictly dominated by TestAndMatch. More instructively, an *eager* combiner that switches
mid-stream reveals a penalty specific to irrevocable problems: with perfect advice, eager
switching scores $0.927$ — *below both* the pure follower ($1.000$) and the pure baseline
($0.958$; `tests/test_combiner_small.py`) — because switching from Ranking to
advice-following (*mimic*) mid-run
lands the committed matching in an *incompatible hybrid*. In an irrevocable problem the
follow/fallback decision must be made *before* the bulk of the commitments, which is why
Choo/BEM test a prefix and then *commit* rather than switching dynamically. The dynamic
combiner that is cheap insurance for caching does not port cleanly to matching.

## 6.5 Chapter summary

Test-and-fallback delivers the adaptive robustness envelope of §6.1, but its accept/reject
decision is fundamentally limited on strong-baseline inputs: no empirical-$\ell_1$ threshold
both captures the upside and stays safe (§6.3), and dynamic switching is dominated by
test-then-commit (§6.4). The resolution limit of §6.3 is the empirical shadow of the
impossibility theorem of Chapter 9.
