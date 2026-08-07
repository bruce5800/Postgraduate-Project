# 第 10 章 Conclusion and Future Work — 审读批注

共 15 条：🔴 必改 6 · 🟡 建议 7 · ⚪ 可选 2。

批注原件在 `en/11_conclusion.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

文件名是 `11_conclusion.md`，但在论文里是第 10 章。

---
### 10-01 · 🟡 建议 · R6 初次读者 · 单段过长

`en/11_conclusion.md:27`

> This thesis studied ... and we honestly reported the directions that did not pan out ...

**问题** 10.1 第一段一口气 15 行，装下了全篇所有发现（做了什么、四类结论、两个负结果）。结论章的第一段是读者最后一次抓住主线的机会，这个密度做不到。

**建议** 拆成两段：第一段只说建立了什么（统一评测框架、复现验证、覆盖范围），第二段只说发现了什么（同一幅图景加三个子结论）。负结果单独一句起段。


### 10-02 · 🟡 建议 · R4 体例校对 · 引用格式混杂

`en/11_conclusion.md:37`

> (Chapter 3) ... (Chapters 4 to 7) ... (Chapter 5, crediting ...) ... (Chapter 6) ... (Chapter 8)

**问题** 同一段里章节引用有五种形态，有的带说明有的不带；读者在长句里要同时跟踪内容和编号。

**建议** 统一成一种：结论句在前，章号括号在句末。或者干脆把这段的章号全部去掉（结论章不必逐句标注出处），只在需要读者回查的地方保留。


### 10-03 · ⚪ 可选 · R3 英语文字编辑 · 自我评价词

`en/11_conclusion.md:47`

> we honestly reported the directions that did not pan out

**问题** honestly 是对自己写作态度的评价。诚实报告负结果是应然，写出来反而显得在争取加分；did not pan out 也偏口语。

**建议** 改成中立叙述：we also report two directions that did not work: ...。诚实靠报告本身体现，不靠形容词。


### 10-04 · 🔴 必改 · R5 答辩提问者 · 节的定位

`en/11_conclusion.md:72`

> 10.2 A theoretical outlook: the price of testing advice / This section sketches, without claiming a full theorem, why no decision rule of any kind escapes the wall

**问题** 这一节叫 outlook，但形态上是一个完整的理论小节：一条带证明草图的不等式、一条命名为 law 的结论、一个常数级推论、外加数值代入。读者（和考官）看到的是理论章，读到的却是不断的免责声明。全篇最大的答辩风险面在这里。

**建议** 两件事：一是把界定提到节首第一句，用最直白的话讲清楚，例如 This section proves one inequality and then reads our own experiments through it. Nothing else in this section is claimed as a theorem.；二是把 budget-stakes law 改称 reading 或 conjecture，law 这个词本身就在宣称已确立。


### 10-05 · 🟡 建议 · R1 二审考官 · 术语未解释

`en/11_conclusion.md:92`

> let gamma_k be the total-variation distance between the laws of their length-k prefixes

**问题** 结论章是被跳读得最多的一章，而 total variation distance 和 the laws of their prefixes 都是没解释的技术表达。2.5 讲过分布测试，但读结论的人未必回去看。

**建议** 给一句直觉：gamma_k, the total variation distance between the two prefix distributions - informally, the best possible accuracy of any test that sees only the first k arrivals。这句直觉恰好就是后面推理要用的，写出来一举两得。


### 10-06 · 🔴 必改 · R1 二审考官 · 符号未定义

`en/11_conclusion.md:125`

> k* = Theta(theta/delta^2) ... scaled by the contention theta ... delta <= 2 epsilon (1 - rho_base)

**问题** 这一页引入了八个符号（delta, Delta, gamma_k, eta_c, eta_r, theta, rho_base, epsilon），其中 theta 只用括号里 contention 一词带过，epsilon 完全没有定义。读者无法核对最后那个 0.004 是怎么算出来的。

**建议** 要么给这三个量各一句定义（theta 是什么的比例、epsilon 是什么的容差），要么把这段改写成不含 theta 和 epsilon 的形式，只保留 delta 与 rho_base。结论章能少一个符号就少一个。


### 10-07 · 🔴 必改 · R2 领域审稿人 · 未证结果陈述为事实

`en/11_conclusion.md:135`

> the decision costs a prefix of k* = Theta(theta/delta^2) ... and the budget is achievable, by a simple directional statistic

**问题** 这句以直陈语气给出了一个上下界匹配的结果。按本节自己的声明，这里只证明了那条不等式，其余是对实验的解读。审稿人和考官都会把这句读成本文的定理。

**建议** 加显式标注：in the companion development (not proved here), the decision costs ...；或改成经验语气：our experiments are consistent with a budget of order ...。


### 10-08 · 🔴 必改 · R2 领域审稿人 · 断言超出 scope

`en/11_conclusion.md:145`

> any upside below Theta(sqrt((1-rho_base)/n)) cannot be captured safely by any rule at any prefix length k <= n

**问题** any rule / cannot / any prefix length 是本论文最强的一句断言，出现在一个自称不宣称定理的小节里，并且紧跟着一个具体数值 0.004。两页之后的 10.3 又说本文不宣称任何超出该不等式的定理。前后自相矛盾，这是最危险的一处。

**建议** 降到与证据相称的语气：our reading predicts that an upside below ... cannot be captured by any rule at k <= n; verifying this is companion work。数值 0.004 保留，但明确写成 the reading predicts ... and the upsides we measured are of this order。


### 10-09 · 🔴 必改 · R5 答辩提问者 · 前提后置

`en/11_conclusion.md:155`

> (decomposable families; whether a non-decomposable family can push the budget higher is open) - 出现在 10.4

**问题** decomposable 这个适用范围前提，第一次出现是在 10.4 的 future work 里，而 10.2 的断言是以无条件语气写的。考官顺着 10.4 回头看 10.2，会问：那你 10.2 的结论到底适用于哪些实例。这个问题在答辩现场很难临时补救。

**建议** 把前提写进 10.2 断言所在的那一句：on the rare-resource (decomposable) instances that produce Figure 6.4 ...。10.4 那句就变成自然的延伸而不是事后补丁。


### 10-10 · 🟡 建议 · R3 英语文字编辑 · 信息层级过深

`en/11_conclusion.md:176`

> a tempting stronger conjecture - that the near-linear sample cost of tolerant distribution testing (2.5) blocks every sublinear rule outright - is false: it is refuted by the same directional statistic

**问题** 结论章里出现了一个我们曾经以为、后来被自己推翻的更强猜想。这段对写作者意义重大，对第一次读的人是三层嵌套（猜想、为什么诱人、为什么错），而它并不改变本文的任何结论。

**建议** 压成一句并去掉猜想的来龙去脉：the wall is not a consequence of distribution testing being expensive - a simple directional statistic is cheap; it is a consequence of the stakes being small。完整故事移到脚注或 companion work。


### 10-11 · 🟡 建议 · R5 答辩提问者 · 反复外指

`en/11_conclusion.md:186`

> the subject of the companion work

**问题** companion work 在全篇出现四次（1.3、10.2 两次、10.3）。每提一次，读者对本论文完成度的印象就低一分，考官也更容易把注意力引到一份他们看不到的稿子上。

**建议** 只在 10.3 limitations 保留一次（那里是它该在的位置），其余三处改成本文不做什么的直述句，不提外部稿件。


### 10-12 · 🔴 必改 · R2 领域审稿人 · 限制缺项

`en/11_conclusion.md:213`

> Limitations: Input model / Test model / Prediction-object heterogeneity / Data breadth / Theory scope

**问题** 最该有的一条不在列表里：全篇只用一个目标函数（匹配规模，即 goodput）衡量。这条限制在 10.4 以 Beyond throughput 的形式出现了，等于把限制写成了未来工作。审稿人对这种搬移很敏感。

**建议** 在 limitations 里新增一条 Objective：we evaluate matching size (goodput) only; on tail latency, fairness, or recompute cost the baseline may be far from optimal and the picture could differ。10.4 那条保留，二者呼应即可。


### 10-13 · 🟡 建议 · R1 二审考官 · 非标准记号

`en/11_conclusion.md:223`

> Because Known-I.I.D. <= Random-Order in difficulty, the algorithms' guarantees carry over

**问题** 用小于等于号连接两个模型名是圈内速记，写在限制一节里会让二审停顿：谁比谁难、carry over 是哪个方向。

**建议** 展开成一句话：because every known i.i.d. instance is also a random order instance, guarantees proved in the random order model carry over to ours (but not conversely)。方向讲明确。


### 10-14 · 🟡 建议 · R3 英语文字编辑 · 收尾长句

`en/11_conclusion.md:264`

> the honest verdict is that a cheap, order-faithful predictor already captures nearly all there is to capture, that the sophisticated machinery earns its keep as insurance rather than as performance, and that finding out whether to trust a prediction costs more, on these inputs, than the prediction is worth.

**问题** 一句 55 词、三个并列 that 从句。全文最后一段应该是最好读的一段。最后一句 Recognizing where predictions cannot help ... 写得很好，不要让它被前面这句拖住。

**建议** 拆成三个短句，一句一个结论，句式可以刻意重复（A cheap predictor already ... The sophisticated machinery earns ... Finding out whether to trust ...）。排比在结尾是加分的。


### 10-15 · ⚪ 可选 · R6 初次读者 · 比喻定义滞后

`en/11_conclusion.md:274`

> The recurring wall raises an obvious question / a third face of the thesis's wall

**问题** wall 在结论章出现四次，是全篇的组织比喻，但它的正式说明在 8.4 才出现，而第一次使用是在 1.3。

**建议** 在 1.3 首次出现处给一句定义（见 1-14），此后全文放心复用，结论章就不需要再解释。

