# 第 3 章 Model, Algorithms, and Methodology — 审读批注

共 15 条：🔴 必改 5 · 🟡 建议 9 · ⚪ 可选 1。

批注原件在 `en/03_model_methodology.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

---
### 3-01 · 🔴 必改 · R1 二审考官 · 符号密度

`en/03_model_methodology.md:36`

> There is a set R of n offline resources and a type graph on r online types

**问题** 3.1 一节内连续引入 R、n、r、N(l)、m、p、OPT、rho_base 八个符号，之后全篇都在用。读者读到第 6 章要回翻两次才能确认 r 和 k 谁是谁。

**建议** 在 3.1 末尾加一张三行的符号表（符号、含义、典型取值），或至少在附录 A 前加一页符号表并在此处指向它。这是全篇性价比最高的一处补充。


### 3-02 · 🔴 必改 · R2 领域审稿人 · 指标定义需要辩护

`en/03_model_methodology.md:47`

> the competitive ratio is the ratio of the expectation of ALG to the expectation of OPT

**问题** 报告的是期望之比，不是比值的期望，两者一般不相等。这是有意的选择（沿用 Borodin 的惯例，也便于配对试验），但正文没有说明，审稿人会直接问为什么不是 E[ALG/OPT]。

**建议** 补一句理由：we report the ratio of expectations, following Borodin et al., so that a single exactly-computed OPT per instance can be shared across algorithms in paired trials; the two agree to within the reported CIs on our instances（若确实如此，给一个数）。


### 3-03 · 🟡 建议 · R1 二审考官 · 记号未解释

`en/03_model_methodology.md:73`

> Feldman via a cap-{2,1,2} flow network and a blue/red decomposition ... Jaillet-Lu via a cap-{3,2,3} network

**问题** cap-{2,1,2} 和 blue/red decomposition 是原论文的内部术语，这里直接搬来当作已知。不做这两个算法的读者会卡住，而这两个算法在第 4 章 F4 里是主角。

**建议** 各补半句功能性说明：什么容量加在哪一层、蓝红分解产出的是什么。或者干脆只说它们各自预计算一个建议匹配，把构造细节推到脚注。


### 3-04 · 🟡 建议 · R3 英语文字编辑 · 条目过长

`en/03_model_methodology.md:84`

> (3.2 的三个 bullet)

**问题** 三个 bullet 分别是 7、5、8 行，每条内部又用破折号和分号套了两到三层。这里是全篇最需要被快速查阅的一节（读者会反复回来确认某个算法是什么），却是最难扫视的排版。

**建议** 每条压成两句：一句说它是什么，一句说它在本文里的角色。构造细节移到脚注或附录。


### 3-05 · 🟡 建议 · R1 二审考官 · 关键机制一句带过

`en/03_model_methodology.md:101`

> use the MPD rank only as the tie-break of the greedy fallback, so the worst-case-optimal base matching carries the load

**问题** 这句话解释了第 4 章 F2 的全部机制（结构性鲁棒为什么平坦），但只有一句、藏在 bullet 里。F2 是本文两大机制之一。

**建议** 把它提成一个独立小段，并说清楚后果：因为建议只影响并列时的选择，预测再差也动不了主体匹配 - 这既是它不会崩的原因，也是它吃不到上升空间的原因。


### 3-06 · 🟡 建议 · R4 体例校对 · 术语

`en/03_model_methodology.md:120`

> FollowPrediction mimics M-hat - routes every arrival to its type's advice partner

**问题** mimic 是实现里的策略名，正文在这里和 6.4 各出现一次，中间隔了三章。读者第二次遇到时已经忘了。

**建议** 要么正文一律用 advice-following，把 mimic 放进括号说明一次；要么在 3.2 就把它定为正式术语并在 6.4 保持一致。全文只留一个名字。


### 3-07 · 🔴 必改 · R1 二审考官 · 误差模型不可复现

`en/03_model_methodology.md:143`

> four structured error models ... random-flip, systematic-bias, adversarial (reflection of a fraction of entries), and distribution-drift

**问题** 四个误差模型只有名字和半句括注，没有构造式。读者无法判断 adversarial 有多 adversarial、random-flip 的强度参数是什么，也就无法评估第 4、5 章误差扫描的强度是否公平。这是实验类论文最常被要求补充的一处。

**建议** 补一张四行小表：模型名、构造（一句公式即可）、强度参数的取值范围。放这里或附录 A 都行，但正文要有指向。


### 3-08 · 🟡 建议 · R2 领域审稿人 · 误差模型的选择理由

`en/03_model_methodology.md:153`

> each is corrupted by its own knob and reported in a parallel panel

**问题** 两族预测对象用不同的误差旋钮，这是必要的，但也意味着跨面板的数字不可直接比较。第 4 章的表却把三个面板并排放在一起。

**建议** 在这里就写明这一点（the panels are not commensurable across families; only the within-panel comparisons are meaningful），第 4 章表注再重复一次。


### 3-09 · 🟡 建议 · R2 领域审稿人 · 定义与测量不对应

`en/03_model_methodology.md:170`

> robustness is its worst-case ratio under adversarial advice

**问题** 定义说的是最坏情况，实验测的是两个具体档（adversarial 与 garbage）中较低的那个。定义与测量之间的差距没有交代，而 robustness 是全文的核心量之一。

**建议** 写明操作化定义：in the experiments we report the minimum over our corruption levels as a proxy for the worst case, which is a lower bound on the true robustness。


### 3-10 · 🔴 必改 · R2 领域审稿人 · 统计方法

`en/03_model_methodology.md:192`

> Reported ratios are means over trials with 95% normal-approximation confidence intervals

**问题** 两个问题：其一，比值型指标在 40 到 100 次重复下用正态近似，需要说明为何可接受；其二，既然用了配对试验，算法之间的比较应报配对差的置信区间，而不是各自比值的置信区间 - 后者会系统性高估差异的不确定性。第 4 章的结论正是靠这些区间支撑的。

**建议** 至少补一句说明；更好的做法是对关键对比（例如 MPD 与 floor）额外报一次配对差的 CI。这是审稿人最可能要求的补充实验，成本很低。


### 3-11 · ⚪ 可选 · R3 英语文字编辑 · 实现细节过多

`en/03_model_methodology.md:202`

> independent, reproducible streams obtained by NumPy's spawn mechanism - by default four streams (graph, instance, Ranking, Jaillet-Lu)

**问题** 正文写到了具体库的具体机制和默认流数，而附录 A.1 又完整写了一遍。学位论文正文可以更抽象一点。

**建议** 正文只留结论（每个比较里唯一变化的是预测，其余随机性完全对齐），把 spawn 与流的清单交给附录。


### 3-12 · 🟡 建议 · R5 答辩提问者 · 判据的时序

`en/03_model_methodology.md:223`

> we target qualitative agreement, accepting small absolute differences (<= 0.02)

**问题** 0.02 这个容忍度是事前定的还是看到结果后定的，正文没说。答辩老师问这一句的概率不低，因为它决定了复现是否算成功。

**建议** 写明它的来源：例如 the tolerance was fixed in advance from the paper's own reported spread / from the size of our CIs。若确实是事后定的，就诚实写成 we report the observed differences and note that all fall below 0.02。


### 3-13 · 🟡 建议 · R1 二审考官 · 结论前置

`en/03_model_methodology.md:246`

> SimpleGreedy attains its minimum 0.864 at c approximately 4.9, and the greedy variants of the complex algorithms their minima approximately 0.884 at c approximately 5.3

**问题** 这一段把六个数字和三条结论混排在一句里，而复现章真正要传达的只有一件事：我们的实现与已发表结果一致。数字是证据，不是主角。

**建议** 先给一句结论（all five qualitative claims reproduce, with absolute differences below 0.02），再列证据。这样跳读的人一眼就拿到了本节的作用。


### 3-14 · 🔴 必改 · R4 体例校对 · 跨章重复

`en/03_model_methodology.md:274`

> A cross-family observation ... both sit above their worst-case theoretical bounds (0.670 and 0.729) by +0.06 and +0.03

**问题** 这一段与附录 A.4 末尾那段几乎逐字相同（同样的 0.729 / 0.764 / +0.06 / +0.03 和同样的解读）。同一发现在正文和附录各写一遍，读者会以为附录有新内容。

**建议** 定正本：解读留正文，附录只留数字并写 see 3.6 for the reading。或者反过来。两处保持一处即可。


### 3-15 · 🟡 建议 · R2 领域审稿人 · 顺带发现的地位

`en/03_model_methodology.md:285`

> This hints at a universal average-case asymptotic constant distinct from the worst-case guarantee

**问题** 这是一个有意思的顺带发现，但用 universal 和 constant 这样的词写在一个只跑了两个图族的复现小节里，强度偏高。审稿人会问：你测了几个族、有没有理论依据。

**建议** 降一档：the two families happen to converge to the same value here; we do not investigate whether this is universal。保留观察，去掉断言。

