# 审读总表

八个单元（摘要+引言、§2–§10）共 **37 条**批注，七个审稿视角。

按视角与严重度：

| 视角 | 🔴 必改 | 🟡 建议 | ⚪ 可选 | 合计 |
|---|---|---|---|---|
| P1 领域外审稿人 | 1 | 3 | 0 | 4 |
| P2 领域审稿人 | 9 | 5 | 0 | 14 |
| P3 英语文字编辑 | 0 | 2 | 0 | 2 |
| P4 体例校对 | 6 | 0 | 0 | 6 |
| P5 审稿意见预演 | 1 | 5 | 0 | 6 |
| P6 初次读者 | 0 | 1 | 0 | 1 |
| P7 复现审稿人 | 3 | 1 | 0 | 4 |
| **合计** | **20** | **17** | **0** | **37** |

按单元：

| 单元 | 🔴 | 🟡 | ⚪ | 清单 |
|---|---|---|---|---|
| 摘要 + 引言 | 2 | 4 | 0 | [00_abstract_intro.review.md](00_abstract_intro.review.md) |
| §2 Setup | 1 | 1 | 0 | [01_setup.review.md](01_setup.review.md) |
| §3 Unified benchmark | 3 | 1 | 0 | [02_unified_benchmark.review.md](02_unified_benchmark.review.md) |
| §4 Order error | 2 | 2 | 0 | [03_order_error.review.md](03_order_error.review.md) |
| §5 Test-and-fallback | 4 | 1 | 0 | [04_test_and_fallback.review.md](04_test_and_fallback.review.md) |
| §6 External validity | 3 | 2 | 0 | [05_external_validity.review.md](05_external_validity.review.md) |
| §7 Budget–stakes law | 4 | 3 | 0 | [06_theory.review.md](06_theory.review.md) |
| §8–10 Serving / related / conclusion | 1 | 3 | 0 | [07_serving_related_conclusion.review.md](07_serving_related_conclusion.review.md) |

---

## 🔴 必改（20 条）

- **0-01** sharpness 无条件陈述 · P2 领域审稿人 — 摘要与引言都把这条律说成 sharp、two-sided、无条件。但 §7.5 的两侧只有在「赌注由常数比例的 spec… （`00_abstract_intro.md:45`）
- **0-02** 赌注符号三套 · P4 体例校对 — 同一个量在摘要与引言里有三个名字：g（stakes）、delta（引言末尾的 stakes cap）、以及 §7.5(i… （`00_abstract_intro.md:55`）
- **1-01** 未解析的交叉引用 · P7 复现审稿人 — 这是一个没被替换掉的占位符，它已经原样印进 talg_main.pdf 的正文（第 3 页）。而且论文里并没有复现附录—… （`01_setup.md:112`）
- **2-01** 代码名进正文 · P4 体例校对 — clvb_zipf 是生成器标识符，带下划线出现在表里。审稿人不知道 clvb 是什么，也看不出这个面板测的是什么。… （`02_unified_benchmark.md:56`）
- **2-02** 三个 floor 不可比 · P4 体例校对 — 三个面板的 floor 是三个不同的数，来自不同图族，表里没有任何提示；两族的质量列语义也不同却同名并排。审稿人第一反应… （`02_unified_benchmark.md:67`）
- **2-03** 无条件断言 · P2 领域审稿人 — strictly worse off 是无条件的，但同一张表里 MPD 在 perfect 与 noisy 两列都高于 … （`02_unified_benchmark.md:99`）
- **3-01** 符号复用 · P4 体例校对 — 这里的 p 是真实权重向量，而 §2 的 p 是类型分布——两处都在讨论预测误差的语境里。核心公式因此可能被读错。… （`03_order_error.md:28`）
- **3-03** 视觉断言缺量化 · P2 领域审稿人 — 这是本节的正面结论，支撑它的只有一句对图的目视描述。审稿人一定会要一个数。… （`03_order_error.md:80`）
- **4-01** 全称断言 · P2 领域审稿人 — never 是全称量词，证据是一条误差 sweep、一个图族、40 次重复。… （`04_test_and_fallback.md:37`）
- **4-02** 常数无出处 · P1 领域外审稿人 — 0.696 凭空出现。领域外审稿人会问它是哪来的、为什么不是 1-1/e。它是本节机制解释的支点。… （`04_test_and_fallback.md:73`）
- **4-04** 把 sigma^2 悄悄设成 1 · P2 领域审稿人 — §7 的预算是 sigma^2/g^2，这里直接写成 1/g^2，等于把 sigma^2 取成 1 而只用一个从句带过。… （`04_test_and_fallback.md:163`）
- **4-05** 用单元测试当证据 · P7 复现审稿人 — 论文正文的数字引用了一个单元测试文件。实际规模是 n=600、r=6、单个种子、不做平均——全节其他数字都有实验设置，只… （`04_test_and_fallback.md:205`）
- **5-01** 指向仓库内部文档 · P7 复现审稿人 — 第 6 节正文三次把读者指向仓库里的 markdown 笔记。审稿人只有 PDF，这些指向对他们等于不存在；而它们支撑的… （`05_external_validity.md:28`）
- **5-02** 算术与断言 · P2 领域审稿人 — 两处问题。其一，0.883-0.782 = 0.101，四舍五入是 0.10 不是 0.11，而括号里的两个数就在同一句… （`05_external_validity.md:67`）
- **5-03** universal · P2 领域审稿人 — universal 用在六个图的样本上过强，而紧接着就要说 F2 在其中两个图上只是部分成立。… （`05_external_validity.md:78`）
- **6-01** sharp 的条件被省略 · P2 领域审稿人 — Theorem 1(i) 给的不可能性门槛是 k = o(1/(eps_W * g))，不是 o(sigma^2/g^2… （`06_theory.md:51`）
- **6-04** 赌注符号在定理内部就不一致 · P4 体例校对 — Theorem 1 的 (i) 用 g、(ii) 用 delta/Delta，而结论写成 sigma^2/g^2。三者的… （`06_theory.md:237`）
- **6-05** 主定理只有证明草图 · P5 审稿意见预演 — 本文的核心定理，下界一侧只给了 proof sketch（耦合、每样本 Hellinger、张量化、代入 Lemma 1… （`06_theory.md:252`）
- **6-06** 推论继承了未声明的条件 · P2 领域审稿人 — 这是全文最强、也最会被引用的一句。它由」Theorem 1 places the feasibility frontie… （`06_theory.md:306`）
- **7-04** 与 §7 自相矛盾 · P4 体例校对 — §10 的局限说新颖性检索「正在进行中」，而 §7.8 与 §7 开头都说这次检索已经完成并给出了结论。同一篇稿子里两处… （`07_serving_related_conclusion.md:127`）

## 🟡 建议（17 条）

- **0-03** 摘要过长 · P3 英语文字编辑 — 摘要约 430 词、单段、含四个带公式的从句。ACM/TALG 的摘要通常 200–250 词，且审稿人先读它决定要不要… （`00_abstract_intro.md:66`）
- **0-04** 表述歧义 · P3 英语文字编辑 — 读作「被平方后的赌注 g 除」，但公式是 sigma^2/g^2，应是」除以赌注 g 的平方」。… （`00_abstract_intro.md:77`）
- **0-05** novelty 断言的可核查性 · P5 审稿意见预演 — 两处 first/new 都是可被单条反例推翻的断言，而支撑它们的检索范围只在 §7 与 §9 零散提及。这是单作者投稿… （`00_abstract_intro.md:88`）
- **0-06** 贡献列表过长 · P6 初次读者 — 五条贡献占了近一页，C4 与 C5 各自内部又套了三到四个子项。审稿人常常只看这一页就形成初判。… （`00_abstract_intro.md:98`）
- **1-02** 外部数据前提 · P7 复现审稿人 — 第 6、8 节的真实图与 trace 结果需要先获取外部数据，而这句话让审稿人以为克隆代码即可复现全部。artifact… （`01_setup.md:122`）
- **2-04** 自我表扬 · P5 审稿意见预演 — visible only 是对自己方法论的表扬，且容易被反驳（分别做两组实验也能看到）。审稿意见里这类句子是免费靶子。… （`02_unified_benchmark.md:136`）
- **3-02** 倍数口径 · P2 领域审稿人 — 没说这个倍数是怎么取的：界除以损失的均值，还是在某个误差强度上取的比。松紧程度是本节的贡献之一，审稿人需要能复核。… （`03_order_error.md:53`）
- **3-04** 度量未定义 · P1 领域外审稿人 — normalized 的归一化方式没说：0 表示完全一致、1 表示完全反序吗。第 6 节还要拿它跨数据集比较。… （`03_order_error.md:90`）
- **4-03** 估计量缺说明 · P2 领域审稿人 — 噪声底给了区间但没说怎么估的、随什么变化。它是 §5.3 到 §7 的桥。… （`04_test_and_fallback.md:101`）
- **5-04** 自我辩护 · P5 审稿意见预演 — 遇到不利结果先给自己定性，是审稿人最敏感的写法之一，反而会让人多看两眼这个边界。后面的解释本身已经充分。… （`05_external_validity.md:102`）
- **5-05** 负结果的覆盖面 · P2 领域审稿人 — 这是本节最有分量的负结果，支撑它的是一句 every ... we tried，但配置清单没给。负结果的说服力全在覆盖面… （`05_external_validity.md:129`）
- **6-02** 记号易误读 · P1 领域外审稿人 — sigma^2 被定义为一个概率（随机到达是 specialist 的概率），却写成一个平方；文中从未定义 sigma … （`06_theory.md:158`）
- **6-03** 闭式常数无推导 · P2 领域审稿人 — 整节的定量结论都建立在这三个 cell 常数上，正文只说「闭式（数值验证过）」而不给推导。审稿人要么自己推一遍，要么要求… （`06_theory.md:200`）
- **6-07** 不可核查的出处 · P5 审稿意见预演 — project archive 对审稿人不存在。而这句支撑的是本文第二项新颖性主张。… （`06_theory.md:372`）
- **7-01** 重复声明 · P5 审稿意见预演 — 同一节里两次声明本节不是贡献。诚实是对的，但两次会让审稿人问：那它为什么占一节。… （`07_serving_related_conclusion.md:35`）
- **7-02** 对文献的全称断言 · P2 领域审稿人 — 对一整条文献线的全称否定。只要审稿人想到一个反例，这句话就成了扣分项——而 test-before-trust 那一线正… （`07_serving_related_conclusion.md:62`）
- **7-03** 非标准记号 · P1 领域外审稿人 — 用小于等于号连接两个模型名是圈内速记，方向也容易读反。领域外审稿人会停顿。… （`07_serving_related_conclusion.md:107`）

## ⚪ 可选（0 条）


