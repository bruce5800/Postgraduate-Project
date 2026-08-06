<!--
Draft §8 (serving case study, DEMOTED) + §9 (related work, lean, non-redundant with
§1/§2/§7) + §10 (limitations & conclusion). Sources: docs/PHASE4_SERVING_REPORT.md,
SERVING_SLO_PROBE.md, LITERATURE_REVIEW.md. Guardrails: serving = case study, NOT a
novelty claim; the SLO probe negative is stated honestly; limitations complete.
-->

# 8. Application Case Study: AI-Inference Serving

To show the framework instantiates a contemporary problem, we cast request routing in an
AI-inference serving system as online $b$-matching: resources are model replicas / cache
shards with a capacity $c$, arrivals are requests drawn from a (non-uniform, bursty)
traffic distribution, an edge is a capability or cache affinity, and goodput is the
competitive ratio against the $b$-matching optimum. We instantiate it on three real traces
(Wikipedia pageviews, an Azure LLM inference trace, and the Mooncake prefix-cache trace)
and across four serving concerns: capacity $c$, stale traffic forecasts, dynamic service
times, and prefix-cache-aware routing.

We present this as a **case study, not a novelty claim** — the systems facts we recover are
established, and the "with-predictions" vocabulary is a re-labeling of them. The framework
does reproduce them cleanly: capacity is a *substitute* for algorithmic robustness (blind
trust in a forecast degrades further as capacity grows, while a capacity-aware baseline
stays safe); a live-load signal beats a stale forecast under dynamic service times; and a
*stable* cache-affinity router beats a reactive one — the reverse of the traffic-forecast
case. Because the literature (§9) suggested the with-predictions lens might yield a *new*
actionable serving result on a tail objective, we probed it: on an SLO/tail objective under
bursty load, a non-predictive policy (static headroom or reactive-adaptive reservation)
matches a clairvoyant oracle to within $\le 3\%$ across every regime we swept
(`docs/SERVING_SLO_PROBE.md`). We found no regime where foresight helps — the tail objective
is forgiving too, a third face of the paper's wall. Serving therefore stays a case study.

# 9. Related Work

Algorithm attributions are given where each algorithm is introduced (§2), and the
positioning of our budget–stakes law against prior testing and tradeoff results is in §7;
here we place the remaining landscape.

**Learning-augmented algorithms.** The consistency/robustness framework originates with
competitive caching with predictions [LV18] and the optimal-tradeoff analyses that followed
[WZ20]; our thesis — that on average-case matching the value is robustness, not consistency
— is a same-spirit but problem-specific statement, made quantitative and then proven
necessary. The direct experimental-study template is Chłędowski et al. [Chl21] in caching,
whose blind-follow-with-switching combiner we benchmark (§5.5); the switching genre
extends to prediction-quality-triggered frameworks such as SemiTrust-and-Switch [ASSS25],
and distributional advice of unknown quality is handled by hedging in ski rental [CD26]
and in Diakonikolas et al.'s sampling-access model — none of these tests the payoff, and
none commits once. The most closely related active line is the *test-before-trust*
program of Choo, Gouleakis and coauthors [Choo24, BCJG25], which statistically validates
advice before use — always by distributional distance; our §5.4/§7.7 argue the
decision-relevant statistic is the payoff instead.

**Algorithm selection and sequential testing.** Choosing between two policies from
samples at gap $g$ costs $O(1/g^2)$ observations by uniform convergence — the classical
engine of data-driven algorithm selection [GR17, Bal20] and, earlier, of sequential
analysis [Wald47]. The delta here is not that engine: in those settings each sample is a
whole instance whose performance is directly observable, whereas a prefix of a *single*
matching instance does not, in general, reveal a policy's full-horizon value. The payoff
identity (Lemma 2) is the structural fact that makes it observable per-arrival on the
hard family, and the bootstrap calibration of §5.4 is what survives of it on benchmark
instances with capacity kinks.

**Online matching with predictions.** MinPredictedDegree [ACI22] and the test-and-fallback
schemes [Choo24, BEM26] are the algorithms we unify and, for the latter, bound; each was
previously studied in isolation. Borodin et al. [Bor18] is the advice-free experimental
foundation our benchmark extends.

**Distribution testing.** Tolerant identity testing [CJKL22, VV11] and $\ell_1$-distance
estimation [JHW18] enter our story as the explanation of why the field's
empirical-$\ell_1$ acceptance rules are blind at sublinear prefixes — the near-linear
$\tilde\Theta(r/\log r)$ price of tolerance is real. Our budget–stakes law shows the
follow/fallback *decision* nonetheless escapes that barrier: its decision-relevant
statistic is the payoff, not the distance (§7.7), which is why our lower bound is a
Hellinger computation rather than a testing reduction.

**Serving systems.** The systems results our §8 case study recovers are established across
Preble, Mooncake, SageServe, and related work; we use them as ground truth, not as
contributions.

# 10. Limitations and Conclusion

**Limitations.** (i) We work in the known-i.i.d. model; since Known-IID $\le$ Random-Order,
the algorithms' guarantees carry, but our empirical wall is an average-case statement and
we do not claim it for adversarial arrival order. (ii) Following the original authors, the
test-and-fallback experiments use an empirical-$\ell_1$ surrogate for the (unimplemented)
distribution tester; the theory does *not* inherit this modeling — the law binds any
rule — and §7.7 separately explains the surrogate's blindness. (iii) The degree- and
histogram-prediction families do not map onto every graph, which is why we report them in
parallel panels rather than one table. (iv) Each real modality is exercised by one trace.
(v) The budget–stakes law is proven on decomposable (disjoint-cell) families, where the
payoff identity holds; whether a *non*-decomposable family can push the budget above
$1/\delta^2$ is open, as is the novelty of payoff-estimating acceptance rules relative to
the broader learning-augmented literature (a dedicated pass is in progress). An earlier
draft claimed a tolerant-testing impossibility for any sublinear rule; that claim was
refuted during its own witness step and the refutation is reported in §7.7.

**Conclusion.** We gave the first unified experimental study of learning-augmented online
bipartite matching — advice-free baselines, MinPredictedDegree and its augmentations, and
the test-and-fallback algorithms — on one harness, with confidence intervals, across
synthetic graphs, six real graphs, and real traces. Across every setting the same wall
appears: the advice-free baseline is already near-optimal, unguarded prediction-following
crashes below it, and the value of the sophisticated algorithms is downside protection,
delivered by structural or adaptive robustness with distinct trade-offs. We then priced
the wall for the test-and-fallback class with a two-sided budget–stakes law: the
follow/fallback decision costs a prefix of $\tilde\Theta(\sigma^2/g^2)$ — baseline slack
over squared stakes — for *any*
decision rule, an explicit directional test achieves it (implemented and benchmarked, it
avoids both threshold pathologies, §5.4), and — because stakes are capped
by the baseline slack — on strong-baseline instances the price exceeds the horizon:
upsides below $\Theta(\sqrt{(1-\rho_{\mathrm{base}})/n})$ are uncapturable at any feasible
prefix. Experiments discover the wall; theory sends the bill. The practical message is a
single sentence — **on average-case matching, the advice's upside is smaller than the
price of finding out whether to trust it** — with one constructive corollary for
algorithm designers: *test the payoff, not the prediction* (the payoff is a per-sample
observable where the distance is not). Progress on predictions for online matching will
come from the regimes this paper brackets: adversarial or non-stationary arrivals, and
objectives (tail, fairness, cost) where the advice-free baseline is genuinely far from
optimal.
