<!--
Thesis Ch 7 — External Validity. Adapted from paper/05 §6 (numbers: run_real_predictor.py,
run_realworld_robustness.py, RANK_LEARNING_M0_M3.md). Cross-refs fixed (§4→Ch5, §7→Ch9).
Guardrails: F2 "qualitatively 6/6, strictly 4/6"; §7.3 learning result is an honest negative
(the fuller Direction-A journey is Ch 8). Figures 7.1 = real_predictor, 7.2 = realworld_robustness.
-->

# Chapter 7. External Validity

Chapters 4–6 use synthetic graphs and a synthetic error knob. Is the picture real? We stress
it three ways, each replacing one synthetic ingredient with its real counterpart: §7.1
replaces the synthetic error with genuine temporal drift from a real request trace, §7.2
replaces the synthetic graphs with six real ones, and §7.3 replaces the hand-made predictor
with a learned one.

<!--REV
id: 7-01
role: R1 二审考官
level: 建议
kind: 外部效度的口径
quote: Chapters 4-6 use synthetic graphs and a synthetic error knob. Is the picture real? We stress it three ways
note: 本章开门见山很好，但没说清楚三种压力测试各自替换掉了哪一个合成成分（预测误差来源、图、预测器的训练方式）。读者读完三节后才拼得出来。
fix: 在这句后加一句对照：7.1 replaces the synthetic error with real drift, 7.2 replaces the synthetic graphs with real ones, 7.3 replaces the hand-made predictor with a learned one。一句话给出本章的骨架。
-->

## 7.1 A real, cheap predictor

We replace the synthetic knob with the cheapest realistic predictor: last-window historical
statistics. Real Wikipedia daily pageviews give a live day (the truth) and earlier days (a
1-, 7-, or 30-day-stale forecast), so the error is genuine temporal drift; we map the trace
onto a fixed serving topology and consume the forecast through the degree route (MPD)
(**Figure 7.1**). Throughout this chapter we measure how much of the available benefit a
predictor realizes by its **gap-capture**,
$(\rho_{\mathrm{ALG}}-\rho_{\mathrm{base}})/(\rho_{\mathrm{oracle}}-\rho_{\mathrm{base}})$
, the fraction of the baseline-to-oracle gap it closes. Three facts emerge.

First, **the predictor is cheap**. The with-predictions literature usually pictures an
expensive learned model; here it is a linear-time count, about $0.11$ ms per instance
against $4.4$ ms to compute $\mathrm{OPT}$ once, a few percent. These are the only
wall-clock numbers in the thesis and are therefore machine-dependent; everything else is a
ratio.

Second, **the benefit is real, partial, and never harmful**: a stale forecast reaches
$27\%$–$68\%$ gap-capture (falling with staleness) and always stays above the baseline
($0.938$–$0.957$ vs $0.923$–$0.925$, even at 30 days).

Third, and this is why: **topology aggregation makes the cheap predictor order-faithful**.
The induced degree predictor's order error is only Kendall-$\tau\approx0.19$–$0.32$, roughly
half the raw histogram's ($0.38$–$0.49$), and since MPD depends only on order (Chapter 5),
the aggregated route survives real drift. Consuming the *same* forecast through the raw
histogram is
catastrophic: blind FollowPrediction collapses to $0.68\to0.36$, far below the $\approx0.92$
baseline: exactly what the robust algorithms of Chapters 4 and 6 are for.

<!--REV
id: 7-02
role: R3 英语文字编辑
level: 必改
kind: 单段承载过多
mark: Three facts emerge
quote: Three facts emerge. First, the cost premise does not bite ... Second, the benefit is real, partial, and never harmful ... Third, and why: topology aggregation makes the cheap predictor order-faithful
note: 7.1 是一段 15 行，装了三个发现、每个发现两到三个数字、一条机制解释和一个反例。这是全章最有说服力的一节，也是最难读的一节。
fix: 拆成三段（每个 fact 一段），机制解释单独一段。数字保留，但每段只留最能说明问题的那一个。
-->

<!--REV
id: 7-03
role: R1 二审考官
level: 必改
kind: 指标未定义
quote: a stale forecast captures 27% to 68% of the oracle gap
note: gap-capture 这个指标在这里第一次出现且没有定义（应是算法相对基线的提升除以 oracle 相对基线的提升）。它随后在 8.1 又用了一次，是本文用来讲小上升空间的主力指标。
fix: 就地给定义式：we report gap-capture, (ALG - baseline)/(oracle - baseline)。一行公式，全文两处受益。
-->

<!--REV
id: 7-04
role: R1 二审考官
level: 建议
kind: 术语自造
mark: the cost premise does not bite
quote: the cost premise does not bite
note: cost premise 是本文自造的说法，指的大概是带预测算法默认预测器很贵这个前提，但正文从未提出过这个前提。读者不知道在反驳谁。
fix: 先把前提写出来再打掉：the with-predictions literature usually assumes the predictor is an expensive model; here it is a linear-time count（并给出那 0.108 毫秒作为证据）。
-->

<!--REV
id: 7-05
role: R1 二审考官
level: 建议
kind: 实验设置缺失
quote: we map the trace onto a fixed serving topology and consume the forecast through the degree route
note: 这个映射是本节外部效度的关键一步（真实 trace 怎么变成二部图），却只有半句。读者无法判断结论有多少来自真实数据、多少来自映射方式的选择。
fix: 补两句说明映射规则，或指向附录 A.5；并说明映射方式的选择是否影响结论（是否试过别的映射）。
-->

![The figure to remember from this chapter: a real, cheap predictor (Wikipedia trace). The aggregated degree route survives staleness (b) because aggregation halves the order error (a); blind histogram-following decays.](../../results/real_predictor.png){width=80%}

## 7.2 Six real-world graphs

We re-run the degree-prediction roster of Chapter 4 on the six Network-Repository graphs (two
Facebook social, two C. elegans biological, two economic input-output), across the same
quality columns, with 95% CIs (**Figure 7.2**). The two load-bearing findings are universal.
**F1 holds on all six**: naive MPD fed an adversarial predictor falls below the Ranking floor
everywhere, by $0.06$ (Reed98) to $0.10$ (CE-PG). **F3 holds on all six, and confirms
its own logic**: the consistency upside is small everywhere (mean $+0.049$; range $+0.022$–$+0.077$)
and smallest exactly where the baseline is strongest: the two dense economic graphs, with
Ranking already $0.965$/$0.977$, give the tiniest upsides.

<!--REV
id: 7-06
role: R2 领域审稿人
level: 必改
kind: 断言过强
quote: F3 is universal and confirms its own logic
note: universal 用在六个图的样本上过强，尤其本节紧接着就要说 F2 在其中两个图上只是部分成立。审稿人会抓这个词。
fix: 改成 holds on all six graphs we tested，并把机制解释（上升空间在基线最强处最小）留作真正的论点 - 那才是这一节的价值。
-->

<!--REV
id: 7-07
role: R2 领域审稿人
level: 建议
kind: 判据不对称
quote: F2 holds qualitatively on all six and strictly on the four social/bio graphs (spread 0.22 to 0.29x MPD's)
note: strictly 给了判据（spread 倍数），qualitatively 没有。两个词并列出现却只有一个可核查，读者会怀疑 qualitatively 是不是事后放宽的口径。
fix: 给出 qualitatively 的判据：例如 the augmentations' spread is smaller than naive MPD's on all six。两个判据都写死。
-->

The structural-robustness finding **F2 holds qualitatively on all six** (the augmentations'
spread across quality columns is smaller than naive MPD's on every graph) and *strictly*,
by the stronger criterion that the spread is at most half of MPD's, on the four
social/bio graphs (spread $0.22$–$0.29\times$ MPD's); on the two dense economic graphs the
protection is only *partial*: the augmentation cushions the adversarial drop ($0.939$ vs
naive MPD's $0.893$) but cannot clear the unusually high $0.965$ floor, dipping $\approx0.03$
below it. Those two graphs are so dense that matching is nearly trivial (Ranking
$\approx0.97$, MinDegree $=1.00$), so there is neither upside to capture (F3) nor much
downside to protect: the boundary is F3's own mechanism at work, not an exception to it. Finally, F4 is dramatic: the
worst-case-designed Feldman/Jaillet–Lu are the weakest advice-free entries on the econ graphs
($0.73$–$0.77$) and the augmentation lifts them to $0.99$, a $+0.26$ rescue.

<!--REV
id: 7-08
role: R5 答辩提问者
level: 必改
kind: 自我辩护
mark: This econ boundary is instructive rather than a failure
quote: This econ boundary is instructive rather than a failure
note: 遇到不利结果时先给自己定性（不是失败），是审稿人和考官最敏感的写法之一，反而会让人多看两眼这个边界。后面的解释（图太密、匹配近乎平凡）本身是充分的。
fix: 删掉这句评价，直接给解释和它的含义：on these two graphs matching is nearly trivial, so there is neither upside to capture nor downside to protect - the mechanism, not an exception。让读者自己得出不是失败的结论。
-->

<!--REV
id: 7-09
role: R1 二审考官
level: 建议
kind: 图注不自足
quote: F1-F3 on six real graphs: naive MPD (red) dips below the Ranking floor everywhere
note: 图注用颜色指代算法（red / green / blue），但没有说明六个子图的排布和纵轴范围是否统一。六联图如果纵轴不同，跨图比较就是错的。
fix: 图注写明：one panel per graph, shared vertical axis (or: axes differ; see values in text)。这一句决定了读者能不能横向读这张图。
-->

![F1–F3 on six real graphs, one panel per graph (axis ranges differ between panels, as the graphs' floors do too, so read each panel against its own dashed floor rather than across panels). Naive MPD (red) dips below the Ranking floor everywhere; the structural augmentations (green/blue) stay flat.](../../results/realworld_robustness.png){width=100%}

## 7.3 Does learning the predictor help?

Because MPD consumes the predictor only through order (Chapter 5), one might train it with a
rank loss rather than regression. We tested this and report an honest negative: the advantage
is real on deliberately engineered features but disappears on real temporal ones, where
rank- and regression-trained predictors induce the same order and reach the same ratio. The
experiments, their numbers and the three-step argument behind them are in §8.1; what matters
for external validity is only the consequence. Once a predictor
is order-faithful, which a cheap historical count already is (§7.1), neither a better
algorithm nor a better-trained predictor buys much on average-case matching.

<!--REV
id: 7-10
role: R4 体例校对
level: 必改
kind: 跨章重复
mark: synthetic features rank-training beats regression sharply
quote: rank-training beats regression sharply (0.989 approximately oracle vs 0.974) ... on real temporal features it disappears - identical order (Kendall-tau 0.126 vs 0.126)
note: 7.3 与 8.1 讲的是同一组实验、同一批数字（0.989 / 0.974 / 0.126），两处各写一遍。读者读到第 8 章会以为是新实验，核对后发现是同一个。
fix: 定正本：第 8 章是正本（那里有完整的 M0 到 M3 过程），7.3 压到三句并明确写 the full account is in 8.1。或者反过来，但不要两处都是完整版。
-->

## 7.4 Chapter summary

On real predictors, real graphs, and a learned predictor, the same wall stands: the
advice-free baseline is near-optimal, unguarded following is unsafe, and predictions buy
downside protection rather than performance, with one instructive boundary: the two dense
economic graphs of §7.2, where the augmentation cannot quite clear an unusually high
floor. Having established the wall empirically across
every setting we could reach, Chapter 8 reports the directions that tried to get past it,
and the concluding outlook (§10.2) explains why it is forced.

<!--REV
id: 7-11
role: R6 初次读者
level: 建议
kind: 章末口径
quote: On real predictors, real graphs, and a learned predictor, the same wall stands
note: 小结把三节压成一句，很好；但 7.2 那两个 econ 图上 F2 只是部分成立的事实在小结里消失了。考官若先读小结再回看正文，会觉得小结报喜不报忧。
fix: 小结补半句：with one instructive boundary (the two dense economic graphs, 7.2)。诚实的小结反而更有说服力。
-->
