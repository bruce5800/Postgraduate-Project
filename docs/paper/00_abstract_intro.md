<!--
Draft §Abstract + §1 of the combined paper (markdown; LaTeX template later).
Honesty guardrails kept: order-error credits ACI; serving = case study; combiner =
benchmarked baseline, not claimed; theory = the budget–stakes law (REVISED 2026-07-27:
the witness step refuted the earlier tolerant-testing impossibility — see
docs/T1_WITNESS_GAP.md and §7). Advisor pass + a novelty pass on payoff-estimating
acceptance rules remain before submission.
-->

# The Limits of Predictions for Online Bipartite Matching: A Unified Experimental Study and a Budget–Stakes Law

## Abstract

Learning-augmented ("with-predictions") algorithms for online bipartite matching have
proliferated: MinPredictedDegree consumes a per-node degree predictor, and a family of
*test-and-fallback* schemes tests a type-histogram prediction on a sublinear prefix of
the arrivals before committing to follow it or to fall back on an advice-free baseline.
These algorithms have been analyzed in isolation — on different input models, against
different error models, and largely in theory. We give the first unified experimental
study, placing all of them on a single harness with a common structured
prediction-error model, a common optimum, and confidence intervals, across synthetic
graphs, six real-world graphs, and real request traces. Our central finding is that, on
average-case (known-i.i.d.) inputs, the value of predictions is **robustness insurance,
not a performance lever**: the advice-free baseline is already near-optimal, so the
*consistency* upside of good advice is small, whereas unguarded prediction-following can
crash far below the baseline — and the practical worth of the sophisticated algorithms
is precisely that they never do. We then prove what the wall *costs*. For the
test-and-fallback class we establish a sharp, two-sided **budget–stakes law**: deciding
whether to follow the advice requires — and, via an explicit one-line rule, only
requires — a prefix of length $\tilde\Theta(\theta/\delta^2)$, the inverse square of the
stakes $\delta$ (what good advice gains over the baseline) scaled by the contention
$\theta$, independent of the instance length. The lower half binds *every* decision rule;
the upper half refutes the natural conjecture that the hardness of tolerant distribution
testing blocks all sublinear rules — the decision-relevant statistic is the *payoff* of
following, which is exponentially cheaper to test than the prediction's distance. Because
the stakes are capped by the baseline slack, on strong-baseline instances the price
exceeds the horizon: upsides below $\approx\sqrt{(1-\rho_{\mathrm{base}})/n}$ are
uncapturable by any rule at any prefix length, and the upsides we measure sit in that
range. Experiments and theory deliver one message: **on average-case matching, the
advice's upside is smaller than the price of finding out whether to trust it.**

---

## 1. Introduction

Online bipartite matching is the canonical model of irrevocable sequential allocation:
offline resources are known in advance, requests arrive one at a time, and each request
must be matched to an available neighbor — or dropped — immediately and irrevocably,
before the rest of the input is seen. It underlies ad allocation, ride-hailing dispatch,
organ exchange, and request routing in serving systems. Classical online algorithms —
Greedy, KVV Ranking [KVV90], and the stochastic-matching algorithms of Feldman et al.
[FMMM09] and Jaillet–Lu [JL14] — are analyzed through the worst-case competitive ratio.

A now-large body of work augments these algorithms with a *prediction* about the input
and asks for two guarantees at once: **consistency** (near-optimal performance when the
prediction is good) and **robustness** (no worse than an advice-free baseline when the
prediction is arbitrarily bad) [LV18, WZ20]. For online matching specifically, two
strands have emerged. MinPredictedDegree (MPD) [ACI22] matches each arrival to its
available neighbor of minimum *predicted* degree, protecting scarce resources; it is
robust by construction (a useless predictor reduces it to Ranking). A second strand — the
*test-and-fallback* algorithms of Choo et al. [Choo24] and Burathep–Erlebach–Moses
[BEM26] — is explicitly adaptive: it Mimics a type-histogram prediction on a sublinear
prefix of arrivals, tests whether the observed arrivals match the prediction, and then
either continues to follow it or falls back to Ranking.

These algorithms have been studied *in isolation* — each on its own input family,
against its own error model, and largely through worst-case theory. As a result, three
basic questions have no empirical answer. How do the algorithms actually compare, head to
head, under one prediction-error model? How much does a prediction help, and at what
cost, on realistic inputs? And — most importantly — *why* does the practical experience
with these algorithms feel so different from their worst-case promise? This paper answers
all three, with a unified experimental study and a theorem that explains what the study
finds.

**A unified experimental study.** We place the advice-free baselines, the MPD family (and
its Feldman/Jaillet–Lu augmentations), and the test-and-fallback algorithms on a single
harness: common graph families, a common structured prediction-error model, a common
optimum computed by Hopcroft–Karp, and 95% confidence intervals throughout. We also
port the blind-follow-with-switching *combiner* of Chłędowski et al. [Chl21] — the
"cheap worst-case insurance" from the caching literature — and benchmark it (we do not
claim it as new). The study runs across synthetic graphs spanning the difficulty range,
six real-world graphs from the Network Repository, and real request traces.

**The empirical wall.** Across every setting we observe the same phenomenon, which we
state as the paper's organizing thesis: *on average-case inputs the value of predictions
is robustness insurance, not a performance lever.* Concretely (Section 3): the advice-free
Ranking is already within a percent or two of the optimum, so the consistency upside of
even perfect advice is small; unguarded prediction-following (blind Mimic, or MPD under
adversarial predictions) crashes *below* the advice-free floor; and the entire practical
value of the sophisticated algorithms is that they refuse to crash. Two distinct
mechanisms deliver this — the structural robustness of the MPD-augmentations and the
adaptive robustness of test-and-fallback — with different consistency/robustness
trade-offs. We confirm the wall on the six real graphs and on real traces, where a cheap,
non-ML historical predictor captures a meaningful fraction of the (small) oracle gap
while never dropping below the baseline (Section 6). We also report a negative result: because
MPD depends on its predictor only through the induced *order*, one might train the
predictor with an order-aware loss instead of regression, but on realistic features the
two coincide — reinforcing that the predictor, once order-faithful, is not the bottleneck.

**Why the wall is necessary — and what it costs.** The empirical wall is not an artifact
of a particular generator or algorithm; it has a price tag. Our main theoretical
contribution (Section 7) is a two-sided **budget–stakes law** for the test-and-fallback
class. Informally:

> Deciding whether to follow the advice costs a prefix of length
> $k^* = \tilde\Theta(\theta/\delta^2)$ — the inverse square of the stakes $\delta$ (what
> good advice gains over the baseline), scaled by the contention $\theta$. Below $k^*$,
> *no* decision rule is simultaneously consistent and robust; at $k^*$, an explicit
> one-line rule is.

The lower half is information-theoretic — it binds *any* measurable rule on the prefix,
not merely the empirical-distance threshold used in practice — via a master
consistency/robustness inequality and a Hellinger computation. The upper half is a
**directional test**: classify each prefix arrival as agreeing or disagreeing with the
advice's local prediction, and follow iff agreements win. Its analysis rests on a *payoff
identity* — on the hard family, the advantage of following is exactly half the mean of a
per-sample observable — which also refutes the tempting stronger conjecture (and an
earlier version of our own claim) that tolerant-testing hardness [CJKL22] makes the
decision impossible for every sublinear rule: the advice's *distance* to the truth is
indeed hard to test, and the field's empirical-$\ell_1$ thresholds are provably blind at
sublinear prefixes, but the decision-relevant *payoff* is not. The wall then re-emerges
exactly where the experiments live: stakes are capped by the baseline slack
($\delta \le 2\varepsilon(1-\rho_{\mathrm{base}})$), so on strong-baseline instances the
budget $k^*$ exceeds the horizon itself — every upside below
$\Theta(\sqrt{(1-\rho_{\mathrm{base}})/n})$ is uncapturable at *any* feasible prefix, and
the upsides measured in Sections 3–6 sit in that range.
<!-- [PROOF STATUS] Both halves are elementary (Bernstein upper; Hellinger + master
inequality lower) and are stated with proofs/sketches in §7; numerical verification in
scripts/verify_witness_gap.py. The earlier tolerant-testing impossibility was refuted
during its own witness step (docs/T1_WITNESS_GAP.md) — the refutation is reported
honestly in §7.7. Remaining before submission: advisor pass; literature pass on
payoff-estimating acceptance rules. -->

**Contributions.**
- **(C1) The first unified benchmark** of learning-augmented online-matching algorithms —
  advice-free baselines, the MPD family, and the test-and-fallback schemes — on one
  harness with a common error model, a common optimum, and confidence intervals
  (Section 3).
- **(C2) The robustness-insurance characterization.** Unguarded followers crash below the
  advice-free floor; two mechanisms (structural and adaptive) restore safety with distinct
  trade-offs; the consistency upside is small on average-case inputs, so the value is
  downside protection. Validated on synthetic graphs, six real graphs, and real traces
  (Sections 3, 6).
- **(C3) An empirical engagement with the order-error theory.** MPD's loss is governed by a
  Kendall-τ order error onto which several error models collapse; we characterize the
  tightness and saturation of the known $n{-}\mathrm{LIS}$ bound [ACI22, App. D] rather than
  re-deriving order-dependence (Section 4).
- **(C4) The first empirical study of test-and-fallback**, including a threshold-calibration
  pathology (a more accurate test can make a worse decision), its recalibration and
  resolution limit, and a benchmark of the dynamic combiner exhibiting an
  irrevocability penalty that explains why matching needs *test-then-commit* (Section 5).
- **(C5) The budget–stakes law.** A sharp two-sided law for test-and-fallback: the
  follow/fallback decision costs a prefix of $\tilde\Theta(\theta/\delta^2)$ for *any*
  rule (lower bound), and an explicit directional test achieves it (upper bound). A
  payoff identity separates cheap payoff-testing from provably hard distance-testing —
  refuting, and reporting honestly, the natural tolerant-testing impossibility — and the
  corollary quantifies the wall: on strong-baseline instances, upsides below
  $\Theta(\sqrt{(1-\rho_{\mathrm{base}})/n})$ are uncapturable at any prefix length
  (Section 7).

The experiments and the law are two views of one fact. The experiments discover a wall —
predictions buy insurance, not performance; the law prices the wall — verifying advice
costs the inverse square of its stakes, and average-case stakes cannot cover the bill. We adopt an AI-inference
serving instantiation as a running application case study (Section 8) rather than a novelty
claim, and we are careful throughout to credit the prior results our findings build on and
to state the scope of each claim.
