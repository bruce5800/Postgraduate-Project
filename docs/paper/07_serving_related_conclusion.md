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
positioning of our lower bound against prior testing and tradeoff results is in §7.1; here
we place the remaining landscape.

**Learning-augmented algorithms.** The consistency/robustness framework originates with
competitive caching with predictions [LV18] and the optimal-tradeoff analyses that followed
[WZ20]; our thesis — that on average-case matching the value is robustness, not consistency
— is a same-spirit but problem-specific statement, made quantitative and then proven
necessary. The direct experimental-study template is Chłędowski et al. [Chl21] in caching,
whose blind-follow-with-switching combiner we benchmark (§5.4).

**Online matching with predictions.** MinPredictedDegree [ACI22] and the test-and-fallback
schemes [Choo24, BEM26] are the algorithms we unify and, for the latter, bound; each was
previously studied in isolation. Borodin et al. [Bor18] is the advice-free experimental
foundation our benchmark extends.

**Distribution testing.** Our impossibility invokes the sample-complexity of tolerant
identity testing [CJKL22, VV11] and $\ell_1$-distance estimation [JHW18]; the surprising
near-linear $\tilde\Theta(r/\log r)$ cost of tolerance (versus $\sqrt r$ for testing) is
exactly what separates "can verify the advice" from "cannot."

**Serving systems.** The systems results our §8 case study recovers are established across
Preble, Mooncake, SageServe, and related work; we use them as ground truth, not as
contributions.

# 10. Limitations and Conclusion

**Limitations.** (i) We work in the known-i.i.d. model; since Known-IID $\le$ Random-Order,
the algorithms' guarantees carry, but our empirical wall is an average-case statement and
we do not claim it for adversarial arrival order. (ii) Following the original authors, the
test-and-fallback experiments use an empirical-$\ell_1$ surrogate for the (unimplemented)
distribution tester; the theorem inherits this modeling of the test. (iii) The degree- and
histogram-prediction families do not map onto every graph, which is why we report them in
parallel panels rather than one table. (iv) Each real modality is exercised by one trace.
(v) The impossibility theorem is strong-form in the $r=\Theta(n)$ regime — the regime with
an upside to contest — and one routine step of its proof (the witness-instance match) plus a
final review remain before it is fully typeset; a version biting at constant $r$ is open.

**Conclusion.** We gave the first unified experimental study of learning-augmented online
bipartite matching — advice-free baselines, MinPredictedDegree and its augmentations, and
the test-and-fallback algorithms — on one harness, with confidence intervals, across
synthetic graphs, six real graphs, and real traces. Across every setting the same wall
appears: the advice-free baseline is already near-optimal, unguarded prediction-following
crashes below it, and the value of the sophisticated algorithms is downside protection,
delivered by structural or adaptive robustness with distinct trade-offs. We then proved the
wall is necessary for the test-and-fallback class: no algorithm whose test inspects only a
sublinear prefix can be both consistent and robust on strong-baseline instances, because the
structure that makes the prefix test feasible is the structure that makes the baseline
near-optimal. Experiments discover the wall; theory proves it must be there. The practical
message is a single sentence — **where you can test the advice, you do not need it** — and it
suggests that progress on predictions for online matching will come not from better
predictors or tests on average-case inputs, but from the regimes this paper brackets:
adversarial or non-stationary arrivals, and objectives (tail, fairness, cost) where the
advice-free baseline is genuinely far from optimal.
