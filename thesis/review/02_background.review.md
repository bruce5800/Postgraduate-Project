# 第 2 章 Background and Related Work — 审读批注

共 13 条：🔴 必改 4 · 🟡 建议 9 · ⚪ 可选 0。

批注原件在 `en/02_background.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

---
### 2-01 · 🟡 建议 · R1 二审考官 · 定义不完整

`en/02_background.md:29`

> Performance is measured by the competitive ratio, the (expected) ratio between the algorithm's matching and an offline optimum

**问题** 括号里的 expected 没说是对什么取期望：到达序列的随机性、算法自身的随机性、还是两者。这个区别在第 3 章会变成 E[ALG]/E[OPT] 还是 E[ALG/OPT] 的选择，此处不交代，读者到第 3 章会以为换了定义。

**建议** 补一句把期望的来源写明：the expectation is over both the random input and the algorithm's own randomness; Chapter 3 fixes the precise form we report。


### 2-02 · 🔴 必改 · R1 二审考官 · 非标准记号

`en/02_background.md:57`

> formally, Known-I.I.D. <= Random-Order in difficulty

**问题** 用小于等于号连接两个模型名是圈内速记，而且方向容易读反：到底谁更难、保证往哪个方向传递。这是全文反复使用的一个论证（10.3 又出现一次），第一次出现就该讲清楚。

**建议** 展开成一句话：every known i.i.d. instance is also a random-order instance, so guarantees proved in the random-order model hold in ours, but not conversely。此后全文可以直接引用这一句。


### 2-03 · 🟡 建议 · R4 体例校对 · 数字精度不一

`en/02_background.md:93`

> first beat it (0.67) ... improved the ratio (to approximately 0.702 and approximately 0.729 respectively)

**问题** 同一串比较里出现两位小数的 0.67 和三位小数的 0.702 / 0.729；而 3.6 又把同样两个界写成 0.670 和 0.729。读者会怀疑 0.67 和 0.670 是不是同一个数。

**建议** 全文统一到三位小数，并在首次出现处标明这些是最坏情况保证（相对于 3.6 的实测值）。


### 2-04 · 🟡 建议 · R6 初次读者 · 读者定位

`en/02_background.md:104`

> This empirical observation - that on typical inputs the simple baseline is already near-optimal - is the seed of the thesis's central finding

**问题** 这句是全章最重要的一句（它是整篇论文的种子），却排在 2.2 的末尾、和一堆比值罗列挤在同一段。第一次读的人很可能滑过去。

**建议** 单独成段，并在句首点明它的地位：One experimental finding in this line is the seed of this thesis。让读者在背景章就记住这一句。


### 2-05 · 🟡 建议 · R6 初次读者 · 单段承载过多

`en/02_background.md:139`

> The paradigm was crystallized by Lykouris and Vassilvitskii ... Wei and Zhang ... the combiner of Chledowski ... Yoshinaga

**问题** 2.3 是一整段 14 行，串了范式定义、缓存起源、最优权衡、combiner、连续退化五条线索，每条一到两句。读者读完记不住哪条与本文有关。

**建议** 拆成三段：范式与两个保证；权衡的理论结果；本文实际会用到的两样东西（combiner 在第 6 章被基准化、连续退化作为对照）。与本文无关的引文压成一句。


### 2-06 · 🔴 必改 · R1 二审考官 · 定义嵌套过深

`en/02_background.md:165`

> n - LIS, the number of resources not in the longest non-decreasing subsequence of the true degrees ordered by the prediction

**问题** 这是全文最难读的一句定义：一句话里套了三层（把真实度数按预测排序、取最长非降子序列、再取补集大小）。而它是第 5 章的主角，读者在这里没读懂，第 5 章就全废了。

**建议** 改成两步走：先说怎么排（list the true degrees in the order the prediction suggests），再说量什么（count how many are out of place - formally n minus the length of the longest non-decreasing subsequence）。再加一句直觉：it is zero exactly when the prediction gets the order right。


### 2-07 · 🔴 必改 · R4 体例校对 · 符号复用

`en/02_background.md:176`

> a prediction of each offline resource's degree (how contended it will be)

**问题** 这里预测对象记作 mu，而 3.3 也用 mu；但 5.1 又写 p[mu]，其中 p 是真实权重——而 p 在 2.2、3.1 里已经是类型分布。同一个字母在同一篇论文里指两个不同对象，且都在讨论预测误差的语境下。

**建议** 把 5.1 的真实权重换个字母（例如 w[mu]），或在 5.1 就地声明这里的 p 与类型分布无关。这一处不改，第 5 章的核心公式会被误读。


### 2-08 · 🟡 建议 · R5 答辩提问者 · 可被追问的评判

`en/02_background.md:203`

> their only lower bound (Choo et al.'s Theorem 3.1) is a generic adversarial indistinguishability result ... and neither proves a lower bound in the stochastic model

**问题** 这是全文对前人工作最强的一句评判，也是本文定位的支点。答辩时会被问：你确认读遍了他们的所有版本和附录吗。现场答不上来，整个定位就松动了。

**建议** 措辞保留，但加一个可核对的限定：in the published versions we examined (arXiv vNN, DATE)。并把 8.3 文献综述的结论与这句显式挂钩，答辩时可以直接引用。


### 2-09 · 🟡 建议 · R5 答辩提问者 · 反复外指

`en/02_background.md:213`

> the full formal development is deferred to companion work

**问题** 这是 companion work 在全文的第五处（另有 1.3、10.2 两处、10.3）。背景章就预告一份读者看不到的稿子，会让人怀疑本论文的完成度。

**建议** 本处删掉，只说本文做到哪一步（Chapter 6 measures it; 10.2 reads the measurement quantitatively）。集中到 10.3 限制一节说明一次即可。


### 2-10 · 🔴 必改 · R2 领域审稿人 · 技术定义不精确

`en/02_background.md:249`

> decide how far p is from q in L1 (total-variation) distance

**问题** L1 距离与总变差距离差一个 1/2 的因子（TV = L1/2）。本章把二者当同义词，而第 6 章的阈值、10.2 的仿射律都对这个常数敏感（例如 tau 约等于 2(1-beta)）。审稿人一定会核对。

**建议** 选定一个并全文统一（建议全用 L1，因为算法和实验都是 L1），在此处明确写 we use the L1 distance throughout; it is twice the total-variation distance。然后回头检查 6.2、6.3、10.2 的每个常数。


### 2-11 · 🟡 建议 · R1 二审考官 · 符号跨章不一致

`en/02_background.md:260`

> samples from an unknown distribution p over a support of size r

**问题** 这里的 r 是分布支撑大小，3.1 的 r 是请求类型数。二者在本文里恰好相等，但从没说破，读者会以为是两个不同的量碰巧同名。

**建议** 加半句点明：here r is the same r as in our model - the number of request types - because the histogram advice is a distribution over types。


### 2-12 · 🟡 建议 · R4 体例校对 · 三套编号不对齐

`en/02_background.md:292`

> Against this background, three gaps stand out

**问题** 本节的三个 gap、1.2 的三个研究问题、1.3 的五条贡献互相不对齐，读者要在三处之间自己配对。三套编号讲的其实是同一件事。

**建议** 让 2.6 的三个 gap 与 1.2 的三个问题一一对应（同序、同措辞），贡献列表再引用这套编号。全文只维护一套骨架。


### 2-13 · 🟡 建议 · R2 领域审稿人 · novelty 断言

`en/02_background.md:302`

> No prior work measures - or bounds - how large a prefix the follow/fallback decision requires on strong-baseline instances

**问题** 第三个 gap 是本文最强的 novelty 断言，但这里只是陈述，没有指向支撑它的检索工作（8.3 有一次专门的先行研究检索）。

**建议** 在这句后面加一个指向：(the prior-art pass behind this claim is described in 8.3)。审稿人和考官顺着这条线就能自己核对。

