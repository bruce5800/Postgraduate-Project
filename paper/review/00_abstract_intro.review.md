# 摘要 + 引言 — 审读批注

共 6 条：🔴 必改 2 · 🟡 建议 4 · ⚪ 可选 0。

批注原件在 `00_abstract_intro.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

---
### 0-01 · 🔴 必改 · P2 领域审稿人 · sharpness 无条件陈述

`00_abstract_intro.md:45`

> For the test-and-fallback class we establish a sharp, two-sided budget-stakes law

**问题** 摘要与引言都把这条律说成 sharp、two-sided、无条件。但 §7.5 的两侧只有在「赌注由常数比例的 specialist mass 以可比信号承载」（Cauchy–Schwarz 那步）时才相接，而 §7.8 自己承认在低信号 sliver 上两侧可以差 sigma^2*eps_W/g 倍，且该情形开放。审稿人对照 §7.8 读摘要，会直接写 the claimed sharpness is conditional and the condition is not stated up front。

**建议** 摘要与引言各加一个限定从句：sharp up to logarithms whenever the stakes are carried by a constant fraction of the specialist mass（并指向 §7.8 的开放情形）。宁可摘要保守，§7 再给完整版。


### 0-02 · 🔴 必改 · P4 体例校对 · 赌注符号三套

`00_abstract_intro.md:55`

> a prefix of length $\tilde\Theta(\sigma^2/g^2)$ ... the squared stakes $g$ ... $\delta \le 2\varepsilon(1-\rho_{\mathrm{base}})$

**问题** 同一个量在摘要与引言里有三个名字：g（stakes）、delta（引言末尾的 stakes cap）、以及 §7.5(ii) 的 delta/Delta（gain/loss）。审稿人读到 delta <= 2 eps (1-rho) 时会以为它和 g 是两个量。

**建议** 全文统一：g = 赌注（scenario pair 的 payoff gap），delta/Delta 只在 Lemma 1 的 gain/loss 语境里出现，并在首次出现处写明二者关系。引言那句 cap 改用 g。


### 0-03 · 🟡 建议 · P3 英语文字编辑 · 摘要过长

`00_abstract_intro.md:66`

> (摘要整体)

**问题** 摘要约 430 词、单段、含四个带公式的从句。ACM/TALG 的摘要通常 200–250 词，且审稿人先读它决定要不要认真读。

**建议** 压到 250 词以内：前三句给问题与实验发现，中间两句给律与它买到什么，最后一句金句。公式只留 sigma^2/g^2 一个。


### 0-04 · 🟡 建议 · P3 英语文字编辑 · 表述歧义

`00_abstract_intro.md:77`

> divided by the squared stakes $g$

**问题** 读作「被平方后的赌注 g 除」，但公式是 sigma^2/g^2，应是」除以赌注 g 的平方」。

**建议** 改成 divided by the square of the stakes $g$。


### 0-05 · 🟡 建议 · P5 审稿意见预演 · novelty 断言的可核查性

`00_abstract_intro.md:88`

> We give the first unified experimental study ... To our knowledge, both the budget-stakes law and the observation that payoff-testing strictly separates from distance-testing in an online algorithm are new

**问题** 两处 first/new 都是可被单条反例推翻的断言，而支撑它们的检索范围只在 §7 与 §9 零散提及。这是单作者投稿最容易被要求补充的地方。

**建议** 在 §9 开头加一句可核对的范围声明（检索了哪些库与会议、关键词、截止时间），并让摘要与 §7 的 new 都指向它。


### 0-06 · 🟡 建议 · P6 初次读者 · 贡献列表过长

`00_abstract_intro.md:98`

> (C1)-(C5) 五条贡献

**问题** 五条贡献占了近一页，C4 与 C5 各自内部又套了三到四个子项。审稿人常常只看这一页就形成初判。

**建议** 每条压到两到三行：一句说贡献是什么，一句说它在哪一节。C4 的实现细节（Jensen 偏差、bootstrap）移到 §5.4。

