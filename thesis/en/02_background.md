<!--
Thesis Ch 2 — Background & Related Work (full-English thesis; Chinese translation later).
Fuller, pedagogical treatment (unlike the paper's compressed §9). Six subsections:
online matching & competitive analysis; the known-i.i.d. model; learning-augmented
algorithms; predictions for matching (the specific algorithms); distribution testing;
positioning. Citation keys align with docs/references.bib (verify names/years there).
Sources: docs/LITERATURE_REVIEW.md, paper/06 §7.1, paper/07 §9, PHASE*/T1_* docs.
-->

# Chapter 2. Background and Related Work

This chapter sets up the technical context the thesis builds on: the online
bipartite-matching problem and its input models (§2.1), the known-i.i.d. model we work in
(§2.2), the learning-augmented ("with-predictions") paradigm and its
consistency/robustness language (§2.3), the specific prediction-based matching algorithms
we benchmark and bound (§2.4), the distribution-testing results our impossibility theorem
relies on (§2.5), and the gaps in the literature this thesis addresses (§2.6).

## 2.1 Online bipartite matching and competitive analysis

In online bipartite matching, one side of a bipartite graph — the *offline* resources — is
known in advance, while the vertices of the other side — the *online* requests — arrive one
at a time. On each arrival the algorithm sees the request's incident edges and must
either match it to a currently unmatched neighbor or leave it unmatched, **immediately and
irrevocably**. The goal is to maximize the size (or, in weighted variants, the value) of
the matching. Performance is measured by the **competitive ratio**, the (expected) ratio
between the algorithm's matching and an offline optimum on the same input.

The difficulty of the problem depends entirely on the assumed *input model*:

- **Adversarial arrival order.** The requests and their order are chosen by an adversary.
  The seminal result of Karp, Vazirani and Vazirani [@kvv1990ranking] is that the randomized
  **Ranking** algorithm — fix a uniformly random priority order on the resources and match
  each request to its highest-priority available neighbor — achieves competitive ratio
  $1-1/e\approx0.632$, and that this is optimal for the adversarial model. Deterministic
  algorithms cannot beat $1/2$.
- **Random arrival order.** The graph is adversarial but the requests arrive in a uniformly
  random order; this is strictly easier than adversarial order and admits ratios above
  $1-1/e$.
- **Known-i.i.d.** Requests are drawn independently from a *known* distribution over request
  types (§2.2); this is the average-case model and the one this thesis studies.

Because the known-i.i.d. and random-order models are more benign than adversarial order —
formally, Known-I.I.D. $\le$ Random-Order in difficulty — algorithms and guarantees
designed for the harder models carry over, a fact we use throughout.

## 2.2 The known-i.i.d. model

In the known-i.i.d. model there is a bipartite *type graph*: each online **type** $\ell$
has a fixed neighborhood $N(\ell)$ among the offline resources, and an instance is generated
by drawing $m$ arrivals independently from a known distribution $p$ over types. The type
graph and $p$ are known; the realized sequence is not. This models settings — ad serving,
recurring request streams — where the population of requests is statistically stable even
though individual arrivals are not.

A line of work has pushed the worst-case (over type graphs) competitive ratio above the
$1-1/e$ adversarial barrier: Feldman et al. [@feldman2009online] first beat it ($0.67$) via a
flow-based *blue/red* decomposition of a suggested matching; Manshadi et al. and Jaillet–Lu
[@jailletlu2014online] improved the ratio (to $\approx0.702$ and $\approx0.729$ respectively) using
LP-based and list-based online policies; subsequent work refined it further. These are the
"sophisticated" algorithms whose worst-case optimality motivates their use.

Crucially for this thesis, Borodin, Karavasilis and Pankratov [@borodin2018experimental] conducted an
experimental study of these algorithms and found that on *average-case* i.i.d. instances
the picture is very different from the worst case: the simple algorithms (Greedy, Ranking)
perform almost as well as the sophisticated ones, whose advantage is a worst-case, not a
typical-case, phenomenon. This empirical observation — that on typical inputs the simple
baseline is already near-optimal — is the seed of the thesis's central finding, and we
reproduce a subset of it as validation (Chapter 3).

## 2.3 Learning-augmented algorithms

The **algorithms-with-predictions** (or *learning-augmented*) paradigm, surveyed in
[@mitzenmacher2020algorithms], equips an online algorithm with a prediction about the unknown input and asks for
two guarantees simultaneously:

- **Consistency:** near-optimal performance when the prediction is accurate;
- **Robustness:** performance no worse than a prediction-free guarantee when the prediction
  is arbitrarily wrong.

The paradigm was crystallized by Lykouris and Vassilvitskii [@lykouris2018caching] for competitive caching,
who showed how to interpolate between trusting and ignoring a predictor while bounding both
consistency and robustness. A large literature followed across ski rental, scheduling,
and other online problems, including the *optimal* consistency/robustness trade-off
analyses of Wei and Zhang [@weizhang2020tradeoffs], which establish problem-intrinsic Pareto frontiers
between the two objectives. A recurring theme is that robustness is obtained by *hedging* —
combining the predictor's advice with a safe default so that a bad prediction cannot cause
catastrophe. The blind-follow-with-switching **combiner** of Chłędowski, Polak, Szabucki
and Żołna [@chledowski2021caching], introduced in an experimental study of robust learning-augmented
caching, is one such hedging mechanism; we port and benchmark it (Chapter 6). That paper is
also the closest methodological template for this thesis's experimental half.

## 2.4 Predictions for online bipartite matching

Two strands apply the with-predictions paradigm to online matching, differing in the
*prediction object* they consume.

**Degree predictions: MinPredictedDegree.** Aamand, Chen and Indyk [@aci2022mpd] propose
**MinPredictedDegree (MPD)**: given a prediction $\mu$ of each offline resource's degree
(how contended it will be), match each arrival to its available neighbor of *minimum
predicted degree* — i.e. protect the resources predicted to be rarest. MPD is robust by
construction: a constant (useless) predictor reduces it to Ranking. A key structural fact,
which the thesis engages in Chapter 5, is that MPD depends on $\mu$ *only through the order
it induces*; the authors' Appendix D bounds the matching loss by an order quantity
($n-\mathrm{LIS}$, the number of resources not in the longest non-decreasing subsequence of
the true degrees ordered by $\mu$), and shows in particular that a monotone (order-preserving)
prediction incurs zero loss.

**Type-histogram advice and test-and-fallback.** A second strand takes the prediction to
be a *histogram* $\hat c$ over request types (how many of each type will arrive). Choo et
al. [@choo2024imperfect] introduce **TestAndMatch**: build a matching from $\hat c$ and Mimic it, but
first spend a sublinear prefix of arrivals *testing* whether the observed type frequencies
match $\hat c$ — using an $\ell_1$-distance tester adapted from Jiao, Han and Weissman
[@jiao2018l1] — and fall back to Ranking if they do not. Burathep, Erlebach and Moses [@bem2026testmatch]
generalize this ("Test-and-Match+") to the random-arrival model and to imperfect knowledge
of the matching size. Both papers give *upper* bounds (algorithms); their only lower bound
(Choo et al.'s Theorem 3.1) is a generic *adversarial* indistinguishability result (no
algorithm is $1$-consistent and $>\tfrac12$-robust), and neither proves a lower bound in
the stochastic model. Notably, Choo et al.'s acceptance threshold already *couples* to the
baseline competitive ratio $\beta$ — but constructively, inside the algorithm design, not
as an impossibility. Turning that coupling into a two-sided, algorithm-independent
impossibility is the theoretical contribution of this thesis (Chapter 9).

## 2.5 Distribution testing

The thesis's impossibility theorem reduces the problem of *safely using* histogram advice
to a question in **distribution testing**: given samples from an unknown distribution $p$
over a support of size $r$ and a known reference $q$, decide how far $p$ is from $q$ in
$\ell_1$ (total-variation) distance. Two regimes must be distinguished:

- **Identity (non-tolerant) testing** — distinguish $p=q$ from $\lVert p-q\rVert_1\ge
  \varepsilon$ — has sample complexity $\Theta(\sqrt r/\varepsilon^2)$ [@paninski2008coincidence; @valiant2017automatic],
  *sublinear* in the support size.
- **Tolerant testing / distance estimation** — distinguish $\lVert p-q\rVert_1\le
  \varepsilon_1$ from $\ge\varepsilon_2$ for $0<\varepsilon_1<\varepsilon_2$, i.e. estimate
  the distance rather than test equality — is provably *much harder*: Valiant and Valiant
  [@valiant2011unseen] showed it requires $\Theta(r/\log r)$ samples, *near-linear* in the support.
  Jiao, Han and Weissman [@jiao2018l1] gave matching bounds for $\ell_1$-distance estimation, and
  Canonne, Jain, Kamath and Li [@canonne2022tolerance] precisely characterized the whole
  $(\varepsilon_1,\varepsilon_2)$ landscape, showing that for constant tolerances the cost
  jumps to the "barely sublinear" $\tilde\Theta(r/\log r)$.

The near-quadratic gap between $\sqrt r$ (testing) and $r/\log r$ (tolerant testing) is the
technical engine of this thesis's theorem: safely following advice requires distinguishing
"close enough to help" from "far enough to hurt" — a *tolerant* test — and it is exactly
this near-linear sample cost that a sublinear prefix cannot pay. To our knowledge, the
connection between distribution-testing sample complexity and the *value of advice in an
online algorithm* has not been made before.

## 2.6 Positioning of this thesis

Against this background, three gaps stand out, which the thesis addresses in turn:

1. **No unified empirical comparison.** The matching algorithms above were each studied in
   isolation, on their own input families and error models, and largely in theory; there is
   no head-to-head experimental benchmark under a common harness. (Chapters 4–7.)
2. **No empirical study of test-and-fallback.** The distribution test at the heart of
   [@choo2024imperfect; @bem2026testmatch] has no deployable implementation (the authors themselves fall back to an
   empirical surrogate), and its testing cost, threshold calibration, and failure modes have
   not been measured. (Chapter 6.)
3. **No lower bound coupling testability to baseline strength.** No prior work proves that a
   sublinear-test algorithm cannot be both consistent and robust on strong-baseline
   instances, nor identifies the few-types structure that makes the test feasible with the
   structure that makes the baseline near-optimal. (Chapter 9.)

The thesis closes the first two gaps experimentally and the third theoretically, arriving at
a single unifying statement — *on average-case online matching, predictions are robustness
insurance rather than a performance lever, and this is necessary* — supported by experiments
across synthetic graphs, real graphs, and real traces, and by an impossibility theorem.
