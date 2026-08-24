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
we benchmark (§2.4), the distribution-testing results behind the algorithms' tests and
the outlook of §10.2 (§2.5), and the gaps in the literature this thesis addresses (§2.6).

## 2.1 Online bipartite matching and competitive analysis

In online bipartite matching, one side of a bipartite graph (the *offline* resources) is
known in advance, while the vertices of the other side (the *online* requests) arrive one
at a time. On each arrival the algorithm sees the request's incident edges and must
either match it to a currently unmatched neighbor or leave it unmatched, **immediately and
irrevocably**. The goal is to maximize the size (or, in weighted variants, the value) of
the matching. Performance is measured by the **competitive ratio**: the ratio between the algorithm's
matching and an offline optimum on the same input, in expectation over both the random
input and the algorithm's own randomness (§3.1 fixes the precise form we report).

<!--REV
id: 2-01
role: R1 二审考官
level: 建议
kind: 定义不完整
quote: Performance is measured by the competitive ratio, the (expected) ratio between the algorithm's matching and an offline optimum
note: 括号里的 expected 没说是对什么取期望：到达序列的随机性、算法自身的随机性、还是两者。这个区别在第 3 章会变成 E[ALG]/E[OPT] 还是 E[ALG/OPT] 的选择，此处不交代，读者到第 3 章会以为换了定义。
fix: 补一句把期望的来源写明：the expectation is over both the random input and the algorithm's own randomness; Chapter 3 fixes the precise form we report。
-->

The difficulty of the problem depends entirely on the assumed *input model*:

- **Adversarial arrival order.** The requests and their order are chosen by an adversary.
  The seminal result of Karp, Vazirani and Vazirani [@kvv1990ranking] is that the randomized
  **Ranking** algorithm (fix a uniformly random priority order on the resources and match
  each request to its highest-priority available neighbor) achieves competitive ratio
  $1-1/e\approx0.632$, and that this is optimal for the adversarial model. Deterministic
  algorithms cannot beat $1/2$.
- **Random arrival order.** The graph is adversarial but the requests arrive in a uniformly
  random order; this is strictly easier than adversarial order and admits ratios above
  $1-1/e$.
- **Known-i.i.d.** Requests are drawn independently from a *known* distribution over request
  types (§2.2); this is the average-case model and the one this thesis studies.

These three models are nested in difficulty, and the direction matters throughout the
thesis: every known-i.i.d. instance is also a random-order instance, and every random-order
instance is an adversarial-order instance. A guarantee proved in a harder model therefore
holds in an easier one, but not conversely, so a bound proved for adversarial order says
nothing about how *well* an algorithm does on known-i.i.d. inputs beyond that floor.

<!--REV
id: 2-02
role: R1 二审考官
level: 必改
kind: 非标准记号
mark: designed for the harder models carry over
quote: formally, Known-I.I.D. <= Random-Order in difficulty
note: 用小于等于号连接两个模型名是圈内速记，而且方向容易读反：到底谁更难、保证往哪个方向传递。这是全文反复使用的一个论证（10.3 又出现一次），第一次出现就该讲清楚。
fix: 展开成一句话：every known i.i.d. instance is also a random-order instance, so guarantees proved in the random-order model hold in ours, but not conversely。此后全文可以直接引用这一句。
-->

## 2.2 The known-i.i.d. model

In the known-i.i.d. model there is a bipartite *type graph*: each online **type** $\ell$
has a fixed neighborhood $N(\ell)$ among the offline resources, and an instance is generated
by drawing $m$ arrivals independently from a known distribution $p$ over types. The type
graph and $p$ are known; the realized sequence is not. This models settings (ad serving,
recurring request streams) where the population of requests is statistically stable even
though individual arrivals are not.

A line of work has pushed the worst-case (over type graphs) competitive ratio above the
$1-1/e$ adversarial barrier: Feldman et al. [@feldman2009online] first beat it ($0.670$) via a
flow-based *blue/red* decomposition of a suggested matching; Manshadi, Oveis Gharan and
Saberi [@manshadi2012online] and Jaillet–Lu [@jailletlu2014online] improved the ratio (to
$\approx0.702$ and $\approx0.729$ respectively) using
LP-based and list-based online policies; subsequent work refined it further. These are the
"sophisticated" algorithms whose worst-case optimality motivates their use.

Crucially for this thesis, Borodin, Karavasilis and Pankratov [@borodin2018experimental]
conducted an experimental study of these algorithms and found that on *average-case* i.i.d.
instances the picture is very different from the worst case: the simple algorithms (Greedy,
Ranking) perform almost as well as the sophisticated ones, whose advantage is a worst-case,
not a typical-case, phenomenon.

One empirical observation in that line is the seed of this thesis: *on typical inputs the
simple baseline is already near-optimal*. Everything that follows is an attempt to find out
what a prediction can add to it, and we reproduce a subset of the study as validation
(Chapter 3).

<!--REV
id: 2-03
role: R4 体例校对
level: 建议
kind: 数字精度不一
mark: LP-based and list-based online policies
quote: first beat it (0.67) ... improved the ratio (to approximately 0.702 and approximately 0.729 respectively)
note: 同一串比较里出现两位小数的 0.67 和三位小数的 0.702 / 0.729；而 3.6 又把同样两个界写成 0.670 和 0.729。读者会怀疑 0.67 和 0.670 是不是同一个数。
fix: 全文统一到三位小数，并在首次出现处标明这些是最坏情况保证（相对于 3.6 的实测值）。
-->

<!--REV
id: 2-04
role: R6 初次读者
level: 建议
kind: 读者定位
quote: This empirical observation - that on typical inputs the simple baseline is already near-optimal - is the seed of the thesis's central finding
note: 这句是全章最重要的一句（它是整篇论文的种子），却排在 2.2 的末尾、和一堆比值罗列挤在同一段。第一次读的人很可能滑过去。
fix: 单独成段，并在句首点明它的地位：One experimental finding in this line is the seed of this thesis。让读者在背景章就记住这一句。
-->

## 2.3 Learning-augmented algorithms

The **algorithms-with-predictions** (or *learning-augmented*) paradigm, surveyed in
[@mitzenmacher2020algorithms], equips an online algorithm with a prediction about the unknown input and asks for
two guarantees simultaneously:

- **Consistency:** near-optimal performance when the prediction is accurate;
- **Robustness:** performance no worse than a prediction-free guarantee when the prediction
  is arbitrarily wrong.

The paradigm was crystallized by Lykouris and Vassilvitskii [@lykouris2018caching] for competitive caching,
who showed how to interpolate between trusting and ignoring a predictor while bounding both
consistency and robustness. A large literature followed across ski rental, scheduling and other online problems,
including the *optimal* consistency/robustness trade-off analyses of Wei and Zhang
[@weizhang2020tradeoffs], which establish problem-intrinsic Pareto frontiers between the two
objectives. Recent work further analyzes how the achievable ratio degrades *continuously*
with prediction accuracy in a distributionally-robust formulation [@yoshinaga2026accuracy],
complementing the discrete consistency/robustness endpoints used here.

Two items from this literature are load-bearing for us. The recurring mechanism is
*hedging*: combining the prediction with a safe default so that a bad prediction cannot
cause catastrophe. The blind-follow-with-switching **combiner** of Chłędowski, Polak,
Szabucki and Żołna [@chledowski2021caching] is one such mechanism, which we port and
benchmark (Chapter 6); their paper, an experimental study of robust learning-augmented
caching, is also the closest methodological template for this thesis's experimental half.

<!--REV
id: 2-05
role: R6 初次读者
level: 建议
kind: 单段承载过多
quote: The paradigm was crystallized by Lykouris and Vassilvitskii ... Wei and Zhang ... the combiner of Chledowski ... Yoshinaga
note: 2.3 是一整段 14 行，串了范式定义、缓存起源、最优权衡、combiner、连续退化五条线索，每条一到两句。读者读完记不住哪条与本文有关。
fix: 拆成三段：范式与两个保证；权衡的理论结果；本文实际会用到的两样东西（combiner 在第 6 章被基准化、连续退化作为对照）。与本文无关的引文压成一句。
-->

## 2.4 Predictions for online bipartite matching

Two strands apply the with-predictions paradigm to online matching, differing in the
*prediction object* they consume.

**Degree predictions: MinPredictedDegree.** Aamand, Chen and Indyk [@aci2022mpd] propose
**MinPredictedDegree (MPD)**: given a prediction $\mu$ of each offline resource's degree
(how contended it will be), match each arrival to its available neighbor of *minimum
predicted degree*, i.e. protect the resources predicted to be rarest. MPD is robust by
construction: a constant (useless) predictor reduces it to Ranking. A key structural fact,
which the thesis engages in Chapter 5, is that MPD depends on $\mu$ *only through the order
it induces*. The authors' Appendix D bounds the matching loss by an order quantity built in
two steps: list the true degrees in the order the prediction suggests, then count how many
of them are out of place: formally $n-\mathrm{LIS}$, where $\mathrm{LIS}$ is the length of
the longest non-decreasing subsequence of that list. The count is zero exactly when the
prediction gets the order right, so a monotone (order-preserving) prediction incurs zero
loss.

<!--REV
id: 2-06
role: R1 二审考官
level: 必改
kind: 定义嵌套过深
mark: the number of resources not in the longest non-decreasing subsequence
quote: n - LIS, the number of resources not in the longest non-decreasing subsequence of the true degrees ordered by the prediction
note: 这是全文最难读的一句定义：一句话里套了三层（把真实度数按预测排序、取最长非降子序列、再取补集大小）。而它是第 5 章的主角，读者在这里没读懂，第 5 章就全废了。
fix: 改成两步走：先说怎么排（list the true degrees in the order the prediction suggests），再说量什么（count how many are out of place - formally n minus the length of the longest non-decreasing subsequence）。再加一句直觉：it is zero exactly when the prediction gets the order right。
-->

<!--REV
id: 2-07
role: R4 体例校对
level: 必改
kind: 符号复用
quote: a prediction of each offline resource's degree (how contended it will be)
note: 这里预测对象记作 mu，而 3.3 也用 mu；但 5.1 又写 p[mu]，其中 p 是真实权重——而 p 在 2.2、3.1 里已经是类型分布。同一个字母在同一篇论文里指两个不同对象，且都在讨论预测误差的语境下。
fix: 把 5.1 的真实权重换个字母（例如 w[mu]），或在 5.1 就地声明这里的 p 与类型分布无关。这一处不改，第 5 章的核心公式会被误读。
-->

**Type-histogram advice and test-and-fallback.** A second strand takes the prediction to
be a *histogram* $\hat c$ over request types (how many of each type will arrive). Choo et
al. [@choo2024imperfect] introduce **TestAndMatch**: build a matching from $\hat c$ and Mimic it, but
first spend a sublinear prefix of arrivals *testing* whether the observed type frequencies
match $\hat c$, using an $\ell_1$-distance tester adapted from Jiao, Han and Weissman
[@jiao2018l1], and fall back to Ranking if they do not. Burathep, Erlebach and Moses [@bem2026testmatch]
generalize this ("Test-and-Match+") to the random-arrival model and to imperfect knowledge
of the matching size. Both papers give *upper* bounds (algorithms); their only lower bound
(Choo et al.'s Theorem 3.1) is a generic *adversarial* indistinguishability result (no
algorithm is $1$-consistent and $>\tfrac12$-robust), and neither proves a lower bound in
the stochastic model. Notably, Choo et al.'s acceptance threshold already *couples* to the
baseline competitive ratio $\beta$, but constructively, inside the algorithm design, not
as a lower bound. What that coupling costs, i.e. how large a prefix the follow/fallback
decision fundamentally requires, is the question this thesis measures (Chapter 6) and then
reads quantitatively (§10.2).

<!--REV
id: 2-08
role: R5 答辩提问者
level: 建议
kind: 可被追问的评判
quote: their only lower bound (Choo et al.'s Theorem 3.1) is a generic adversarial indistinguishability result ... and neither proves a lower bound in the stochastic model
note: 这是全文对前人工作最强的一句评判，也是本文定位的支点。答辩时会被问：你确认读遍了他们的所有版本和附录吗。现场答不上来，整个定位就松动了。
fix: 措辞保留，但加一个可核对的限定：in the published versions we examined (arXiv vNN, DATE)。并把 8.3 文献综述的结论与这句显式挂钩，答辩时可以直接引用。
-->

<!--REV
id: 2-09
role: R5 答辩提问者
level: 建议
kind: 反复外指
quote: the full formal development is deferred to companion work
note: 这是 companion work 在全文的第五处（另有 1.3、10.2 两处、10.3）。背景章就预告一份读者看不到的稿子，会让人怀疑本论文的完成度。
fix: 本处删掉，只说本文做到哪一步（Chapter 6 measures it; 10.2 reads the measurement quantitatively）。集中到 10.3 限制一节说明一次即可。
-->

## 2.5 Distribution testing

The test at the heart of the algorithms above is a question in **distribution testing**:
given samples from an unknown distribution $p$ over a support of size $r$ (the same $r$ as
in our model, the number of request types, because the histogram advice is a distribution
over types) and a known
reference $q$, decide how far $p$ is from $q$. We measure that distance in $\ell_1$
throughout, as the algorithms and our experiments do; it is *twice* the total-variation
distance, and every threshold quoted in this thesis is an $\ell_1$ threshold. Two regimes
must be distinguished:

- **Identity (non-tolerant) testing**, distinguishing $p=q$ from $\lVert p-q\rVert_1\ge
  \varepsilon$, has sample complexity $\Theta(\sqrt r/\varepsilon^2)$ [@paninski2008coincidence; @valiant2017automatic],
  *sublinear* in the support size.
- **Tolerant testing / distance estimation**, distinguishing $\lVert p-q\rVert_1\le
  \varepsilon_1$ from $\ge\varepsilon_2$ for $0<\varepsilon_1<\varepsilon_2$, i.e. estimate
  the distance rather than test equality, is provably *much harder*: Valiant and Valiant
  [@valiant2011unseen] showed it requires $\Theta(r/\log r)$ samples, *near-linear* in the support.
  Jiao, Han and Weissman [@jiao2018l1] gave matching bounds for $\ell_1$-distance estimation, and
  Canonne, Jain, Kamath and Li [@canonne2022tolerance] precisely characterized the whole
  $(\varepsilon_1,\varepsilon_2)$ landscape, showing that for constant tolerances the cost
  jumps to the "barely sublinear" $\tilde\Theta(r/\log r)$.

The near-quadratic gap between $\sqrt r$ (testing) and $r/\log r$ (tolerant testing)
matters twice in this thesis. It is why the deployable versions of TestAndMatch fall back
to an empirical surrogate for their tester, and it is why that surrogate is blind on large
supports: the resolution limit measured in Chapter 6. Whether the barrier also dooms
every *other* decision rule turns out to be subtler than it first appears; the concluding
outlook (§10.2) returns to this point.

<!--REV
id: 2-10
role: R2 领域审稿人
level: 必改
kind: 技术定义不精确
mark: given samples from an unknown distribution
quote: decide how far p is from q in L1 (total-variation) distance
note: L1 距离与总变差距离差一个 1/2 的因子（TV = L1/2）。本章把二者当同义词，而第 6 章的阈值、10.2 的仿射律都对这个常数敏感（例如 tau 约等于 2(1-beta)）。审稿人一定会核对。
fix: 选定一个并全文统一（建议全用 L1，因为算法和实验都是 L1），在此处明确写 we use the L1 distance throughout; it is twice the total-variation distance。然后回头检查 6.2、6.3、10.2 的每个常数。
-->

<!--REV
id: 2-11
role: R1 二审考官
level: 建议
kind: 符号跨章不一致
mark: over a support of size
quote: samples from an unknown distribution p over a support of size r
note: 这里的 r 是分布支撑大小，3.1 的 r 是请求类型数。二者在本文里恰好相等，但从没说破，读者会以为是两个不同的量碰巧同名。
fix: 加半句点明：here r is the same r as in our model - the number of request types - because the histogram advice is a distribution over types。
-->

## 2.6 Positioning of this thesis

Against this background, three gaps stand out. They correspond one-to-one to the three
questions of §1.2, and the thesis addresses them in that order:

1. **No unified empirical comparison.** The matching algorithms above were each studied in
   isolation, on their own input families and error models, and largely in theory; there is
   no head-to-head experimental benchmark under a common harness. (Chapters 4–7.)
2. **No empirical study of test-and-fallback.** The distribution test at the heart of
   [@choo2024imperfect; @bem2026testmatch] has no deployable implementation (the authors themselves fall back to an
   empirical surrogate), and its testing cost, threshold calibration, and failure modes have
   not been measured. (Chapter 6.)
3. **No quantification of what the prefix test costs.** No prior work measures, or bounds, how
   large a prefix the follow/fallback decision requires on strong-baseline instances, where the
   upside to be captured is smallest (§8.3 describes the prior-art pass behind this claim).
   (Chapter 6 empirically; §10.2 in outlook.)

The thesis closes the first two gaps experimentally and takes a first quantified step at the
third.

<!--REV
id: 2-12
role: R4 体例校对
level: 建议
kind: 三套编号不对齐
quote: Against this background, three gaps stand out
note: 本节的三个 gap、1.2 的三个研究问题、1.3 的五条贡献互相不对齐，读者要在三处之间自己配对。三套编号讲的其实是同一件事。
fix: 让 2.6 的三个 gap 与 1.2 的三个问题一一对应（同序、同措辞），贡献列表再引用这套编号。全文只维护一套骨架。
-->

<!--REV
id: 2-13
role: R2 领域审稿人
level: 建议
kind: novelty 断言
quote: No prior work measures - or bounds - how large a prefix the follow/fallback decision requires on strong-baseline instances
note: 第三个 gap 是本文最强的 novelty 断言，但这里只是陈述，没有指向支撑它的检索工作（8.3 有一次专门的先行研究检索）。
fix: 在这句后面加一个指向：(the prior-art pass behind this claim is described in 8.3)。审稿人和考官顺着这条线就能自己核对。
-->
