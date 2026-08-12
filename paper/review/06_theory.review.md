# §7 Budget–stakes law — 审读批注

共 7 条：🔴 必改 4 · 🟡 建议 3 · ⚪ 可选 0。

批注原件在 `06_theory.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

---
### 6-01 · 🔴 必改 · P2 领域审稿人 · sharp 的条件被省略

`06_theory.md:51`

> and this is *sharp*: below $k^*$ no decision rule whatsoever can be simultaneously consistent and robust (Theorem 1(i)), while at $k^*$ an explicit rule succeeds

**问题** Theorem 1(i) 给的不可能性门槛是 k = o(1/(eps_W * g))，不是 o(sigma^2/g^2)；两者只在 Cauchy-Schwarz 那一步的条件下相接，而 §7.8 承认在低信号 sliver 上可差 sigma^2*eps_W/g 倍。本节开头把 sharp 说成无条件的，审稿人读到 §7.8 会认为前面在过度宣称。

**建议** 本节开头就把条件写出来：sharp up to logarithms whenever the stakes are carried, at comparable signal levels, by a constant fraction of the specialist mass；并直接指向 §7.8 的开放情形。


### 6-02 · 🟡 建议 · P1 领域外审稿人 · 记号易误读

`06_theory.md:158`

> $\sigma^2 := \sum_i \theta_i / N$

**问题** sigma^2 被定义为一个概率（随机到达是 specialist 的概率），却写成一个平方；文中从未定义 sigma 本身，直到 §7.6 才出现 g* = sigma/sqrt(n)。领域外审稿人会去找 sigma 的定义。

**建议** 在定义处点明：我们把它记作 sigma^2 是因为它同时是决策统计量的方差上界，sigma 即其平方根，§7.6 会用到。


### 6-03 · 🟡 建议 · P2 领域审稿人 · 闭式常数无推导

`06_theory.md:200`

> In closed form (verified numerically), cell $i$ has OPT = 1 + theta_i, baseline 1 + theta_i/2

**问题** 整节的定量结论都建立在这三个 cell 常数上，正文只说「闭式（数值验证过）」而不给推导。审稿人要么自己推一遍，要么要求补附录。

**建议** 把两行推导放进附录，正文指过去；数值验证保留但不作为唯一依据。


### 6-04 · 🔴 必改 · P4 体例校对 · 赌注符号在定理内部就不一致

`06_theory.md:237`

> payoff gap $g=\frac2N\sum_{i\in W}\theta_i\varepsilon_i$ ... on which following gains $\ge\delta$ and loses $\ge\Delta$ ... $k \ge C(\sigma^2/\min(\delta,\Delta)^2)$

**问题** Theorem 1 的 (i) 用 g、(ii) 用 delta/Delta，而结论写成 sigma^2/g^2。三者的关系（g 与 min(delta,Delta) 是否同阶）没有写明，读者无法确认两侧真的在比较同一个量。

**建议** 在定理陈述前统一符号，并写明 (i) 的 g 与 (ii) 的 min(delta,Delta) 在何种意义下同阶——这正是两侧能相接的关键，不能留给读者推断。


### 6-05 · 🔴 必改 · P5 审稿意见预演 · 主定理只有证明草图

`06_theory.md:252`

> *Proof sketch of (i).*

**问题** 本文的核心定理，下界一侧只给了 proof sketch（耦合、每样本 Hellinger、张量化、代入 Lemma 1）。TALG 的审稿人对主定理通常要求完整证明；作者自己的 PROOF STATUS 备注里也写着」typeset the two short proofs in the appendix」，这件事还没做。

**建议** 把 (i) 的完整证明写进附录：耦合的构造、per-sample Hellinger 的那步等式如何得到、张量化与 joint convexity 的引用出处，以及 o(1) 的含义。既然作者自己说这两个证明很短，补上的成本远小于被要求 major revision 的成本。


### 6-06 · 🔴 必改 · P2 领域审稿人 · 推论继承了未声明的条件

`06_theory.md:306`

> Corollary (uncapturable upsides): every advice upside smaller than Theta(sqrt((1-rho_base)/n)) is uncapturable by any test-and-fallback rule at any prefix length k <= n

**问题** 这是全文最强、也最会被引用的一句。它由」Theorem 1 places the feasibility frontier at g ~ sigma/sqrt(k)」推出，而这个 frontier 的」and no further」方向来自 (i)，因而继承了 §7.5 那个 Cauchy-Schwarz 条件；推论本身却是无条件陈述的。

**建议** 把条件写进推论（on families where the two sides of Theorem 1 meet），或把它降为 under the conditions of Theorem 1。这一处不改，§7.8 的诚实声明会与推论直接冲突。


### 6-07 · 🟡 建议 · P5 审稿意见预演 · 不可核查的出处

`06_theory.md:372`

> a dedicated novelty pass (recorded in the project archive) found no payoff-testing acceptance rule

**问题** project archive 对审稿人不存在。而这句支撑的是本文第二项新颖性主张。

**建议** 把检索范围写进 §9（库、关键词、截止时间），正文指向 §9 而不是 archive。

