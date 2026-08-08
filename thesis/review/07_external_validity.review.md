# 第 7 章 External Validity — 审读批注

共 11 条：🔴 必改 5 · 🟡 建议 6 · ⚪ 可选 0。

批注原件在 `en/07_external_validity.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

---
### 7-01 · 🟡 建议 · R1 二审考官 · 外部效度的口径

`en/07_external_validity.md:14`

> Chapters 4-6 use synthetic graphs and a synthetic error knob. Is the picture real? We stress it three ways

**问题** 本章开门见山很好，但没说清楚三种压力测试各自替换掉了哪一个合成成分（预测误差来源、图、预测器的训练方式）。读者读完三节后才拼得出来。

**建议** 在这句后加一句对照：7.1 replaces the synthetic error with real drift, 7.2 replaces the synthetic graphs with real ones, 7.3 replaces the hand-made predictor with a learned one。一句话给出本章的骨架。


### 7-02 · 🔴 必改 · R3 英语文字编辑 · 单段承载过多

`en/07_external_validity.md:42`

> Three facts emerge. First, the cost premise does not bite ... Second, the benefit is real, partial, and never harmful ... Third, and why: topology aggregation makes the cheap predictor order-faithful

**问题** 7.1 是一段 15 行，装了三个发现、每个发现两到三个数字、一条机制解释和一个反例。这是全章最有说服力的一节，也是最难读的一节。

**建议** 拆成三段（每个 fact 一段），机制解释单独一段。数字保留，但每段只留最能说明问题的那一个。


### 7-03 · 🔴 必改 · R1 二审考官 · 指标未定义

`en/07_external_validity.md:53`

> a stale forecast captures 27% to 68% of the oracle gap

**问题** gap-capture 这个指标在这里第一次出现且没有定义（应是算法相对基线的提升除以 oracle 相对基线的提升）。它随后在 8.1 又用了一次，是本文用来讲小上升空间的主力指标。

**建议** 就地给定义式：we report gap-capture, (ALG - baseline)/(oracle - baseline)。一行公式，全文两处受益。


### 7-04 · 🟡 建议 · R1 二审考官 · 术语自造

`en/07_external_validity.md:63`

> the cost premise does not bite

**问题** cost premise 是本文自造的说法，指的大概是带预测算法默认预测器很贵这个前提，但正文从未提出过这个前提。读者不知道在反驳谁。

**建议** 先把前提写出来再打掉：the with-predictions literature usually assumes the predictor is an expensive model; here it is a linear-time count（并给出那 0.108 毫秒作为证据）。


### 7-05 · 🟡 建议 · R1 二审考官 · 实验设置缺失

`en/07_external_validity.md:74`

> we map the trace onto a fixed serving topology and consume the forecast through the degree route

**问题** 这个映射是本节外部效度的关键一步（真实 trace 怎么变成二部图），却只有半句。读者无法判断结论有多少来自真实数据、多少来自映射方式的选择。

**建议** 补两句说明映射规则，或指向附录 A.5；并说明映射方式的选择是否影响结论（是否试过别的映射）。


### 7-06 · 🔴 必改 · R2 领域审稿人 · 断言过强

`en/07_external_validity.md:97`

> F3 is universal and confirms its own logic

**问题** universal 用在六个图的样本上过强，尤其本节紧接着就要说 F2 在其中两个图上只是部分成立。审稿人会抓这个词。

**建议** 改成 holds on all six graphs we tested，并把机制解释（上升空间在基线最强处最小）留作真正的论点 - 那才是这一节的价值。


### 7-07 · 🟡 建议 · R2 领域审稿人 · 判据不对称

`en/07_external_validity.md:107`

> F2 holds qualitatively on all six and strictly on the four social/bio graphs (spread 0.22 to 0.29x MPD's)

**问题** strictly 给了判据（spread 倍数），qualitatively 没有。两个词并列出现却只有一个可核查，读者会怀疑 qualitatively 是不是事后放宽的口径。

**建议** 给出 qualitatively 的判据：例如 the augmentations' spread is smaller than naive MPD's on all six。两个判据都写死。


### 7-08 · 🔴 必改 · R5 答辩提问者 · 自我辩护

`en/07_external_validity.md:128`

> This econ boundary is instructive rather than a failure

**问题** 遇到不利结果时先给自己定性（不是失败），是审稿人和考官最敏感的写法之一，反而会让人多看两眼这个边界。后面的解释（图太密、匹配近乎平凡）本身是充分的。

**建议** 删掉这句评价，直接给解释和它的含义：on these two graphs matching is nearly trivial, so there is neither upside to capture nor downside to protect - the mechanism, not an exception。让读者自己得出不是失败的结论。


### 7-09 · 🟡 建议 · R1 二审考官 · 图注不自足

`en/07_external_validity.md:139`

> F1-F3 on six real graphs: naive MPD (red) dips below the Ranking floor everywhere

**问题** 图注用颜色指代算法（red / green / blue），但没有说明六个子图的排布和纵轴范围是否统一。六联图如果纵轴不同，跨图比较就是错的。

**建议** 图注写明：one panel per graph, shared vertical axis (or: axes differ; see values in text)。这一句决定了读者能不能横向读这张图。


### 7-10 · 🔴 必改 · R4 体例校对 · 跨章重复

`en/07_external_validity.md:165`

> rank-training beats regression sharply (0.989 approximately oracle vs 0.974) ... on real temporal features it disappears - identical order (Kendall-tau 0.126 vs 0.126)

**问题** 7.3 与 8.1 讲的是同一组实验、同一批数字（0.989 / 0.974 / 0.126），两处各写一遍。读者读到第 8 章会以为是新实验，核对后发现是同一个。

**建议** 定正本：第 8 章是正本（那里有完整的 M0 到 M3 过程），7.3 压到三句并明确写 the full account is in 8.1。或者反过来，但不要两处都是完整版。


### 7-11 · 🟡 建议 · R6 初次读者 · 章末口径

`en/07_external_validity.md:184`

> On real predictors, real graphs, and a learned predictor, the same wall stands

**问题** 小结把三节压成一句，很好；但 7.2 那两个 econ 图上 F2 只是部分成立的事实在小结里消失了。考官若先读小结再回看正文，会觉得小结报喜不报忧。

**建议** 小结补半句：with one instructive boundary (the two dense economic graphs, 7.2)。诚实的小结反而更有说服力。

