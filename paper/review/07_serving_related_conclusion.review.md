# §8–10 Serving / related / conclusion — 审读批注

共 4 条：🔴 必改 1 · 🟡 建议 3 · ⚪ 可选 0。

批注原件在 `07_serving_related_conclusion.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

---
### 7-01 · 🟡 建议 · P5 审稿意见预演 · 重复声明

`07_serving_related_conclusion.md:35`

> We present this as a **case study, not a novelty claim** ... Serving therefore stays a case study.

**问题** 同一节里两次声明本节不是贡献。诚实是对的，但两次会让审稿人问：那它为什么占一节。

**建议** 保留一次，并把这一节的正面价值写出来（它验证抽象能落到真实系统，并且是 §6.3 负结果的实验场）。


### 7-02 · 🟡 建议 · P2 领域审稿人 · 对文献的全称断言

`07_serving_related_conclusion.md:62`

> none of these tests the payoff, and none commits once

**问题** 对一整条文献线的全称否定。只要审稿人想到一个反例，这句话就成了扣分项——而 test-before-trust 那一线正是活跃的、且作者自己也说是直接对手。

**建议** 限定到检索到的范围：among the works we surveyed (§9), none tests the payoff。并与 0-05 的范围声明挂钩。


### 7-03 · 🟡 建议 · P1 领域外审稿人 · 非标准记号

`07_serving_related_conclusion.md:107`

> since Known-IID $\le$ Random-Order

**问题** 用小于等于号连接两个模型名是圈内速记，方向也容易读反。领域外审稿人会停顿。

**建议** 展开：every known-i.i.d. instance is also a random-order instance, so guarantees proved there carry over to ours, but not conversely。


### 7-04 · 🔴 必改 · P4 体例校对 · 与 §7 自相矛盾

`07_serving_related_conclusion.md:127`

> as is the novelty of payoff-estimating acceptance rules ... (a dedicated pass is in progress)

**问题** §10 的局限说新颖性检索「正在进行中」，而 §7.8 与 §7 开头都说这次检索已经完成并给出了结论。同一篇稿子里两处直接冲突，审稿人一定会发现。

**建议** 统一口径：既然 §7 说已完成，§10 这一条要么删掉，要么改成「检索已完成、结论见 §9，但覆盖面有限」。

