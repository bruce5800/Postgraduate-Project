# 第 1 章 Introduction — 审读批注

共 18 条：🔴 必改 4 · 🟡 建议 10 · ⚪ 可选 4。

批注原件在 `en/01_introduction.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

---
### 1-01 · 🟡 建议 · R1 二审考官 · 术语未解释

`en/01_introduction.md:29`

> MinPredictedDegree, which consumes a per-resource degree prediction

**问题** degree 在这里指资源在兼容图上的度数，也就是它会被多少种请求争抢。领域外读者会把它读成随便一个图论量，抓不到这个预测到底预测了什么。

**建议** 补半句功能性解释：a prediction of how many kinds of request will compete for each resource, i.e. how contended it will be。名字可以照留。


### 1-02 · 🟡 建议 · R4 体例校对 · 术语漂移

`en/01_introduction.md:39`

> a hint about which resources will be contended

**问题** 同一个对象在本页出现三个名字：hint、prediction、advice（摘要里也是）。单看都通顺，连起来读者会怀疑是不是三样东西。

**建议** 定一条全篇规则：形式对象一律 prediction；只有在讨论信不信它的时候用 advice，并在此处点明二者同指；hint 只留在这一句的口语解释里，或直接删。定完规则全文 grep 一遍。


### 1-03 · ⚪ 可选 · R6 初次读者 · 保持

`en/01_introduction.md:49`

> consistency, meaning near-optimal performance when the prediction is good, and robustness, meaning ...

**问题** 这两个术语的处理方式（加粗 + 就地一句话释义 + 立刻给出对立面）是全文最好的一处，第一次读的人在这里不会掉队。

**建议** 把它当成全文模板：后面每一个首次出现的核心术语（order error, harness, wall, stakes, resolution）都照这个格式处理一次。


### 1-04 · 🟡 建议 · R3 英语文字编辑 · 长句语序

`en/01_introduction.md:69`

> The algorithms had, moreover, only ever been studied in isolation - each on its own input model, against its own notion of prediction error, and largely through theory - so there was no common ground on which to compare them, quantify how much a prediction actually buys, or explain the gap.

**问题** 一句 55 词里塞了三件事：过去怎么研究的、因此缺什么、以及三个缺什么的并列。moreover 插在 had 和 only 中间也很别扭。

**建议** 拆成两句，并把 moreover 提到句首：Moreover, these algorithms had only ever been studied in isolation - each on its own input model and its own notion of prediction error. There was therefore no common ground on which to compare them or to quantify what a prediction actually buys.


### 1-05 · 🟡 建议 · R6 初次读者 · 段落功能不单一

`en/01_introduction.md:79`

> This gap between the worst-case promise and the average-case reality is the puzzle that motivates this thesis.

**问题** 这一段同时承担了三个功能：给出反直觉现象、指出文献空白、预告本文贡献。第一次读的人不知道该记住哪一句，而这一段其实是全篇的钩子。

**建议** 把 puzzle 那句单独成段作为本章的题眼，文献空白与本文承诺合成下一段。现在的顺序是现象 - 承诺 - 空白 - 再承诺，绕了一圈。


### 1-06 · 🟡 建议 · R1 二审考官 · 缺少基准定义

`en/01_introduction.md:104`

> how much does a prediction help, at what cost, on realistic data?

**问题** 全章反复用 near-optimal、upside、baseline，但从没说清相对什么衡量。读者到第 3 章才知道分母是离线最优 OPT、指标是 ratio。研究问题一节是最需要交代量尺的地方。

**建议** 在这三个问题前加一句：throughout, performance is measured as the ratio of the matching produced to the offline optimum on the same instance。一句话即可，正式定义仍留在第 3 章。


### 1-07 · ⚪ 可选 · R6 初次读者 · 结构映射

`en/01_introduction.md:114`

> The thesis is organized around three questions

**问题** 三个研究问题与紧接着的五条贡献不是一一对应，读者要自己配对。

**建议** 在每条贡献后面用括号标出它回答哪个问题（Q1 / Q2 / Q3），或者把贡献按三问题分成三组。改动很小，收益是读者能立刻看懂论文骨架。


### 1-08 · 🟡 建议 · R1 二审考官 · 术语未解释

`en/01_introduction.md:131`

> places ... on one harness - common graphs, a common structured prediction-error model, a common optimum, and confidence intervals

**问题** harness 是工程口语，学位论文里第一次出现应给个定义；structured prediction-error model 里的 structured 也没说明相对什么（相对独立同分布的随机扰动）。

**建议** harness 首次出现处加同位语：on a single experimental harness (one code path in which every algorithm sees the same instances, the same predictions, and the same optimum)。structured 补一句：errors are injected along the structure of the instance rather than as i.i.d. noise。


### 1-09 · 🔴 必改 · R1 二审考官 · 术语未解释

`en/01_introduction.md:155`

> MinPredictedDegree's loss is governed by a Kendall-tau order error

**问题** Kendall-tau 在这里是第一次出现，且是本条贡献的核心量，却没有任何解释。二审考官读到这条贡献时无法判断它强在哪。

**建议** 加一句话释义：a Kendall-tau order error (the fraction of resource pairs the predictor ranks in the wrong relative order), i.e. only the ranking the predictor induces matters, not the numbers it outputs。最后半句其实才是这条贡献的卖点，现在没说出来。


### 1-10 · ⚪ 可选 · R2 领域审稿人 · 保持

`en/01_introduction.md:165`

> We credit Aamand-Chen-Indyk's Appendix D for the order-dependence itself

**问题** 归属写得很干净，明确区分了前人已有的结论与本文的增量。审稿人对这类主动划界一向加分。

**建议** 保持原样。同样的写法建议复制到第 6 章（Choo/BEM 阈值是他们的，pathology 是你的）和第 5 章。


### 1-11 · 🟡 建议 · R5 答辩提问者 · 可被追问的断言

`en/01_introduction.md:181`

> the first head-to-head comparison of these families / The first empirical study of test-and-fallback

**问题** 一页里两处 first。这两条大概率站得住，但答辩时必然被问：你怎么确定没有别人做过？现场答不上来比不写 first 更伤。

**建议** 正文保留 first，但在第 2.6 节确保有一句可核对的范围声明（检索了哪些库、到什么时间），并把这句准备成答辩的标准答案。


### 1-12 · 🔴 必改 · R2 领域审稿人 · 贡献越界

`en/01_introduction.md:201`

> A quantified account of why the wall stands (Chapter 6 and 10.2): the resolution-limit finding ... is given a theoretical outlook in the conclusion

**问题** 这一条把一个实验发现（6.3 的分辨率极限 + 图 6.4）和一个明确声明未证明的展望（10.2）打包成同一条贡献。审稿人和考官对贡献列表的读法是逐条追证据，而这条的后半截按你自己在 10.3 的说法是没有证据的。

**建议** 拆成两件事：贡献只保留实验部分（分辨率极限在整个难度区间都成立，图 6.4），把 outlook 降为本条末尾的一句话说明其存在，不占 bullet。贡献列表里少一条、但每条都守得住，是更好的交易。


### 1-13 · 🔴 必改 · R5 答辩提问者 · 招问措辞

`en/01_introduction.md:212`

> The full formal development is deliberately deferred to companion work in preparation

**问题** companion work in preparation 在学位论文里会引出两个不想在答辩现场处理的问题：那部分是谁做的、有没有被评审过。

**建议** 改成主体明确、不承诺未来的写法：a fuller formal development is being prepared separately by the author and is not part of this thesis。全文四处提到 companion work，建议只保留 10.3 limitations 里的那一处（见 10-10）。


### 1-14 · 🔴 必改 · R1 二审考官 · 比喻未定义

`en/01_introduction.md:222`

> A quantified account of why the wall stands

**问题** wall 是全篇的核心比喻，在这里第一次出现却没有定义；它的正式说明要到 8.4 才有。第一次读的人只能猜。

**建议** 在这条贡献第一次用 wall 的地方就地定义一次，例如：the wall - the recurring finding that no amount of better prediction or better algorithm moves the average-case ratio appreciably。定义一次之后全文放心复用。


### 1-15 · 🟡 建议 · R3 英语文字编辑 · 条目长度失衡

`en/01_introduction.md:233`

> (bullet 列表整体)

**问题** 五条贡献的长度是 4 / 7 / 5 / 4 / 9 行，第二条和第五条各自套了三个分号从句，读起来像段落而不是要点。

**建议** 每条压到 3 到 4 行：首句一句话说清贡献是什么，细节交给章节引用。列表的价值在于可扫视，现在这个价值被长度吃掉了。


### 1-16 · 🟡 建议 · R4 体例校对 · 跨章重复与循环引用

`en/01_introduction.md:250`

> an attempt to find a serving regime where predictions genuinely help

**问题** 这个 SLO 探针在 8.2 和 9.2 各写了一遍，数字、结论、两条原因几乎逐句相同；而且 8.2 说 The serving case study (Chapter 9)，9.2 说 the full account is in Chapter 8，两节互相把读者推给对方。

**建议** 定一处为正本（建议 8.2，因为它属于负结果章），9.2 压到两句并明确写 we summarise the probe here; the full account is in 8.2。这条不在本次重点章内，但从第 1 章的路线图就能看出来，建议一起处理。


### 1-17 · 🟡 建议 · R6 初次读者 · 路线图同构

`en/01_introduction.md:278`

> Chapter 2 surveys ... Chapter 3 fixes ... Chapter 4 presents ... Chapter 5 examines ...

**问题** 十个句子同一句式排下来，读起来像把目录抄了一遍，读完记不住任何结构。

**建议** 按 1.2 的三个问题分组：先说哪两章建立共同基础（2 到 3），再说哪几章回答 Q1 和 Q2（4 到 7），再说哪几章处理 Q3 与边界（8 到 10）。三句话代替十句，读者反而记得住。


### 1-18 · ⚪ 可选 · R3 英语文字编辑 · 金句复用

`en/01_introduction.md:288`

> on average-case online matching, predictions are robustness insurance rather than a performance lever - and the upside they offer is smaller than the price of finding out whether to trust them.

**问题** 这句金句在摘要、1.4、10.1 三处逐字重复。重复本身是有意的，但三次都用完整长版会稀释它。

**建议** 只在 1.4 和 10.1 用完整版，摘要里用压缩版（或反过来）。同一句话在一篇论文里逐字出现三次，第三次读者会跳过。

