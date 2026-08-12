<!--
Thesis Ch 10 (was Ch 11; the theory chapter was cut 2026-07-27 and replaced by the
one-page outlook in §10.2 — full theory lives in the companion paper, docs/paper/06).
Conclusion: summary, theoretical outlook, limitations, future work, closing.
-->

# Chapter 10. Conclusion and Future Work

## 10.1 Summary

This thesis studied learning-augmented algorithms for online bipartite matching by first
building a common experimental foundation and then explaining what it revealed. On a single
harness — validated against the published Borodin et al. study (Chapter 3) — we compared the
advice-free baselines, MinPredictedDegree and its augmentations, and the test-and-fallback
algorithms, across synthetic graphs, six real-world graphs, and real request traces
(Chapters 4–7).

Across every setting the same picture appeared: the advice-free baseline is already
near-optimal on average-case inputs, so the *consistency* upside of a good prediction is
small; unguarded prediction-following crashes *below* the baseline under bad predictions; and
the value of the sophisticated algorithms is downside protection, delivered by either a
structural or an adaptive robustness mechanism with distinct trade-offs. We sharpened the
sub-questions — that the (small) loss is governed by a Kendall-$\tau$ order error rather than
magnitude (Chapter 5, crediting the prior order-dependence result of ACI), and that the
adaptive test has a threshold-calibration pathology and a resolution limit (Chapter 6) — and
we honestly reported the directions that did *not* pan out: learning the predictor for extra
performance, and finding a serving regime where predictions genuinely help (Chapter 8).

<!--REV
id: 10-01
role: R6 初次读者
level: 建议
kind: 单段过长
quote: This thesis studied ... and we honestly reported the directions that did not pan out ...
note: 10.1 第一段一口气 15 行，装下了全篇所有发现（做了什么、四类结论、两个负结果）。结论章的第一段是读者最后一次抓住主线的机会，这个密度做不到。
fix: 拆成两段：第一段只说建立了什么（统一评测框架、复现验证、覆盖范围），第二段只说发现了什么（同一幅图景加三个子结论）。负结果单独一句起段。
-->

<!--REV
id: 10-02
role: R4 体例校对
level: 建议
kind: 引用格式混杂
quote: (Chapter 3) ... (Chapters 4 to 7) ... (Chapter 5, crediting ...) ... (Chapter 6) ... (Chapter 8)
note: 同一段里章节引用有五种形态，有的带说明有的不带；读者在长句里要同时跟踪内容和编号。
fix: 统一成一种：结论句在前，章号括号在句末。或者干脆把这段的章号全部去掉（结论章不必逐句标注出处），只在需要读者回查的地方保留。
-->

<!--REV
id: 10-03
role: R3 英语文字编辑
level: 可选
kind: 自我评价词
quote: we honestly reported the directions that did not pan out
note: honestly 是对自己写作态度的评价。诚实报告负结果是应然，写出来反而显得在争取加分；did not pan out 也偏口语。
fix: 改成中立叙述：we also report two directions that did not work: ...。诚实靠报告本身体现，不靠形容词。
-->

The recurring wall raises an obvious question: is it an accident of the inputs we chose,
or is it forced? The next section gives our answer in outlook form. The single sentence
that unifies the thesis is: **on average-case online matching, predictions are robustness
insurance rather than a performance lever — and the upside they offer is smaller than the
price of finding out whether to trust them.**

## 10.2 A theoretical outlook: the price of testing advice

This section does two things and nothing more: it proves one inequality, and then reads our
own experiments through it. Nothing beyond that inequality is claimed as a theorem, and the
reading that follows it is an interpretation of measurements rather than a proof.

With the scope fixed: the experiments say that no *practical* acceptance threshold captures
the upside safely (§6.3, Figure 6.4). The question here is whether a decision rule of some
*other* kind could, on the inputs where the wall stands.

<!--REV
id: 10-04
role: R5 答辩提问者
level: 必改
kind: 节的定位
quote: 10.2 A theoretical outlook: the price of testing advice / This section sketches, without claiming a full theorem, why no decision rule of any kind escapes the wall
note: 这一节叫 outlook，但形态上是一个完整的理论小节：一条带证明草图的不等式、一条命名为 law 的结论、一个常数级推论、外加数值代入。读者（和考官）看到的是理论章，读到的却是不断的免责声明。全篇最大的答辩风险面在这里。
fix: 两件事：一是把界定提到节首第一句，用最直白的话讲清楚，例如 This section proves one inequality and then reads our own experiments through it. Nothing else in this section is claimed as a theorem.；二是把 budget-stakes law 改称 reading 或 conjecture，law 这个词本身就在宣称已确立。
-->

> **A trade-off inequality.** Let $G$ and $\mathrm{Bd}$ be two instance distributions
> sharing the *same* advice, such that following the advice gains $\delta$ under $G$ and
> loses $\Delta$ under $\mathrm{Bd}$ relative to the advice-free baseline, and let
> $\gamma_k$ be the total-variation distance between the laws of their length-$k$
> prefixes — informally, the best accuracy any test can reach when it sees only the first
> $k$ arrivals. Then every test-and-fallback algorithm — deciding by *any* measurable rule on
> its prefix — satisfies
> $$(1-\eta_c)\;\le\;\eta_r+\gamma_k+o(1),$$
> where $\eta_c$ is the fraction of the upside it forgoes under $G$ and $\eta_r$ its
> robustness loss under $\mathrm{Bd}$ as a fraction of $\Delta$.

<!--REV
id: 10-05
role: R1 二审考官
level: 建议
kind: 术语未解释
mark: be the total-variation distance between the laws of their length
quote: let gamma_k be the total-variation distance between the laws of their length-k prefixes
note: 结论章是被跳读得最多的一章，而 total variation distance 和 the laws of their prefixes 都是没解释的技术表达。2.5 讲过分布测试，但读结论的人未必回去看。
fix: 给一句直觉：gamma_k, the total variation distance between the two prefix distributions - informally, the best possible accuracy of any test that sees only the first k arrivals。这句直觉恰好就是后面推理要用的，写出来一举两得。
-->

The proof is a short conditioning argument: capturing the upside forces the algorithm to
follow with high probability under $G$; robustness forces fallback under $\mathrm{Bd}$;
and no function of the prefix can behave differently on two prefix distributions that are
statistically $\gamma_k$-close. The inequality thus converts "consistent *and* robust"
into a question about *sample complexity*: how long must the prefix be before it
distinguishes advice worth following from advice worth rejecting?

The reading applies to the rare-resource instances that produce Figure 6.4 — a
*decomposable* family, in which the instance splits into independent cells and the advice
acts on each of them separately — and it is a **budget–stakes** relation. Write $\delta$
for the *stakes*: what good advice gains over the baseline. In the companion development,
which is not proved here, the decision costs a prefix of
$k^* = \tilde\Theta(\theta/\delta^2)$ — the inverse square of the stakes, scaled by a
contention parameter $\theta$ that on these instances is of the same order as the baseline
slack $1-\rho_{\mathrm{base}}$ — and that budget is met by a simple *directional* statistic
(do the prefix arrivals agree with the advice's predictions more often than they contradict
them?). The stakes are in turn capped by the same slack, $\delta = O(1-\rho_{\mathrm{base}})$:
advice can only win what the baseline leaves on the table. Substituting, the reading predicts
that on strong-baseline instances the required prefix exceeds the whole instance — that an
upside below $\Theta\bigl(\sqrt{(1-\rho_{\mathrm{base}})/n}\bigr)$ would not be captured by
any rule at any prefix length $k \le n$. At the parameters of Chapter 4
($\rho_{\mathrm{base}}\approx0.99$, $n=2000$) that threshold is $\approx0.004$, and the
upsides we measured are of exactly this order (F3): the empirical wall sits where the
reading says it should. Whether the same relation holds beyond decomposable families is
open (§10.4). This is Figure 6.4 read quantitatively: the potential upside and
the capturable upside separate as the baseline strengthens, because the stakes shrink
faster than the test's resolution improves.

<!--REV
id: 10-06
role: R1 二审考官
level: 必改
kind: 符号未定义
mark: scaled by the contention
quote: k* = Theta(theta/delta^2) ... scaled by the contention theta ... delta <= 2 epsilon (1 - rho_base)
note: 这一页引入了八个符号（delta, Delta, gamma_k, eta_c, eta_r, theta, rho_base, epsilon），其中 theta 只用括号里 contention 一词带过，epsilon 完全没有定义。读者无法核对最后那个 0.004 是怎么算出来的。
fix: 要么给这三个量各一句定义（theta 是什么的比例、epsilon 是什么的容差），要么把这段改写成不含 theta 和 epsilon 的形式，只保留 delta 与 rho_base。结论章能少一个符号就少一个。
-->

<!--REV
id: 10-07
role: R2 领域审稿人
level: 必改
kind: 未证结果陈述为事实
quote: the decision costs a prefix of k* = Theta(theta/delta^2) ... and the budget is achievable, by a simple directional statistic
note: 这句以直陈语气给出了一个上下界匹配的结果。按本节自己的声明，这里只证明了那条不等式，其余是对实验的解读。审稿人和考官都会把这句读成本文的定理。
fix: 加显式标注：in the companion development (not proved here), the decision costs ...；或改成经验语气：our experiments are consistent with a budget of order ...。
-->

<!--REV
id: 10-08
role: R2 领域审稿人
level: 必改
kind: 断言超出 scope
mark: cannot be captured safely by any rule at any prefix length
quote: any upside below Theta(sqrt((1-rho_base)/n)) cannot be captured safely by any rule at any prefix length k <= n
note: any rule / cannot / any prefix length 是本论文最强的一句断言，出现在一个自称不宣称定理的小节里，并且紧跟着一个具体数值 0.004。两页之后的 10.3 又说本文不宣称任何超出该不等式的定理。前后自相矛盾，这是最危险的一处。
fix: 降到与证据相称的语气：our reading predicts that an upside below ... cannot be captured by any rule at k <= n; verifying this is companion work。数值 0.004 保留，但明确写成 the reading predicts ... and the upsides we measured are of this order。
-->

<!--REV
id: 10-09
role: R5 答辩提问者
level: 必改
kind: 前提后置
mark: on the rare-resource instances that produce
quote: (decomposable families; whether a non-decomposable family can push the budget higher is open) - 出现在 10.4
note: decomposable 这个适用范围前提，第一次出现是在 10.4 的 future work 里，而 10.2 的断言是以无条件语气写的。考官顺着 10.4 回头看 10.2，会问：那你 10.2 的结论到底适用于哪些实例。这个问题在答辩现场很难临时补救。
fix: 把前提写进 10.2 断言所在的那一句：on the rare-resource (decomposable) instances that produce Figure 6.4 ...。10.4 那句就变成自然的延伸而不是事后补丁。
-->

Two honest notes bound the scope of this outlook. First, the budget law cuts both ways:
where the stakes are large (a weak baseline), the directional statistic is cheap and
following good advice is easy — the wall is a statement about strong-baseline,
average-case inputs, not about testing in general. In particular the wall is not a consequence of distribution testing being
expensive — a directional statistic is cheap — but of the stakes being small; the
$\ell_1$-threshold blindness of §6.3 comes from testing the *distance* rather than the
*payoff*. Second, this thesis claims only the inequality displayed above and the quantitative
reading of its own experiments; the two-sided law and its exact scope are not established
here (§10.3).

<!--REV
id: 10-10
role: R3 英语文字编辑
level: 建议
kind: 信息层级过深
quote: a tempting stronger conjecture - that the near-linear sample cost of tolerant distribution testing (2.5) blocks every sublinear rule outright - is false: it is refuted by the same directional statistic
note: 结论章里出现了一个我们曾经以为、后来被自己推翻的更强猜想。这段对写作者意义重大，对第一次读的人是三层嵌套（猜想、为什么诱人、为什么错），而它并不改变本文的任何结论。
fix: 压成一句并去掉猜想的来龙去脉：the wall is not a consequence of distribution testing being expensive - a simple directional statistic is cheap; it is a consequence of the stakes being small。完整故事移到脚注或 companion work。
-->

<!--REV
id: 10-11
role: R5 答辩提问者
level: 建议
kind: 反复外指
quote: the subject of the companion work
note: companion work 在全篇出现四次（1.3、10.2 两次、10.3）。每提一次，读者对本论文完成度的印象就低一分，考官也更容易把注意力引到一份他们看不到的稿子上。
fix: 只在 10.3 limitations 保留一次（那里是它该在的位置），其余三处改成本文不做什么的直述句，不提外部稿件。
-->

## 10.3 Limitations

- **Input model.** We work in the known-i.i.d. model. Because every known-i.i.d. instance is
  also a random-order instance, guarantees proved in the random-order model carry over to
  ours (but not conversely, §2.1); the empirical wall, however, is an *average-case* statement; we do not claim it for adversarial arrival order.
- **Test model.** Following the original authors, the test-and-fallback experiments use an
  empirical-$\ell_1$ surrogate for the (unimplemented) distribution tester; §10.2 explains
  why the surrogate's blindness is structural rather than an implementation artifact.
- **Prediction-object heterogeneity.** The degree- and histogram-prediction families do not
  map onto every graph, which is why they are reported in parallel panels rather than one
  table.
- **Data breadth.** Each real modality is exercised by one trace.
- **Objective.** We evaluate matching size (goodput) only. On objectives where the
  advice-free baseline is *not* near-optimal — tail latency, per-type fairness, migration or
  recompute cost — the picture could differ; our one probe in that direction (§8.2) closed
  the simplest such attempt but not the space (§10.4).
- **Theory scope.** The thesis deliberately confines its theory to the outlook of §10.2 —
  one proved trade-off inequality and a quantitative reading of the experiments. The full
  budget–stakes law is companion work in preparation, and no theorem beyond the stated
  inequality is claimed here.

<!--REV
id: 10-12
role: R2 领域审稿人
level: 必改
kind: 限制缺项
mark: Each real modality is exercised by one trace
quote: Limitations: Input model / Test model / Prediction-object heterogeneity / Data breadth / Theory scope
note: 最该有的一条不在列表里：全篇只用一个目标函数（匹配规模，即 goodput）衡量。这条限制在 10.4 以 Beyond throughput 的形式出现了，等于把限制写成了未来工作。审稿人对这种搬移很敏感。
fix: 在 limitations 里新增一条 Objective：we evaluate matching size (goodput) only; on tail latency, fairness, or recompute cost the baseline may be far from optimal and the picture could differ。10.4 那条保留，二者呼应即可。
-->

<!--REV
id: 10-13
role: R1 二审考官
level: 建议
kind: 非标准记号
quote: Because Known-I.I.D. <= Random-Order in difficulty, the algorithms' guarantees carry over
note: 用小于等于号连接两个模型名是圈内速记，写在限制一节里会让二审停顿：谁比谁难、carry over 是哪个方向。
fix: 展开成一句话：because every known i.i.d. instance is also a random order instance, guarantees proved in the random order model carry over to ours (but not conversely)。方向讲明确。
-->

## 10.4 Future work

The thesis brackets, rather than resolves, the settings in which predictions might genuinely
help online matching, and these are the natural next directions.

- **Beyond average-case inputs.** The wall is an average-case phenomenon. Adversarial or
  non-stationary arrival orders, where the advice-free baseline is provably far from optimal,
  are where predictions should carry real value — and where a *positive* counterpart to
  this thesis's wall might be proved.
- **Beyond throughput.** Objectives on which the baseline is not near-optimal — tail latency,
  per-type fairness, migration or recompute cost — may admit genuine with-predictions gains
  that the goodput objective forecloses; our serving SLO probe (Chapter 8) closed the
  simplest such attempt but not the space.
- **Completing the theory.** Finishing the companion budget–stakes development — the sharp
  two-sided law, the directional statistic as its matching upper bound, and its exact scope
  (decomposable families; whether a non-decomposable family can push the budget higher is
  open) — would turn the outlook of §10.2 into a tight characterization.
- **Better tests, honestly.** Whether a super-linear or amortized test, or a test that
  reuses online decisions as samples, can beat the stakes-squared budget of §10.2 is an
  open and practically motivated question.

## 10.5 Closing

Predictions are a powerful tool for online algorithms, but this thesis is a study of their
*limits* on one well-understood problem. On average-case online matching, the honest verdict has three parts. A cheap,
order-faithful predictor already captures nearly all there is to capture. The sophisticated
machinery earns its keep as insurance rather than as performance. And finding out whether to
trust a prediction costs more, on these inputs, than the prediction is worth. Recognizing where predictions cannot help is, we hope, as useful as
knowing where they can.

<!--REV
id: 10-14
role: R3 英语文字编辑
level: 建议
kind: 收尾长句
quote: the honest verdict is that a cheap, order-faithful predictor already captures nearly all there is to capture, that the sophisticated machinery earns its keep as insurance rather than as performance, and that finding out whether to trust a prediction costs more, on these inputs, than the prediction is worth.
note: 一句 55 词、三个并列 that 从句。全文最后一段应该是最好读的一段。最后一句 Recognizing where predictions cannot help ... 写得很好，不要让它被前面这句拖住。
fix: 拆成三个短句，一句一个结论，句式可以刻意重复（A cheap predictor already ... The sophisticated machinery earns ... Finding out whether to trust ...）。排比在结尾是加分的。
-->

<!--REV
id: 10-15
role: R6 初次读者
level: 可选
kind: 比喻定义滞后
mark: -
quote: The recurring wall raises an obvious question / a third face of the thesis's wall
note: wall 在结论章出现四次，是全篇的组织比喻，但它的正式说明在 8.4 才出现，而第一次使用是在 1.3。
fix: 在 1.3 首次出现处给一句定义（见 1-14），此后全文放心复用，结论章就不需要再解释。
-->
