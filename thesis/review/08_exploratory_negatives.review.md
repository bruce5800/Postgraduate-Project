# 第 8 章 Exploratory Directions and Negative Results — 审读批注

共 13 条：🔴 必改 4 · 🟡 建议 8 · ⚪ 可选 1。

批注原件在 `en/08_exploratory_negatives.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

---
### 8-01 · 🟡 建议 · R6 初次读者 · 编号跳号

`en/08_exploratory_negatives.md:21`

> M0 - the mechanism exists ... M1 - but the advantage is doubly gated ... M3 - and it disappears on real features

**问题** 三个里程碑编号是 M0、M1、M3，中间跳过了 M2。读者的第一反应是这里漏了一节，或者 M2 是失败到不能写的部分。

**建议** 要么改成 M1 到 M3 连号，要么用一句话交代 M2 是什么以及为什么不报告（例如它被 M3 取代）。跳号在学位论文里一定会被问。


### 8-02 · 🟡 建议 · R5 答辩提问者 · 章的定位

`en/08_exploratory_negatives.md:31`

> This chapter reports them honestly, including the negatives, because they are part of the evidence and because ruling out ambitious alternatives is itself a result.

**问题** 这句为整章的存在做辩护，语气偏防守。负结果章本身是加分项，不需要先自辩。

**建议** 改成正面陈述这一章提供什么：Each direction is reported with the evidence that closed it。诚实通过内容体现，不通过声明体现。


### 8-03 · 🟡 建议 · R2 领域审稿人 · 结论限定

`en/08_exploratory_negatives.md:57`

> confirming that regression is the wrong training objective when it matters

**问题** when it matters 是一个事后加的限定，等于说在它成立的时候它成立。而 M1、M3 恰恰证明了它几乎从不成立。这句话会被审稿人当作循环论证的例子。

**建议** 把限定写成可检验的条件：regression is the wrong objective when the features separate magnitude from order - a condition M1 and M3 show is rare。


### 8-04 · 🟡 建议 · R1 二审考官 · 指标重复出现

`en/08_exploratory_negatives.md:76`

> a more favorable framing is gap-capture, where rank-training recovers essentially the full oracle gap

**问题** gap-capture 在 7.1 用过一次、这里再用一次，两处都没有定义（见 7-03）。而且 a more favorable framing 这个说法等于告诉读者：我们换了个对自己有利的口径。

**建议** 统一在 7.1 给定义，这里直接用；并把 a more favorable framing 改成中性说法：measured as gap-capture rather than as absolute ratio。


### 8-05 · 🟡 建议 · R2 领域审稿人 · 负结果的范围

`en/08_exploratory_negatives.md:95`

> across every topology and lag configuration tried

**问题** 这是本章最有分量的一个负结果，支撑它的是一句 every configuration tried，但配置清单没有给（试了几种拓扑、几种滞后、哪条 trace）。负结果的说服力全在覆盖面上。

**建议** 把清单写进正文一句或附录一行：topologies A/B/C, lags 1/7/30, two traces。审稿人接受负结果的前提是知道你找过多远。


### 8-06 · 🟡 建议 · R5 答辩提问者 · 投稿视角外泄

`en/08_exploratory_negatives.md:115`

> Learning the predictor with a decision-aligned loss does not elevate to a standalone contribution

**问题** elevate to a standalone contribution 是投稿语言（够不够单独发一篇），出现在学位论文里会让考官意识到这一章是从投稿计划里改写来的。

**建议** 换成对本论文的判断：this direction does not change the picture of Chapters 4-7, and we report it as a negative result。


### 8-07 · 🟡 建议 · R6 初次读者 · 先给结论

`en/08_exploratory_negatives.md:135`

> The obstacle is again the wall: every serving variant we tried optimizes throughput (goodput), and throughput is forgiving

**问题** 这一段先讲动机再讲障碍再讲出路，读者要读到段末才知道本节结论是负的。而节标题已经写了 a negative probe。

**建议** 把 the escape must be a different objective 这句提到段首作为本节的论点，后面的论证跟着走。


### 8-08 · 🔴 必改 · R2 领域审稿人 · 对照组的地位

`en/08_exploratory_negatives.md:158`

> against a clairvoyant oracle that reserves based on the actual future burst

**问题** clairvoyant oracle 被当作上界使用，但它只是一个知道未来的启发式（按未来 burst 预留），不是该目标下的最优策略。若它本身次优，那么非预测策略追平它就不能说明预测无用 - 而这正是本节的结论。

**建议** 两条路：证明或论证该策略在此目标下确实最优；或者把措辞降级为 a clairvoyant baseline（不是 oracle），并说明它是一个上界的估计而非上界。这是本节结论成立与否的关键。


### 8-09 · 🟡 建议 · R2 领域审稿人 · 反常结果需要解释

`en/08_exploratory_negatives.md:169`

> a trivial static reservation of one slot drives tight-SLO violations to near zero and beats the clairvoyant oracle outright

**问题** 非预测策略跑赢了全知策略，这在逻辑上就说明全知策略不是最优（呼应上一条）。正文把它作为结论的强化，实际上它是对照组设计的一个警告信号。

**建议** 把这句改成对照组局限的证据并就地说明原因（全知策略按未来 burst 预留，反而在中等负载下预留过多）。诚实处理这一点会显著提高本节的可信度。


### 8-10 · 🔴 必改 · R4 体例校对 · 跨章重复

`en/08_exploratory_negatives.md:187`

> a third face of the wall, after throughput (Chapters 4-7) and predictor-learning (8.1)

**问题** 8.2 与 9.2 写的是同一次探针，数字、两条原因、以及 a third face of the wall 这句话几乎逐字重复；而 8.2 指向第 9 章、9.2 又指回第 8 章，两节互相把读者推给对方。

**建议** 定 8.2 为正本（它属于负结果章），9.2 压到两句并写 we summarise the probe here; the full account is in 8.2。同时删掉其中一处的循环指向。


### 8-11 · 🔴 必改 · R5 答辩提问者 · 招问的方法描述

`en/08_exploratory_negatives.md:219`

> We conducted a large multi-source, adversarially-verified literature search (documented in docs/LITERATURE_REVIEW.md)

**问题** 两个问题。其一，adversarially-verified 这个说法在文献综述语境下没有公认含义，考官很可能顺口问一句这具体是怎么做的、是不是自动化工具做的 - 而这是你最不想在现场即兴回答的问题。其二，正文引用了一个仓库内部文档，读者拿不到。

**建议** 把方法写成可复述的常规程序：检索了哪些库、用了哪些关键词、时间范围、以及交叉核对的方式；把 docs 文档的实质内容摘成附录一页，正文指向附录而不是指向仓库路径。


### 8-12 · 🔴 必改 · R4 体例校对 · 指向仓库内部文档

`en/08_exploratory_negatives.md:230`

> (documented in docs/LITERATURE_REVIEW.md)

**问题** 全文有三处直接引用仓库里的文档或测试文件路径（这里、6.4 的 tests/test_combiner_small.py、附录 A.6 的 docs/T1_*.md）。学位论文的读者只有 PDF，这些指向对他们等于不存在。

**建议** 统一处理：凡是支撑正文数字的，摘进附录；凡是只为存档的，删掉或改成 available from the author。


### 8-13 · ⚪ 可选 · R6 初次读者 · 保持

`en/08_exploratory_negatives.md:252`

> The three explorations point the same way ... it recurs everywhere we pushed.

**问题** 8.4 用三句话收束三节、再指向第 10 章，是全文结构最干净的一处小结。

**建议** 保持。建议把这个格式（三句复述 + 一句出口）作为其他各章小结的模板。

