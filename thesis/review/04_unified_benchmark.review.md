# 第 4 章 The Unified Benchmark — 审读批注

共 12 条：🔴 必改 5 · 🟡 建议 6 · ⚪ 可选 1。

批注原件在 `en/04_unified_benchmark.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

---
### 4-01 · 🟡 建议 · R1 二审考官 · 代码名进正文

`en/04_unified_benchmark.md:45`

> Panel A - clvb_zipf

**问题** clvb_zipf 是代码里的生成器标识符，带下划线出现在正文和图表里。读者不知道 clvb 是什么（CLV-B 模型的缩写），也无法从名字看出这个面板测的是什么。

**建议** 正文用可读名（Panel A - heavy-tailed degrees (Zipf)），把 clvb_zipf 作为脚本名放进附录 A 的映射表。第 5 章的 systematic_bias 同理。


### 4-02 · 🟡 建议 · R6 初次读者 · 面板设计的动机

`en/04_unified_benchmark.md:56`

> The panels differ only in the type graph connecting requests to resources

**问题** 三个面板的设计逻辑（一个给度数预测足够信号、一个几乎没有信号、一个是直方图建议的主场）是本章最巧的地方，但被写成了三个并列的 bullet，读者容易当成三组普通实验。

**建议** 在 bullet 前加一句把设计意图说穿：the three panels are chosen so that the degree predictor has strong, weak, and irrelevant signal respectively。


### 4-03 · 🔴 必改 · R4 体例校对 · 方法描述重复

`en/04_unified_benchmark.md:80`

> Every panel runs with paired trials: within a panel, every algorithm and quality level reuses the same graphs, arrival sequences, realized optima ...

**问题** 这一整段与 3.5 的描述几乎逐字相同（配对试验、四条随机流、正态近似 CI）。第二次出现没有新增信息。

**建议** 本段压成一句并指向 3.5：methodology as in 3.5; panel-specific parameters are listed above。省下的篇幅用来解释面板之间为什么不可横向比较（见 3-08）。


### 4-04 · 🔴 必改 · R2 领域审稿人 · 跨面板不可比

`en/04_unified_benchmark.md:91`

> The quality columns instantiate the error models of 3.3 - degree panels: perfect, noisy, adversarial, garbage; advice panel: ... (perfect / mild / bad / garbage)

**问题** 两族的四个质量档语义完全不同（一个是度数向量的结构化扰动，一个是直方图向 eta 混合），却排成同一张表的同名四列。读者的第一反应一定是横向比较 Panel A 的 noisy 与 Panel C 的 mild。

**建议** 在表注里用一句话封死这个误读：columns are comparable within a panel only; the corruption knobs differ across prediction families (3.3)。必要时把 Panel C 的列名改成 eta=0 / 0.3 / 0.6 / 1.0，让它一眼看出是另一套刻度。


### 4-05 · 🔴 必改 · R4 体例校对 · 加粗规则与表注不符

`en/04_unified_benchmark.md:172`

> Bold marks dips below the floor

**问题** 表注说加粗表示跌破 floor，但 Panel C 的 floor 是 0.990，而 FollowPrediction 的 mild=0.832 和 bad=0.679 同样低于 floor，却只有 garbage=0.472 被加粗。规则和标记不一致，是考官翻表时最容易一眼看到的问题。

**建议** 两个选择：把 Panel C 该加粗的三个数都加粗，或者把表注改成 bold marks each algorithm's worst column。无论选哪个，三个面板要用同一条规则。


### 4-06 · 🔴 必改 · R1 二审考官 · 三个 floor 数值差异

`en/04_unified_benchmark.md:184`

> Ranking (floor) 0.948 / Greedy = Ranking (floor) 0.890 / Ranking (floor) 0.990

**问题** 同一张表里 floor 有三个值（0.948、0.890、0.990），第 6 章又出现 0.99 和 0.958。它们来自不同的图族，但表里没有任何提示，读者只会觉得数字对不上。这是全文一致性风险最高的一处（见 CROSS_CHAPTER X-2）。

**建议** 在表注加一句：the floor is instance-dependent; it is Ranking's ratio on that panel's own graph family。并回头统一第 6 章各处 floor 的写法与出处。


### 4-07 · 🔴 必改 · R2 领域审稿人 · 断言范围

`en/04_unified_benchmark.md:218`

> Using either unguarded is strictly worse than using no prediction at all.

**问题** strictly worse 是无条件断言，但同一张表里 MPD 在 perfect 和 noisy 两列都高于 floor（0.989 和 0.956 对 0.948）。这句话只在坏建议下成立。

**建议** 补上条件：under adversarial or garbage advice, using either unguarded is worse than using no prediction at all。一个从句就把一句可被表格直接反驳的话救回来。


### 4-08 · 🟡 建议 · R1 二审考官 · 图注不自足

`en/04_unified_benchmark.md:228`

> The consistency-robustness plane (the data of Table 4.1)

**问题** 这是本章的总结图，图注却没说两个坐标轴各自怎么定义（consistency 用哪一列、robustness 用哪一列）。而这两个量的操作化定义正是 3.4 留下的问题。

**建议** 图注写明：horizontal axis = ratio under perfect advice; vertical axis = ratio under the worst corruption level。读者才能自己核对点位。


### 4-09 · ⚪ 可选 · R6 初次读者 · 保持

`en/04_unified_benchmark.md:245`

> This is the thesis in one panel

**问题** 这句话是全章最好的一处指路，读者读到这里会立刻明白 Panel C 的地位。

**建议** 保持。同类做法可以复制到第 6 章（哪一张图是那一章的题眼）和第 7 章。


### 4-10 · 🟡 建议 · R2 领域审稿人 · 数值呈现

`en/04_unified_benchmark.md:255`

> the advice-free Ranking is already 0.990 and MPD-with-true-degrees is 0.999 - under 0.01 for any advice to add on the good side

**问题** 0.01 这个上升空间是全文的核心量（10.2 的 stakes 就是它），但这里只作为一句顺带的减法出现，也没有给不确定度。既然每个数都有 CI，这个差值也应该有。

**建议** 把它写成一个带不确定度的量：the entire consistency headroom is 0.009 +/- 0.00x - smaller than most of the effects we will measure。这一句会成为第 6 章和 10.2 反复引用的锚点。


### 4-11 · 🟡 建议 · R5 答辩提问者 · 自我表扬式断言

`en/04_unified_benchmark.md:272`

> The prediction does more for the worst-case-designed algorithms than for greedy - a pairing visible only under a unified table.

**问题** visible only under a unified table 是对自己方法论的表扬，而且容易被反驳（分别做两组实验也能看到）。答辩现场这类句子是免费的靶子。

**建议** 去掉 only：a pairing that a unified table makes immediate。观察本身很好，不需要这半句加分。


### 4-12 · 🟡 建议 · R3 英语文字编辑 · 小结与要点重复

`en/04_unified_benchmark.md:290`

> On average-case matching the advice-free baseline is already near-optimal, unguarded prediction-following is unsafe, and the value of the sophisticated algorithms is downside protection

**问题** 章末小结把 F1、F2、F3 又复述了一遍，而它们刚在两页前以加粗标题出现过。

**建议** 小结只留一句本章结论加一句下章出口（第 5 章要问的是：这个小小的损失由什么决定）。

