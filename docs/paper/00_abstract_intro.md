<!--
Draft §Abstract + §1 of the combined paper (markdown; LaTeX template later).
Honesty guardrails kept: order-error credits ACI; serving = case study; combiner =
benchmarked baseline, not claimed; theory scope stated (r=Θ(n)); T1 written as the
intended claim — the PROOF is to be finalized + advisor-signed before submission
(see the [PROOF PENDING] note in §1 and docs/T1_*).
-->

# The Limits of Predictions for Online Bipartite Matching: A Unified Experimental Study and an Impossibility Theorem

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
is precisely that they never do. We then prove that this wall is *necessary*. For the
test-and-fallback class, no algorithm whose test inspects only a sublinear prefix can be
simultaneously $(1-o(1))$-consistent and robust on strong-baseline instances, because
the structure that makes the prefix distribution-test statistically feasible is exactly
the structure that makes the baseline near-optimal. The proof reduces safe advice-use to
*tolerant* distribution testing and invokes its near-linear sample-complexity barrier.
Experiments and theory together deliver one message: **where you can test the advice, you
do not need it.**

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

**Why the wall is necessary.** The empirical wall is not an artifact of a particular
generator or algorithm; it is forced. Our main theoretical contribution (Section 7) is an
impossibility theorem for the test-and-fallback class. Informally:

> On strong-baseline instances, no test-and-fallback algorithm whose test inspects only a
> sublinear prefix of the arrivals can be simultaneously $(1-o(1))$-consistent and robust.

The reason is a coupling between *testability* and *baseline strength*. To decide safely
whether to follow the advice, the algorithm must, from its prefix, distinguish advice that
is *close enough to help* from advice that is *far enough to hurt* — a **tolerant**
distribution-testing problem, provably harder than ordinary testing, requiring nearly as
many samples as the support has types (Θ̃(n/\log n) [CJKL22], versus √n for the
non-tolerant version). But the prefix is statistically informative only when the type
distribution has few, high-count types — and that is exactly the regime in which the
advice-free baseline is already near-optimal, leaving nothing to test *for*. Where the
baseline is weak enough that advice could help, the support is large, each type is seen
$O(1)$ times, and no sublinear prefix can run the test. The proof makes this precise via a
master consistency/robustness inequality and a reduction that holds for *any* decision
rule on the prefix — not merely the empirical-distance threshold used in practice — so it
is a genuine information-theoretic impossibility rather than a comment on one algorithm.
<!-- [PROOF PENDING] T1 is stated here as the intended claim; the full proof is complete
in skeleton with the core lemma rigorous, the single-cell and affine-conversion steps
verified, and the tolerant-testing lower bound cited (docs/T1_*). One routine step
(the witness-instance match) and an advisor pass remain before final typesetting. -->

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
- **(C5) The impossibility theorem.** No sublinear-test test-and-fallback is both
  consistent and robust on strong-baseline matching, via a reduction to tolerant
  distribution testing; the testability ⟺ baseline-strength coupling is the crux (Section
  7).

The experiments and the theorem are two views of one fact. The experiments discover a wall
— predictions buy insurance, not performance; the theorem proves the wall is necessary for
any algorithm that verifies its advice on a sublinear prefix. We adopt an AI-inference
serving instantiation as a running application case study (Section 8) rather than a novelty
claim, and we are careful throughout to credit the prior results our findings build on and
to state the scope of each claim.
