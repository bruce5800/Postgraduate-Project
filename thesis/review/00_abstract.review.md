# 摘要 — 审读批注

共 10 条：🔴 必改 4 · 🟡 建议 6 · ⚪ 可选 0。

批注原件在 `review/00_abstract.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

源文件是 `thesis/latex/meta.yaml` 的 `abstract:` 块（中文版在 `meta_zh.yaml`）；`review/00_abstract.md` 只是批注用的副本，改定稿请改 meta.yaml。

---
### A-01 · 🔴 必改 · R1 二审考官 · 术语未解释

`review/00_abstract.md:28`

> MinPredictedDegree consumes a per-node degree predictor ... a type-histogram prediction on a sublinear prefix

**问题** 摘要第一句就并列了三个只有本领域读者才认识的对象：MinPredictedDegree（一个具体算法名）、type-histogram prediction（预测对象）、sublinear prefix（相对什么是亚线性？）。二审考官读到这里没有任何上下文可以挂靠，第一句就掉队。

**建议** 把算法名换成它做的事，把亚线性换成读者能想象的量。例如：one family consumes a prediction of how contended each resource will be; another tests a prediction of the arrival mix on a short prefix of the requests (a vanishing fraction of the instance) before deciding whether to trust it. 具体算法名留到正文。


### A-02 · 🟡 建议 · R1 二审考官 · 缺少问题直觉

`review/00_abstract.md:38`

> algorithms for online bipartite matching have proliferated

**问题** 摘要从未说明 online bipartite matching 是什么问题、难在哪。评审细则里摘要要能独立被非本方向的人读懂。

**建议** 开头补半句不可逆性这个核心：where requests arrive one at a time and each must be irrevocably matched to a resource, or dropped, before the rest of the input is seen. Ch1 第一段已有这句话，直接压缩过来即可。


### A-03 · 🔴 必改 · R3 英语文字编辑 · 长句密集

`review/00_abstract.md:48`

> We give the first unified experimental study, placing all of them on a single harness with a common structured prediction-error model, a common optimum, and confidence intervals, across ...

**问题** 230 词的摘要里有四个超长句（约 60 / 47 / 68 / 66 词），其中三句还都用了分号加破折号的多层并置。摘要是全篇被读得最多、也最需要一遍读懂的一段。

**建议** 每句压到 25 词以内，一句一个动作。示例：We place all of them on one experimental harness: a common prediction-error model, a common optimum, and confidence intervals. We run it on synthetic graphs, six real-world graphs, and real request traces.


### A-04 · 🔴 必改 · R3 英语文字编辑 · 结尾重复

`review/00_abstract.md:59`

> a price that ... exceeds the length of the instance itself. Experiments and outlook deliver one message: ... the advice's upside is smaller than the price of finding out whether to trust it.

**问题** 最后两句是同一命题的两种说法，摘要结尾连说两遍会显得内容不够。

**建议** 二选一。保留最后一句作为全篇金句（它更好记），把倒数第二句的 a price that ... itself 删掉，让 scales as the inverse square of the advice's upside 直接收在句号上。


### A-05 · 🔴 必改 · R2 领域审稿人 · scope 与正文不符

`review/00_abstract.md:70`

> We close with a theoretical outlook: a proved consistency/robustness trade-off inequality, together with a budget–stakes reading

**问题** 摘要用 proved 和 law 一类的措辞介绍这部分，读者形成的预期是本文有一个理论结果；而正文 10.2 明确说 sketches, without claiming a full theorem，完整发展 deferred to companion work，10.3 又把它列为 limitation。摘要与正文的 scope 不一致，是考官最容易当场追问的地方。

**建议** 在摘要里就把边界说清楚，只需加一个限定词组：We close with a theoretical outlook (one proved inequality, and a quantitative reading of our own experiments; the full development is companion work). 宁可摘要保守，正文再给惊喜。


### A-06 · 🟡 建议 · R2 领域审稿人 · 断言支撑

`review/00_abstract.md:80`

> We give the first unified experimental study

**问题** first 是可被证伪的断言，摘要里没有限定范围。这本身站得住（2.6 有定位），但要确保正文有一句明确的检索范围声明供审稿人核对。

**建议** 摘要保留 first 不变，但确认 2.6 有一句类似 to our knowledge, no prior work evaluates these two families on a common harness 的话，并在答辩前准备好这句的依据。


### A-07 · 🟡 建议 · R4 体例校对 · 术语漂移

`review/00_abstract.md:90`

> unguarded prediction-following ... the consistency upside of good advice ... the advice's upside

**问题** 同一个对象在摘要里交替叫 prediction 和 advice（还有 hint 出现在 Ch1）。单独看都通顺，连起来读者会怀疑二者是不是两样东西。

**建议** 定一条全篇规则：正式对象一律 prediction，只有在讲信不信它的时候用 advice，并在 Ch1 首次出现时点明二者同指。然后全文 grep 一遍统一。


### A-08 · 🟡 建议 · R6 初次读者 · 缺少可信锚点

`review/00_abstract.md:100`

> the advice-free baseline is already near-optimal, so the consistency upside of good advice is small

**问题** 整段摘要没有一个数字。实验类论文的摘要给一两个关键数字，读者立刻就相信 upside 很小这个反直觉结论；否则它读起来像一个观点。

**建议** 塞两个数：baseline 已达 OPT 的约 0.99，而无防护地跟随坏预测会掉到约 0.45。这是全文最有说服力的一组对比。


### A-09 · 🟡 建议 · R3 英语文字编辑 · 指代过远

`review/00_abstract.md:110`

> the practical worth of the sophisticated algorithms is that they never do

**问题** they never do 指代的是二十多个词之前的 crash far below the baseline，读者需要回读。

**建议** 写实：their practical worth is that they never crash.


### A-10 · 🟡 建议 · R5 答辩提问者 · 招问句

`review/00_abstract.md:120`

> Experiments and outlook deliver one message

**问题** 这句把 outlook 与实验并列为结论来源。老师顺着这句问的第一个问题一定是：你的 outlook 究竟证明了什么？而按 10.3 的自述，那里只证明了一条不等式。

**建议** 改成实验交付结论、展望给出解释的层级关系：Our experiments deliver one message, and the outlook explains why it should be expected. 同时和 A-05 的限定保持一致。

