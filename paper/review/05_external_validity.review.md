# §6 External validity — 审读批注

共 5 条：🔴 必改 3 · 🟡 建议 2 · ⚪ 可选 0。

批注原件在 `05_external_validity.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

---
### 5-01 · 🔴 必改 · P7 复现审稿人 · 指向仓库内部文档

`05_external_validity.md:28`

> docs/REAL_PREDICTOR.md / docs/REALWORLD_ROBUSTNESS.md / docs/RANK_LEARNING_M0_M3.md

**问题** 第 6 节正文三次把读者指向仓库里的 markdown 笔记。审稿人只有 PDF，这些指向对他们等于不存在；而它们支撑的是本节的主要数字。

**建议** 凡支撑正文数字的，摘进复现附录；其余删掉。脚本路径可以保留（artifact 里有），docs/*.md 不行。


### 5-02 · 🔴 必改 · P2 领域审稿人 · 算术与断言

`05_external_validity.md:67`

> by 0.07 (Caltech36: 0.843<0.913) to 0.11 (CE-PG: 0.782<0.883)

**问题** 两处问题。其一，0.883-0.782 = 0.101，四舍五入是 0.10 不是 0.11，而括号里的两个数就在同一句里，审稿人一眼能验算。其二，最小跌幅其实是 Reed98 的 0.063，不是 Caltech36 的 0.070。

**建议** 改成 by 0.06 (Reed98) to 0.10 (CE-PG)，或保留 Caltech36 作为例子但把区间端点写对。


### 5-03 · 🔴 必改 · P2 领域审稿人 · universal

`05_external_validity.md:78`

> F3 is universal and confirms its own logic

**问题** universal 用在六个图的样本上过强，而紧接着就要说 F2 在其中两个图上只是部分成立。

**建议** 改成 holds on all six graphs we tested；机制解释（上升空间在基线最强处最小）才是这一节的价值。


### 5-04 · 🟡 建议 · P5 审稿意见预演 · 自我辩护

`05_external_validity.md:102`

> This econ boundary is instructive rather than a failure

**问题** 遇到不利结果先给自己定性，是审稿人最敏感的写法之一，反而会让人多看两眼这个边界。后面的解释本身已经充分。

**建议** 删掉这句评价，直接给解释：那两个图太稠密，匹配近乎平凡，既无上升空间可抓也无多少下行需保护——这是 F3 的机制在起作用，不是它的例外。


### 5-05 · 🟡 建议 · P2 领域审稿人 · 负结果的覆盖面

`05_external_validity.md:129`

> across every topology and lag we tried

**问题** 这是本节最有分量的负结果，支撑它的是一句 every ... we tried，但配置清单没给。负结果的说服力全在覆盖面。

**建议** 把实际配置写进正文一句：150 个上下文长度类型、500 个度数为 8 的副本、40 个窗口、三个滞后特征、60/40 划分；若确实扫过多组拓扑与滞后，把清单也列出来。

