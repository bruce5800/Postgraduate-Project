<!--
Draft §8 (serving case study, DEMOTED) + §9 (related work, lean, non-redundant with
§1/§2/§7) + §10 (limitations & conclusion). Sources: docs/PHASE4_SERVING_REPORT.md,
SERVING_SLO_PROBE.md, LITERATURE_REVIEW.md. Guardrails: serving = case study, NOT a
novelty claim; the SLO probe negative is stated honestly; limitations complete.
-->

# 8. Application Case Study: AI-Inference Serving

To show the framework instantiates a contemporary problem, we cast request routing in an
AI-inference serving system as online capacitated matching: resources are model replicas /
cache shards serving up to $c$ concurrent requests, arrivals are requests drawn from a
(non-uniform, bursty) traffic distribution, and an edge is a capability or cache affinity.
Two quantities must be kept apart: raw *goodput* is the fraction of arrivals served, while
the *competitive ratio* is the number served divided by the capacitated optimum on the same
realized instance; they coincide only when the optimum can serve every arrival, which under
overload it cannot, so we report the competitive ratio. We instantiate the mapping across
four serving concerns: capacity $c$ (on a synthetic topology, where advice quality can be
swept directly), stale traffic forecasts (Wikipedia pageviews), dynamic service times (an
Azure LLM inference trace), and prefix-cache-aware routing (the Mooncake prefix-cache
trace).

We present this as a **case study, not a novelty claim** — the systems facts we recover are
established, and the "with-predictions" vocabulary is a re-labeling of them. The framework
does reproduce them cleanly: capacity is a *substitute* for algorithmic robustness (blind
trust in a forecast degrades further as capacity grows, while a capacity-aware baseline
stays safe); a live-load signal beats a stale forecast under dynamic service times; and a
*stable* cache-affinity router beats a reactive one — the reverse of the traffic-forecast
case. Because the literature (§9) suggested the with-predictions lens might yield a *new*
actionable serving result on a tail objective, we probed it: on an SLO/tail objective under
bursty load, a non-predictive policy (static headroom or reactive-adaptive reservation)
comes within $\le 3\%$ of a policy with perfect foresight across every regime we swept. We found no regime where foresight helps — the tail objective
is forgiving too, a third face of the paper's wall. Serving therefore stays a case study.

<!--REV
id: 7-01
role: P5 审稿意见预演
level: 建议
kind: 重复声明
quote: We present this as a **case study, not a novelty claim** ... Serving therefore stays a case study.
note: 同一节里两次声明本节不是贡献。诚实是对的，但两次会让审稿人问：那它为什么占一节。
fix: 保留一次，并把这一节的正面价值写出来（它验证抽象能落到真实系统，并且是 §6.3 负结果的实验场）。
-->

# 9. Related Work

Algorithm attributions are given where each algorithm is introduced (§2), and the
positioning of our budget–stakes law against prior testing and tradeoff results is in §7;
here we place the remaining landscape.

**Scope of our novelty claims.** Both claims we mark as new — the budget–stakes law, and
the observation that testing the *payoff* separates from testing the prediction's distance
— rest on a targeted search rather than an exhaustive one, and we state its extent so it
can be checked. We searched the learning-augmented / algorithms-with-predictions
literature through **April 2026**, over DBLP, arXiv (cs.DS, cs.LG) and Google Scholar,
for prefix- or sample-based acceptance rules — keywords *test-before-trust*, *advice
testing*, *trust the prediction*, *test-then-commit*, *prediction validation*,
*consistency–robustness trade-off*, *tolerant testing* — and read in depth the four
nearest lines (test-before-trust; switching and combining frameworks; distributional
advice of unknown quality; data-driven algorithm selection), including the
test-before-trust group's own April-2026 survey talk of their programme. We found no
acceptance rule that estimates the payoff of following. A citation trace of every work
citing [Choo24] would be the completionist step and we have not performed it; the claims
should be read as scoped to this search.

**Learning-augmented algorithms.** The consistency/robustness framework originates with
competitive caching with predictions [LV18] and the optimal-tradeoff analyses that followed
[WZ20]; our thesis — that on average-case matching the value is robustness, not consistency
— is a same-spirit but problem-specific statement, made quantitative and then proven
necessary. The direct experimental-study template is Chłędowski et al. [Chl21] in caching,
whose blind-follow-with-switching combiner we benchmark (§5.5); the switching genre
extends to prediction-quality-triggered frameworks such as SemiTrust-and-Switch [ASSS25],
and distributional advice of unknown quality is handled by hedging in ski rental [CD26]
and in Diakonikolas et al.'s sampling-access model — among the works covered by the
search above, none tests the payoff and none commits once. The most closely related active line is the *test-before-trust*

<!--REV
id: 7-02
role: P2 领域审稿人
level: 建议
kind: 对文献的全称断言
quote: none of these tests the payoff, and none commits once
note: 对一整条文献线的全称否定。只要审稿人想到一个反例，这句话就成了扣分项——而 test-before-trust 那一线正是活跃的、且作者自己也说是直接对手。
fix: 限定到检索到的范围：among the works we surveyed (§9), none tests the payoff。并与 0-05 的范围声明挂钩。
-->
program of Choo, Gouleakis and coauthors [Choo24, BCJG25], which statistically validates
advice before use — always by distributional distance; our §5.4/§7.7 argue the
decision-relevant statistic is the payoff instead.

**Algorithm selection, best-arm identification, and sequential testing.** Choosing
between two policies from samples at gap $g$ costs $\Theta(1/g^2)$ observations — the
classical engine of sequential analysis [Wald47], of data-driven algorithm selection
[GR17, Bal20], of two-armed best-arm identification [MT04, KCG16], and of off-policy
evaluation [DLL11]. We import that engine and claim no novelty for it. The delta is the
*observation model*: in algorithm selection each sample is a whole instance with directly
observable performance; a bandit pull directly reveals the pulled arm's reward; off-policy
evaluation consumes logged actions with known propensities. Our prefix is none of these —
it is a **passive stream of arrivals**, containing no actions and no rewards of either
policy. That such a stream reveals a policy pair's full-horizon value gap at all, at rate
$\sigma^2/g^2$ and — by the law's lower half — provably no faster under *any* rule, is
the content of the payoff identity and of Theorem 1, not of the statistics; and the
bootstrap calibration of §5.4 is what survives of the identity on benchmark instances
with capacity kinks.

**Online matching with predictions.** MinPredictedDegree [ACI22] and the test-and-fallback
schemes [Choo24, BEM26] are the algorithms we unify and, for the latter, bound; each was
previously studied in isolation. Blending designs for the fractional relaxation [CJS25]
optimize the robustness–consistency Pareto frontier directly and test nothing — 
complementary to, and untouched by, the budget–stakes law, which prices the *decision to
test*. Borodin et al. [Bor18] is the advice-free experimental foundation our benchmark
extends.

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

**Limitations.** (i) The experiments are in the known-i.i.d. model. Every known-i.i.d.
instance is also a random-order instance, so guarantees proved in the random-order model
carry over to ours but not conversely; the law itself does extend to random order
(Remark, §7.8), but our empirical wall is an average-case statement and

<!--REV
id: 7-03
role: P1 领域外审稿人
level: 建议
kind: 非标准记号
mark: the algorithms' guarantees carry
quote: since Known-IID $\le$ Random-Order
note: 用小于等于号连接两个模型名是圈内速记，方向也容易读反。领域外审稿人会停顿。
fix: 展开：every known-i.i.d. instance is also a random-order instance, so guarantees proved there carry over to ours, but not conversely。
-->
we do not claim it for adversarial arrival order. (ii) Following the original authors, the
test-and-fallback experiments use an empirical-$\ell_1$ surrogate for the (unimplemented)
distribution tester; the theory does *not* inherit this modeling — the law binds any
rule — and §7.7 separately explains the surrogate's blindness. (iii) The degree- and
histogram-prediction families do not map onto every graph, which is why we report them in
parallel panels rather than one table. (iv) Each real modality is exercised by one trace.
(v) The budget–stakes law is proven on decomposable (disjoint-cell) families, where the
payoff identity holds; whether a *non*-decomposable family can push the budget above
$1/\delta^2$ is open. Our novelty claim for payoff-estimating acceptance rules rests on

<!--REV
id: 7-04
role: P4 体例校对
level: 必改
kind: 与 §7 自相矛盾
mark: whether a *non*-decomposable family
quote: as is the novelty of payoff-estimating acceptance rules ... (a dedicated pass is in progress)
note: §10 的局限说新颖性检索「正在进行中」，而 §7.8 与 §7 开头都说这次检索已经完成并给出了结论。同一篇稿子里两处直接冲突，审稿人一定会发现。
fix: 统一口径：既然 §7 说已完成，§10 这一条要么删掉，要么改成「检索已完成、结论见 §9，但覆盖面有限」。
-->
the search reported in §9: that search is complete, but bounded by the venues,
keywords and cut-off stated there, so we present the claim as scoped rather than
exhaustive. An earlier
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
