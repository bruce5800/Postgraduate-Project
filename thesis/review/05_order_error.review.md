# 第 5 章 What Governs the Loss — 审读批注

共 8 条：🔴 必改 2 · 🟡 建议 6 · ⚪ 可选 0。

批注原件在 `en/05_order_error.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

---
### 5-01 · 🟡 建议 · R5 答辩提问者 · 章标题

`en/05_order_error.md:18`

> Chapter 5. What Governs the Loss: Order Error and ACI's Bound

**问题** 这是全文唯一在章标题里放他人姓名缩写的章。ACI 对领域外读者是无意义的三个字母，而目录是考官最先看到的东西。

**建议** 改成 Order Error and the Known Bound，或 Order Error: What the Known Bound Does and Does Not Say。归属留在正文（5.1 已经写得很好）。


### 5-02 · 🔴 必改 · R4 体例校对 · 符号冲突

`en/05_order_error.md:40`

> at most n - LIS(p[mu]), where p[mu] is the true weights ordered by mu

**问题** 这里的 p 是真实权重向量，而 2.2、3.1 里的 p 是类型分布。同一篇论文用同一个字母指两个不同对象，并且都出现在讨论预测误差的语境中，第 5 章的核心公式因此可能被读错。

**建议** 换字母：把真实权重写成 w，公式变成 n - LIS(w[mu])。改动很小，消除的是一个真实的误读风险。


### 5-03 · 🟡 建议 · R3 英语文字编辑 · 免责声明重复

`en/05_order_error.md:51`

> Thus order-dependence and the zero-effect of a monotone bias are ACI's results, not ours

**问题** 本章在 5.1 末、5.2 开头、5.3 开头三次声明这不是我们的发现。诚实是对的，但三次会变成过度自我设限，读者反而记不住本章真正的贡献。

**建议** 保留 5.1 末的这一处（它在证据旁边，最有说服力），5.3 改成正面陈述本章加了什么，把 not ours 压缩成半句。


### 5-04 · 🟡 建议 · R1 二审考官 · 度量未定义

`en/05_order_error.md:68`

> the normalized Kendall-tau order error

**问题** normalized 的归一化方式没说：0 表示完全一致、1 表示完全反序吗；还是 1 减去相关系数。全章的结论都挂在这个量上，第 7 章还要拿它跨数据集比较。

**建议** 给出定义式或一句话：we report tau normalized to [0,1], where 0 means the predicted order is exactly right and 1 means it is exactly reversed。


### 5-05 · 🟡 建议 · R2 领域审稿人 · 倍数的算法

`en/05_order_error.md:85`

> the realized loss lies far below the bound at every point - by roughly 16x (adversarial) to 75x (distribution-drift)

**问题** 16 倍和 75 倍是怎么算的没有说明：是 bound 除以 loss 的均值，还是在某个特定误差强度上取的比。松紧程度是本章贡献之一，读者需要能复核。

**建议** 写明口径：ratio of the bound to the realized loss, at the strongest corruption level of each model（或你实际用的口径）。


### 5-06 · 🟡 建议 · R2 领域审稿人 · 饱和的证据

`en/05_order_error.md:101`

> For every non-trivial error it is pinned near its maximum (approximately 610 to 673 for n = 1000)

**问题** 饱和这个结论用了一个区间（610 到 673），但没给最大可能值。读者要自己推断 n - LIS 的上界是不是 n = 1000，从而判断 610 到 673 算不算贴顶。

**建议** 补一句参照：out of a maximum of n = 1000, and against realized losses of 8 to 42。三个量放在一起，饱和这个结论才立得住。


### 5-07 · 🔴 必改 · R2 领域审稿人 · 视觉断言缺量化

`en/05_order_error.md:118`

> the four models fall on one increasing curve

**问题** 这是本章最重要的正面结论（Kendall-tau 是统一四个误差结构的量），但支撑它的只有一句对图的目视描述。审稿人会立刻要一个数：单调性有多强、四个模型的点重合到什么程度。

**建议** 给一个统计量：例如四个模型合并后的 Spearman 相关系数，或以 tau 为唯一自变量拟合后的 R^2 与各模型残差。一个数就能把目视断言变成可核查的结果。


### 5-08 · 🟡 建议 · R6 初次读者 · 章太短且无出口

`en/05_order_error.md:137`

> 5.3 Chapter summary

**问题** 全章只有三页，且小结没有说明第 5 章的结论会在哪里被用到（第 7 章用它解释为什么廉价预测器有效、第 8 章用它推出排序学习的想法）。这个因果链是全文最漂亮的一条，值得点破。

**建议** 小结加一句出口：this is why Chapter 7 can explain a cheap predictor's success by its order fidelity, and why Chapter 8 tried to train for order directly。

