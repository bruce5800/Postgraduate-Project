# §4 Order error — 审读批注

共 4 条：🔴 必改 2 · 🟡 建议 2 · ⚪ 可选 0。

批注原件在 `03_order_error.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

---
### 3-01 · 🔴 必改 · P4 体例校对 · 符号复用

`03_order_error.md:28`

> at most $n - \mathrm{LIS}(p[\mu])$, where $p[\mu]$ is the true weights ordered by $\mu$

**问题** 这里的 p 是真实权重向量，而 §2 的 p 是类型分布——两处都在讨论预测误差的语境里。核心公式因此可能被读错。

**建议** 把真实权重换成 w，公式写成 n - LIS(w[mu])，并在首次出现处说明它与类型分布 p 无关。


### 3-02 · 🟡 建议 · P2 领域审稿人 · 倍数口径

`03_order_error.md:53`

> loose by roughly 16x (adversarial) to 75x (distribution-drift)

**问题** 没说这个倍数是怎么取的：界除以损失的均值，还是在某个误差强度上取的比。松紧程度是本节的贡献之一，审稿人需要能复核。

**建议** 写明口径：ratio of the bound to the realized loss at each model's strongest corruption level。


### 3-03 · 🔴 必改 · P2 领域审稿人 · 视觉断言缺量化

`03_order_error.md:80`

> the four structured error models fall on a single increasing curve

**问题** 这是本节的正面结论，支撑它的只有一句对图的目视描述。审稿人一定会要一个数。

**建议** 给统计量。四个模型全部误差水平合并（44 个点）的实测值是 Spearman rho = 0.979、Pearson r = 0.992，各非退化模型内部均不低于 0.97——直接写进正文即可。


### 3-04 · 🟡 建议 · P1 领域外审稿人 · 度量未定义

`03_order_error.md:90`

> the normalized Kendall-tau order error

**问题** normalized 的归一化方式没说：0 表示完全一致、1 表示完全反序吗。第 6 节还要拿它跨数据集比较。

**建议** 给一句：reported on [0,1], where 0 means the predicted order is exactly right and 1 that it is exactly reversed。

