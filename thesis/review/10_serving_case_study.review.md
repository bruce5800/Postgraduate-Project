# 第 9 章 Application Case Study: Serving — 审读批注

共 8 条：🔴 必改 4 · 🟡 建议 4 · ⚪ 可选 0。

批注原件在 `en/10_serving_case_study.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

文件名是 `10_serving_case_study.md`，但在论文里是第 9 章。

---
### 9-01 · 🔴 必改 · R5 答辩提问者 · 过度自我贬低

`en/10_serving_case_study.md:16`

> It is presented, deliberately, as a case study, not a novelty claim - the systems facts below are known, and the with-predictions vocabulary is a re-labeling of them

**问题** 本章在开头、9.2 末、9.3 末三次声明自己不是贡献，其中一次还说本章的语言只是对已知事实的重新贴标签。考官读完会直接问：那这一章为什么留在论文里。诚实是对的，但需要同时给出这一章的正面价值。

**建议** 保留 case study 的定位，但把价值写出来：它验证了本文的抽象能容纳一个真实系统问题，并且是第 8 章负结果的实验场。三次声明减到一次。


### 9-02 · 🔴 必改 · R2 领域审稿人 · 指标定义不一致

`en/10_serving_case_study.md:38`

> goodput - the fraction of requests served - is the competitive ratio against the b-matching optimum

**问题** 这句把两个不同的量当成同一个：被服务请求的比例，与相对 b-matching 最优的比值。二者只有在最优能服务全部请求时才相等，而本章讨论的正是过载场景。

**建议** 分开定义并选一个作为报告指标：goodput = served/arrived; the competitive ratio = served/OPT。然后检查本章每个数字用的是哪一个。这一处不改，第 9 章所有比值的含义都是含混的。


### 9-03 · 🔴 必改 · R4 体例校对 · 符号冲突

`en/10_serving_case_study.md:49`

> online b-matching: the offline resources are ... each with a capacity c

**问题** 同一句里 b-matching 的 b 与容量 c 指的是同一件事，却用了两个字母；后文图注又写 c = 8。读者会以为 b 和 c 是两个不同的参数。

**建议** 统一用 c，并写明 b-matching with all capacities equal to c；或者反过来全用 b。图注同步。


### 9-04 · 🟡 建议 · R1 二审考官 · 图注缺设置

`en/10_serving_case_study.md:67`

> Capacity as robustness: blindly following the forecast crashes goodput - deeper at ample capacity (c=8) - while the adaptive test stays flat.

**问题** 本章三张图的图注都没有说明用的是哪条 trace、多大规模、多少次重复。第 9 章是最可能被系统方向的读者单独翻阅的一章，图必须能独立看懂。

**建议** 每张图注补一个括号：(Wikipedia trace, n = ..., ... trials)。三张图统一格式。


### 9-05 · 🟡 建议 · R2 领域审稿人 · 机制断言

`en/10_serving_case_study.md:77`

> Capacity is thus a substitute for algorithmic robustness

**问题** substitute 是一个强的机制断言（容量可以替代算法鲁棒性），但证据是一条曲线随 c 变化的形状。二者在什么范围内可互换、代价各是多少，都没有讨论。

**建议** 降为观察加条件：over the capacity range we swept, added capacity buys the same protection that the adaptive test does。或者补一句代价对比（多买一份容量 vs 跑一次前缀测试）。


### 9-06 · 🟡 建议 · R6 初次读者 · 三段并列缺主线

`en/10_serving_case_study.md:103`

> Each of these recovers an established systems result cleanly

**问题** 三个 serving concern 是三段并列，读者读完不知道它们之间是什么关系（前两个说预测不如反应，第三个说反应不如稳定 - 其实是一个漂亮的反转）。9.1 末尾这句只是把它们打包收尾。

**建议** 点破这条主线：the first two say react rather than forecast; the third says the opposite, because cache locality rewards persistence - the objective decides which。这一章最有意思的地方现在是隐藏的。


### 9-07 · 🔴 必改 · R4 体例校对 · 与 8.2 重复且循环引用

`en/10_serving_case_study.md:127`

> the full account is in Chapter 8

**问题** 本节与 8.2 内容几乎逐句重复（同样的 3% 、同样的一格静态预留、同样的两条原因、同样的 a third face of the wall），而且 8.2 写 the serving case study (Chapter 9)、这里写 the full account is in Chapter 8，两节互相指向对方。

**建议** 本节压到两句（结论加指向），正本留在 8.2；删掉其中一处的相互指向，只保留单向。


### 9-08 · 🟡 建议 · R3 英语文字编辑 · 小结重复

`en/10_serving_case_study.md:146`

> The serving instantiation shows the framework reaches a live systems problem and recovers its established results - capacity as a robustness substitute, live load over stale forecasts, stability for cache locality

**问题** 小结把 9.1 的三个小标题原样复述一遍，再加上第三次 not an independent contribution 的声明。

**建议** 小结只留一句：本章证明抽象能落到真实系统上，且连尾延迟目标也没有给预测留出空间。三个小标题读者刚看过。

