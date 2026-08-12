<!--
Draft §3 The unified benchmark (markdown; LaTeX later). Numbers are the actual run
(scripts/run_unified_benchmark.py; results/unified_benchmark_tables.md &
unified_benchmark.png). CIs are 95% half-widths (±.001–.003, tight). Guardrails:
combiner benchmarked not claimed; prediction-object heterogeneity stated openly.
Table 1 = the three panels; Figure 1 = the grouped bars.
-->

# 3. The Unified Benchmark

This section places all three algorithm families on one harness and establishes the
paper's organizing thesis. We report competitive ratios (mean $\pm$ 95% CI) as a function
of prediction quality, in three panels chosen to span the regimes each family was designed
for.

## 3.1 Design

The families consume different prediction objects, so we drive each with its own
corruption knob and present them in parallel panels (Section 2.3); the shared harness —
graphs, $\mathrm{OPT}$, CI methodology, and the advice-free floor — is what makes the
panels comparable.

- **Panel A — clvb_zipf** ($n=1000$, 60 trials): heavy-tailed offline degrees, the regime
  where degree predictions carry signal.
- **Panel B — left-regular $d{=}5$** ($n=1000$, 60 trials): near-homogeneous degrees,
  where predictions have little to add.
- **Panel C — few-types $r{=}8$** ($n=2000$, 50 trials): near-perfect-matchable, the
  calibrated regime for the type-histogram test-and-fallback algorithms.

For the degree-prediction panels the quality columns are *perfect* (true degrees),
*noisy* (random-flip at strength $\tfrac12$), *adversarial* (order-reversing), and
*garbage* (fully random $\equiv$ Ranking predictor). For the advice panel the columns are
$\eta\in\{0,0.3,0.6,1.0\}$ (*perfect / mild / bad / garbage*). Confidence intervals are
tight throughout ($\pm 0.001$–$0.003$); we omit them from the prose and report them in
Table 1.

**Table 1** (the three panels, 95% CI) and **Figure 1** (grouped bars) are the section's
data. The salient rows:

| | perfect | noisy | adversarial | garbage |
|---|---:|---:|---:|---:|
| *Panel A — clvb_zipf* | | | | |
| Ranking (floor) | 0.948 | — | — | — |
| MinDegree (oracle) | 0.996 | — | — | — |
| MPD | 0.989 | 0.956 | **0.908** | 0.946 |
| Feldman(MPD) | 0.981 | 0.979 | 0.976 | 0.978 |
| JailletLu(MPD) | 0.977 | 0.976 | 0.974 | 0.975 |
| Feldman / JailletLu (base) | 0.887 / 0.900 | — | — | — |
| *Panel B — left-regular $d{=}5$* | | | | |
| Greedy = Ranking (floor) | 0.890 | — | — | — |
| MinDegree (oracle) | 0.966 | — | — | — |
| MPD | 0.932 | 0.906 | **0.854** | 0.888 |
| Feldman(MPD) / JailletLu(MPD) | 0.906 / 0.904 | 0.902 / 0.903 | 0.896 / 0.899 | 0.900 / 0.901 |
| Feldman / JailletLu (base) | 0.760 / 0.788 | — | — | — |

<!--REV
id: 2-01
role: P4 体例校对
level: 必改
kind: 代码名进正文
mark: -
quote: Panel A - clvb_zipf
note: clvb_zipf 是生成器标识符，带下划线出现在表里。审稿人不知道 clvb 是什么，也看不出这个面板测的是什么。
fix: 改成可读名（heavy-tailed degrees (Zipf)），把脚本标识符放进复现附录。
-->

<!--REV
id: 2-02
role: P4 体例校对
level: 必改
kind: 三个 floor 不可比
mark: -
quote: Ranking (floor) 0.948 / Greedy = Ranking (floor) 0.890 / Ranking (floor) 0.990
note: 三个面板的 floor 是三个不同的数，来自不同图族，表里没有任何提示；两族的质量列语义也不同却同名并排。审稿人第一反应是横向比较。
fix: 表注加一句：floor 是 Ranking 在该面板自身图族上的比值，面板之间不可比；两族的质量列同样只在面板内部可比。
-->

| | perfect | mild | bad | garbage |
|---|---:|---:|---:|---:|
| *Panel C — few-types $r{=}8$* | | | | |
| Ranking (floor) | 0.990 | — | — | — |
| MPD (true degrees) | 0.999 | — | — | — |
| FollowPrediction | 1.000 | 0.832 | 0.679 | **0.472** |
| TestAndMatch (Choo) | 1.000 | 0.984 | 0.989 | 0.990 |
| TestAndMatch (BEM) | 0.998 | 0.988 | 0.988 | 0.968 |
| Combiner *(benchmark)* | 0.990 | 0.990 | 0.990 | 0.990 |

![The unified benchmark (Table 1) as grouped bars: competitive ratio by algorithm and advice quality, one group per panel; the advice-free floor and oracle ceiling bracket every bar.](../../results/unified_benchmark.png){width=100%}

## 3.2 Four findings

**(F1) Robustness is engineered, not free: naive followers crash below the floor.** Both
unguarded prediction-followers dive under the advice-free Ranking floor once the
prediction is adversarial or garbage: MPD falls to $0.908 < 0.948$ (Panel A, adversarial)
and $0.854 < 0.890$ (Panel B), and FollowPrediction collapses to $0.472 \ll 0.990$
(Panel C). A practitioner using either *unguarded* is strictly worse off than using no
prediction at all. Every *robust* algorithm in the tables — the augmentations,

<!--REV
id: 2-03
role: P2 领域审稿人
level: 必改
kind: 无条件断言
quote: A practitioner using either unguarded is strictly worse off than using no prediction at all.
note: strictly worse off 是无条件的，但同一张表里 MPD 在 perfect 与 noisy 两列都高于 floor。这句话能被自己的表格直接反驳。
fix: 补条件：under adversarial or garbage advice。一个从句的事。
-->
TestAndMatch, the combiner — avoids this by construction, not by luck.

**(F2) Two distinct robustness mechanisms, with different shapes.** *Structural*
robustness (Feldman(MPD), JailletLu(MPD)): a worst-case-optimal base matching carries the
load and the prediction only breaks ties, so performance is nearly *flat* across quality —
Feldman(MPD) moves only $0.981\!\to\!0.976$ from perfect to adversarial (Panel A). It
cannot crash, but it also caps the upside (it never reaches the $0.996$ oracle, and sits
below MPD's $0.989$ at perfect). *Adaptive* robustness (TestAndMatch): test a sublinear
prefix, then commit — capturing the upside when advice is good (Choo $1.000$ at perfect)
*and* holding the floor when advice is bad ($0.990$ at garbage). On Panel C it is the only
algorithm on the upper envelope at both ends. The two mechanisms trade consistency for
robustness in opposite ways.

**(F3) The consistency upside is small on average-case inputs; the spread lives on the
bad-advice side.** On few-types the advice-free Ranking is already $0.990$ and
MPD-with-true-degrees is $0.999$ — under $0.01$ for *any* advice to add on the good side.
Every wide gap in Panel C ($1.000\!\to\!0.472$ for FollowPrediction; the half-wide
envelope) is a *downside* gap. This is the thesis in one panel: learning-augmented
matching on typical inputs is robustness insurance, not a performance lift — a fact
Section 7 prices: safely capturing an upside this small would take a longer prefix than
the instance itself.

**(F4) The augmentation rescues structurally weak base algorithms.** Feldman and
Jaillet–Lu are tuned for the worst-case ratio and are the *weakest* advice-free entries on
these average-case inputs (Panel B: $0.760$ / $0.788$, well below Greedy's $0.890$). The
MPD augmentation lifts them to $\approx 0.90$ — the prediction does *more* for the
worst-case-designed algorithms than for greedy. This pairing is visible only under a

<!--REV
id: 2-04
role: P5 审稿意见预演
level: 建议
kind: 自我表扬
quote: This pairing is visible only under a unified table.
note: visible only 是对自己方法论的表扬，且容易被反驳（分别做两组实验也能看到）。审稿意见里这类句子是免费靶子。
fix: 去掉 only：a pairing that a unified table makes immediate。
-->
unified table.

## 3.3 Takeaway

Read together, F1–F4 say that on average-case matching the advice-free baseline is already
near-optimal, unguarded prediction-following is unsafe, and the value of the sophisticated
algorithms is downside protection delivered by one of two mechanisms. Sections 4–6 sharpen
and stress-test each part — what governs the (small) loss, what the adaptive test costs,
and whether the picture survives on real graphs, real traces, and a learned predictor —
and Section 7 proves the wall is not an artifact but a price: a budget–stakes law that
puts the required test prefix beyond the horizon exactly where the baseline is strong.
