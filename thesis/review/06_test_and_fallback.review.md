# 第 6 章 Test-and-Fallback in Depth — 审读批注

共 17 条：🔴 必改 6 · 🟡 建议 10 · ⚪ 可选 1。

批注原件在 `en/06_test_and_fallback.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

---
### 6-01 · 🔴 必改 · R1 二审考官 · 名称未消歧

`en/06_test_and_fallback.md:18`

> FollowPrediction / TestAndMatch / BEM / Choo

**问题** 本章有四个名字在流通：FollowPrediction、TestAndMatch、Choo、BEM。前两个是策略名，后两个是作者缩写，但正文从未说明 Choo 和 BEM 是同一个 TestAndMatch 的两种变体、还是两个不同算法。6.1 直接写 BEM 0.998 到 0.969；Choo 1.000 到 0.991，读者到这里必须自己反推。

**建议** 在本章导语加一句名称表：we write TestAndMatch for the test-and-fallback scheme in general, and Choo and BEM for its two published instantiations, which differ only in the acceptance threshold。四个名字一次说清，全章受益。


### 6-02 · 🟡 建议 · R3 英语文字编辑 · 导语长句

`en/06_test_and_fallback.md:29`

> This chapter gives their first empirical study: the robustness envelope they achieve (6.1), a counter-intuitive failure of the acceptance threshold (6.2), its recalibration and the resolution limit that recalibration exposes (6.3) - a limit that persists across the whole difficulty range and anchors the theoretical outlook of 10.2 - and a benchmark of the dynamic combiner that explains the commit-once structure (6.4).

**问题** 一句 70 词，四项并列，中间还插了一个破折号从句。章导语是读者决定怎么读这一章的地方，恰恰最不该长。

**建议** 拆成两句：一句列四项（各一个短语），一句单独说 6.3 的分辨率极限是本章通往 10.2 的接口。


### 6-03 · 🟡 建议 · R1 二审考官 · 符号未复述

`en/06_test_and_fallback.md:49`

> few-types instances (n=2000, r=8, prefix k=200, 40 trials)

**问题** 四个符号在第 3 章定义，但读者到这里已经隔了十五页，尤其 r 和 k 很容易记混（r 是类型数还是资源数？k 是前缀长度还是折数？）。

**建议** 括号里就地补词：(n=2000 arrivals, r=8 request types, a prefix of k=200 arrivals, 40 trials)。多几个词，读者不用回翻。


### 6-04 · 🟡 建议 · R2 领域审稿人 · 全称断言

`en/06_test_and_fallback.md:60`

> its prefix test rejects it and it falls back to Ranking, never crashing

**问题** never 是全称量词，而证据是一条误差 sweep、一个图族、40 次重复。审稿人会盯这类词。

**建议** 限定到证据范围：it does not fall below the advice free floor at any point of this sweep。真正的全称结论留给 6.3 的机制解释去承担。


### 6-05 · 🔴 必改 · R1 二审考官 · 数字来源缺失

`en/06_test_and_fallback.md:87`

> the Choo/BEM threshold tau is calibrated to the worst-case baseline beta approximately 0.696

**问题** 0.696 凭空出现。读者（尤其二审）会立刻想：这个数是哪来的、为什么不是 1-1/e。这是本节机制解释的支点，支点没有来源，整个 pathology 的论证就悬空了。

**建议** 补半句出处：beta is the worst case competitive ratio the advice free baseline is proved to achieve in this model (see 2.x / the original paper)。若是你自己算的，写明算法与实例族。


### 6-06 · 🔴 必改 · R3 英语文字编辑 · 信息密度

`en/06_test_and_fallback.md:98`

> as k grows 25 to 800, the ratio falls 0.992 to 0.956 and the misjudgement rate rises 0.00 to 0.60. The mechanism: ... A small noisy prefix over-estimates ell_1 and accidentally rejects the borderline advice (landing safely on the floor); a large accurate prefix correctly measures ell_1 approximately 0.16 < tau and accepts the mildly-bad advice ...

**问题** 一段里有六组数字加一条两步机制解释，其中一句 45 词。这是全章最反直觉的发现，却是最难读的一段，第一次读需要读三遍。

**建议** 改成三段式：第一句只讲现象（更大的测试反而做出更差的决定，给两个数）。第二句讲原因的一半（阈值是按最坏情况基线校准的，而这些实例的基线是 0.99）。第三句讲另一半（小前缀因为噪声误拒而侥幸安全，大前缀准确测量后照章接受了坏建议）。数字各归各句。


### 6-07 · 🟡 建议 · R3 英语文字编辑 · 强调过密

`en/06_test_and_fallback.md:108`

> worse / falls / rises / accidentally rejects / accepts / below

**问题** 这一段有八处斜体强调。强调密度一高，强调就失效，读者反而抓不到哪个才是重点。

**建议** 每段最多留一到两处。本段真正需要强调的只有一个词组：more accurate 却 worse decision。


### 6-08 · 🟡 建议 · R6 初次读者 · 题眼被藏起来

`en/06_test_and_fallback.md:119`

> (landing safely on the floor)

**问题** 错误的原因导致了正确的结果，这是本节最有意思、也最能体现你观察力的一点，现在被塞在括号里一带而过。

**建议** 把它提成独立一句并点名：the small test is right for the wrong reason - it rejects because it is noisy, not because the advice is bad。这句话会成为读者记住这一节的抓手。


### 6-09 · 🔴 必改 · R1 二审考官 · 先用后释

`en/06_test_and_fallback.md:149`

> 6.3 Recalibration, and the resolution limit it exposes

**问题** resolution limit 出现在节标题里，正文到第六行才隐含解释（阈值小于估计量噪声底）。读者带着一个没定义的词读了半页。

**建议** 节的第一句就下定义：by resolution we mean the smallest difference in ell_1 the empirical estimator can distinguish from noise at prefix length k。后面的论证才有依托。


### 6-10 · 🟡 建议 · R2 领域审稿人 · 断言范围

`en/06_test_and_fallback.md:159`

> On strong-baseline instances, no practical empirical-ell_1 threshold can both capture the consistency upside and stay safe

**问题** no ... can 是不可能性断言，而证据是两个具体阈值加一次噪声底估计。practical 和 empirical-ell_1 这两个限定词已经做得很好，但审稿人仍会问：所有阈值都试过了吗。

**建议** 把量词落到证据上：among thresholds of this form, and at the prefix lengths we can afford, none both captures ... 真正的任意规则版本是 10.2 的事，两处的强度要分开。


### 6-11 · 🟡 建议 · R3 英语文字编辑 · 重复

`en/06_test_and_fallback.md:169`

> a better tester only follows whichever threshold more faithfully

**问题** 与 6.2 末句 a more accurate test only follows it more faithfully 几乎同形同义，隔了半页再说一遍，第二次读起来像作者忘了自己写过。

**建议** 6.2 那句改成机制描述，把这句金句留给 6.3 的小结独享。


### 6-12 · 🟡 建议 · R2 领域审稿人 · 估计量缺说明

`en/06_test_and_fallback.md:179`

> smaller than the empirical-ell_1 estimator's noise floor (approximately 0.05 to 0.13)

**问题** 噪声底给了区间但没说这个区间是怎么来的、随什么变化（k？r？重复次数？）。这是本节论证的关键量，也是整篇论文通往 10.2 的桥。

**建议** 补一句：the range spans k from 25 to 800 (noise falls as k grows); it is the standard deviation of the plug in estimate across trials at zero true error。一句话就把这个数从断言变成可复核的量。


### 6-13 · 🟡 建议 · R1 二审考官 · 图注不自足

`en/06_test_and_fallback.md:203`

> as the baseline weakens (left)

**问题** 这是全章最重要的一张图，图注却没说横轴是什么。as the baseline weakens (left) 只是暗示了方向，读者要回正文才知道扫的是类型数 r。图应当能脱离正文被看懂。

**建议** 图注首句直接交代坐标：horizontal axis: number of request types r (fewer types = weaker advice free baseline, shown left); vertical axis: ratio gain over the baseline。然后再讲结论。


### 6-14 · 🔴 必改 · R5 答辩提问者 · 数据来源可疑

`en/06_test_and_fallback.md:228`

> eager switching scores 0.927 - below both the pure follower (1.000) and the pure baseline (0.958; tests/test_combiner_small.py)

**问题** 论文正文的数字引用了一个单元测试文件。答辩时这一定会被问：这是正式实验还是小规模自测、n 多大、重复多少次、有没有置信区间。全章其他数字都有实验设置，只有这一处没有。

**建议** 要么把它升级为一次正式实验并给出与 6.1 同格式的设置与置信区间，要么在正文明说它的地位：a small scale sanity experiment (n=..., ... trials), reported to illustrate the mechanism rather than to measure it。脚本路径移到附录 A 的映射表里。


### 6-15 · 🔴 必改 · R4 体例校对 · 同名不同值

`en/06_test_and_fallback.md:239`

> the pure baseline (0.958) / the advice-free floor (approximately 0.99) / the combiner sits exactly on the floor (0.990)

**问题** 本章出现了三个都叫基线或 floor 的数：0.99、0.990、0.958。它们大概来自不同实例族与不同规模，但正文没有区分，读者只会认为哪里算错了。这是最容易被考官当场指出的不一致。

**建议** 两条都做：给每个数标注它所在的实例设置（一个括号即可），并在本章第一次出现时统一命名（advice free floor 只指 6.1 那个族的数）。若三者本可统一，那就统一。


### 6-16 · 🟡 建议 · R4 体例校对 · 代码名进正文

`en/06_test_and_fallback.md:250`

> switching from Ranking to advice-following (mimic) mid-run

**问题** mimic 是代码里的策略名，在正文这是它第一次也是唯一一次出现，读者不知道它和 advice following 是不是两回事。

**建议** 删掉 mimic，或写成 (called mimic in the implementation)。正文只用一个名字。


### 6-17 · ⚪ 可选 · R6 初次读者 · 小结无出口

`en/06_test_and_fallback.md:269`

> The resolution limit of 6.3 ... is the empirical anchor of the theoretical outlook in 10.2.

**问题** 本章小结只回顾结论，没有告诉读者接下来该带着什么问题读第 7 章。全书各章小结的结构如果一致（回顾 + 出口），阅读节奏会好很多。

**建议** 末尾补一句出口：the next chapter asks whether this picture survives outside synthetic instances。并检查其他各章小结是否都有这样一句。

