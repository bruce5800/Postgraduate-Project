<!--
Draft §7 — the budget–stakes law (C5, Direction C — REVISED 2026-07-27). THE CENTERPIECE.
Sources: docs/T1_PROOF_SKELETON.md (Lemma 1), T1_W1_single_cell.md (cell constants),
T1_W2_W3a_closeout.md (affine law), T1_WITNESS_GAP.md (payoff identity, refutation of the
tolerant-testing route, T1' both halves). Figure 8 = impossibility_frontier.png,
Figure 9 = directional_rsweep.png (§7.7).
Verification scripts: scripts/verify_witness_gap.py (payoff identity, directional test,
plug-in-l1 blindness), plus the W1/W3a checks referenced in Appendix.

[PROOF STATUS — for the authors, delete before submission]
The earlier draft stated a sublinear-test impossibility for ANY rule at k = o(n/log n) via
a reduction to tolerant identity testing. That theorem is FALSE — attempting the witness
step refuted it (see docs/T1_WITNESS_GAP.md): on the cell family the follow-payoff equals
half the mean of a per-sample observable, so a directional rule succeeds at k = O(log n).
This section now states what is true instead: a sharp budget–stakes law (Theorem 1, both
halves elementary — Bernstein/Hoeffding upper, Hellinger + Lemma 1 lower). Lemma 1 and the
affine law carry over unchanged. GENERALIZED 2026-07-28: heterogeneous profiles
(theta_i, eps_i) + magnitude-free achievability, organized around the specialist mass
sigma^2 = sum theta_i/N with the exact identity 1-rho_base = sigma^2/2; verified by
scripts/verify_budget_stakes_hetero.py (see docs/T1_HETERO_GENERAL.md). Remaining before
submission (single-author as of 2026-07-28): the author's own line-by-line verification
of this section. Proof of (i) typeset in Appendix B 2026-08-13 (from the sketch here
plus T1_HETERO_GENERAL fact 3) — NEEDS THE AUTHOR'S CHECK; (ii)'s Bernstein proof is
already inline. Novelty pass DONE
2026-07-29 (docs/NOVELTY_PAYOFF_TEST.md) — no payoff-testing acceptance rule found in the
adjacent lines; positioning debts (test-before-trust, data-driven selection, Wald) paid
in the intro paragraph and §9.

Differentiation to defend (put up front): Choo's threshold τ=2(n̂/n−β)−ε couples to the
baseline β CONSTRUCTIVELY; our lower bound is information-theoretic (any prefix rule).
And our positive result says the field's ℓ₁-testing lens is the wrong statistic on
average-case inputs — the decision-relevant functional (the payoff) is exponentially
cheaper to test than the distribution distance.
-->

# 7. A Budget–Stakes Law: What a Sublinear Test Can and Cannot Buy

Every experiment above met the same wall: on average-case matching the advice-free baseline
is near-optimal, so predictions buy robustness insurance rather than performance, and — for
the test-and-fallback algorithms — no acceptance threshold both captures the (tiny) upside
and stays safe (§5.3). This section quantifies the wall. The result is a two-sided
**budget–stakes law**: on a natural instance family, deciding whether to follow the advice
requires a prefix of length $k^* = \tilde\Theta(\sigma^2/g^2)$ — the instance's
specialist mass (exactly twice its baseline slack) divided by the square of the stakes
$g$ — with **no** decision rule whatsoever simultaneously consistent and robust below the
budget (Theorem 1(i)) and an explicit, embarrassingly simple rule succeeding at it
(Theorem 1(ii)). The two sides meet, up to logarithms, whenever the stakes are carried at
comparable signal levels by a constant fraction of the specialist mass — the condition
under which "$k^*$" names one quantity rather than two; when instead the stakes hide in a
vanishing sliver of low-signal cells the sides can separate, and we leave that regime open
(§7.8). The
corollary is the wall: stakes are capped by the baseline slack, so on strong-baseline
instances meeting that condition the required prefix exceeds the entire horizon — any
upside smaller than
$\approx 2\sqrt{(1-\rho_{\mathrm{base}})/n}$ is uncapturable at *every* $k\le n$, and the
upsides we measured in §3–§5 sit in exactly that range.

<!--REV
id: 6-01
role: P2 领域审稿人
level: 必改
kind: sharp 的条件被省略
quote: and this is *sharp*: below $k^*$ no decision rule whatsoever can be simultaneously consistent and robust (Theorem 1(i)), while at $k^*$ an explicit rule succeeds
note: Theorem 1(i) 给的不可能性门槛是 k = o(1/(eps_W * g))，不是 o(sigma^2/g^2)；两者只在 Cauchy-Schwarz 那一步的条件下相接，而 §7.8 承认在低信号 sliver 上可差 sigma^2*eps_W/g 倍。本节开头把 sharp 说成无条件的，审稿人读到 §7.8 会认为前面在过度宣称。
fix: 本节开头就把条件写出来：sharp up to logarithms whenever the stakes are carried, at comparable signal levels, by a constant fraction of the specialist mass；并直接指向 §7.8 的开放情形。
-->

En route we record an honest negative of independent interest (§7.7): the natural
conjecture — that the $\tilde\Theta(r/\log r)$ hardness of *tolerant distribution testing*
[CJKL22, VV11, JHW18] makes the follow/fallback decision itself hard for any rule at
sublinear $k$ — is **false**. The advice's *distance* $\ell_1(p,q)$ is indeed hard to test,
and the empirical-$\ell_1$ rules the field actually uses [Choo24, BEM26] are provably blind
at $k \ll r$; but the decision-relevant functional is the *payoff* of following, which on
decomposable instances collapses to a per-sample observable. Testing the payoff is
exponentially cheaper than testing the prediction.

**Relation to prior work.** Choo et al. [Choo24] and Burathep–Erlebach–Moses [BEM26] give
*upper* bounds (algorithms) in this model and no statistical lower bound; Choo et al.'s
Thm 3.1 is the generic adversarial trade-off (no algorithm is $1$-consistent and
$>\tfrac12$-robust), driven by adversarial instances, not by the resolution of a sublinear
test. Their acceptance threshold $\tau = 2(\hat n/n-\beta)-\varepsilon$ couples to the
baseline $\beta$ *constructively*; Theorem 1(i) is the information-theoretic counterpart —
it binds *every* measurable rule on the prefix. The consistency/robustness lower bounds
elsewhere in the with-predictions literature [WZ20] are problem-intrinsic Pareto frontiers,
not gated by a test. Tolerant-testing sample complexity [CJKL22] enters our story twice,
both times off the critical path: it explains *why* the field's $\ell_1$-threshold rules
are blind (§7.7), and its hard instances are exactly what our payoff identity (Lemma 2)
sidesteps. To our knowledge, both the budget–stakes law and the observation that
payoff-testing strictly separates from distance-testing in an online algorithm are new.
A dedicated pass over the adjacent lines (§9) found none testing the payoff: the
*test-before-trust* program of Choo, Gouleakis and coauthors [Choo24, BCJG25] validates
advice by distributional distance throughout — exactly the statistic §7.7 shows is the
wrong one on average-case inputs; switching frameworks [Chl21, ASSS25] switch dynamically
on prediction quality or regret rather than committing on a payoff test, and matching's
irrevocability breaks them (§5.5); data-driven algorithm selection [GR17, Bal20] chooses
among algorithms from samples of *whole instances* with observable per-instance
performance, whereas here a single instance's prefix must reveal a policy's full-horizon
value — which is what the payoff identity provides; and the $1/g^2$ budget echoes
classical sequential analysis [Wald47], whose engine — not its novelty — Lemma 2 imports
into matching.

## 7.1 The test-and-fallback class

Fix an instance family and a budget $k=o(n)$. A **test-and-fallback** algorithm $A_k$
observes the first $k$ arrivals $X_{1:k}$ and the advice $\sigma$, outputs a (possibly
randomized) decision $D\in\{\mathsf{Follow},\mathsf{Fallback}\}$ as a function of
$(X_{1:k},\sigma)$, and thereafter Mimics $\sigma$ if $D=\mathsf{Follow}$ and runs the
advice-free baseline $B$ (Ranking) otherwise. Because $k=o(n)$, the prefix's own
contribution to the ratio is $O(k/n)=o(1)$, absorbed below. Write $\rho_{\mathrm{base}} =
\mathbb E[B]/\mathrm{OPT}$ for the baseline strength, **consistency** for the ratio under
good advice, and **robustness** for the ratio under adversarial advice.

## 7.2 The master trade-off (rigorous)

> **Lemma 1.** Let $G,\mathrm{Bd}$ be two instance distributions sharing the *same* advice
> $\sigma$, with prefix laws $\mathcal L_G,\mathcal L_{\mathrm{Bd}}$ and
> $\gamma_k:=\mathrm{TV}(\mathcal L_G,\mathcal L_{\mathrm{Bd}})$. Suppose following $\sigma$
> gains $\delta$ under $G$ and loses $\Delta$ under $\mathrm{Bd}$ relative to $B$.
> Parameterize $A_k$ by the fraction $\eta_c$ of the upside it forgoes under $G$ and its
> robustness loss $\eta_r\Delta$ under $\mathrm{Bd}$. Then
> $$(1-\eta_c)\;\le\;\eta_r+\gamma_k+o(1).$$

*Proof.* Conditioning on $D$ under $G$, $\mathbb E_G[A_k]/\mathrm{OPT} = P_G(\mathsf F)\,
\mathbb E_G[\mathrm{Mimic}]/\mathrm{OPT} + P_G(\mathsf R)\rho_{\mathrm{base}} \pm o(1) \ge
\rho_{\mathrm{base}} + \delta\,P_G(\mathsf F)-o(1)$, so the captured upside $(1-\eta_c)\delta$
forces $P_G(\mathsf F)\ge 1-\eta_c-o(1)$. Symmetrically $P_{\mathrm{Bd}}(\mathsf F)=\eta_r
+o(1)$. Since $D$ is a function of $(X_{1:k},\sigma)$ and $\sigma$ is identical,
$|P_G(\mathsf F)-P_{\mathrm{Bd}}(\mathsf F)|\le\gamma_k$; chaining gives the claim. $\qed$

With an *uninformative* prefix ($\gamma_k=o(1)$) one cannot be both near-fully-consistent
($\eta_c\to0$) and robust ($\eta_r\to0$). Everything below is a computation of how large
$k$ must be before the prefix becomes informative — and (the half the earlier draft
missed) of how *small* a $k$ already suffices.

## 7.3 The construction and the affine law

The family is a disjoint union of $m$ independent **rare-resource cells**, each over a
distinct type-pair, so the support is $r=\Theta(m)$ and (at $m = \Theta(n)$) each type is
seen $O(1)$ times. Cell $i$ has resources $\{a_i,b_i\}$, a flexible request (neighborhood
$\{a_i,b_i\}$) that must be routed before a specialist ($\{a_i\}$ or $\{b_i\}$, present
with probability $\theta_i$) is seen; the right route depends on the future specialist.
The profile $\{(\theta_i,\varepsilon_i)\}_{i\le m}$ is **arbitrary** — no homogeneity is
assumed anywhere below. In closed form (verified numerically), cell $i$ has
$\mathrm{OPT}=1+\theta_i$, baseline $1+\theta_i/2$, and following the advice gains or
loses exactly $\theta_i\lvert s_i-\tfrac12\rvert$ over the baseline according to whether
the advice's *direction* is right, where $s_i = \tfrac12 \pm \varepsilon_i$ is the
specialist bias and $\varepsilon_i$ the signal; the advice-to-truth distance is
$\ell_1=2\theta_i\lvert s_i-\hat s_i\rvert$ per cell.

These aggregate cleanly. Summing over cells yields an **exact affine law** (proven; verified
to three decimals):
$$\mathbb E[\text{follow-ratio}] \;=\; \rho_{\mathrm{perfect}} - \tfrac12\,\ell_1(p,q),
\qquad \ell_1^\star \;=\; 2\big(\rho_{\mathrm{perfect}}-\rho_{\mathrm{base}}\big),$$
where $\rho_{\mathrm{perfect}}$ is the all-correct-direction ratio and $\ell_1^\star$ the
break-even. The quantity that organizes everything is the family's **specialist mass**
$$\sigma^2 \;:=\; \frac{\sum_i \theta_i}{N}, \qquad N=\sum_i(1+\theta_i)=\mathrm{OPT}$$
— the probability that a random arrival is a specialist, and (below) the variance bound
on the decision statistic. Two exact identities anchor what follows: the baseline slack
*is* half the specialist mass,
$$1-\rho_{\mathrm{base}} \;=\; \sigma^2/2,$$
and the maximum stakes (the full upside) are
$\rho_{\mathrm{perfect}}-\rho_{\mathrm{base}} = \sum_i\theta_i\varepsilon_i/N
\le 2\varepsilon_{\max}\,(1-\rho_{\mathrm{base}})$: *the upside is at most an

<!--REV
id: 6-02
role: P1 领域外审稿人
level: 建议
kind: 记号易误读
mark: the probability that a random arrival is a specialist
quote: $\sigma^2 := \sum_i \theta_i / N$
note: sigma^2 被定义为一个概率（随机到达是 specialist 的概率），却写成一个平方；文中从未定义 sigma 本身，直到 §7.6 才出现 g* = sigma/sqrt(n)。领域外审稿人会去找 sigma 的定义。
fix: 在定义处点明：我们把它记作 sigma^2 是因为它同时是决策统计量的方差上界，sigma 即其平方根，§7.6 会用到。
-->
$\varepsilon$-fraction of the baseline slack.* That the same $\sigma^2$ measures both
the slack and the noise is not a coincidence — it is the law. The canonical (verified)
instantiation takes $\theta_i=\theta$, $\varepsilon_i=\varepsilon$ and a wrong-direction
fraction $\varphi=\tfrac14$ (good: $\ell_1 = a$, gain $\delta$) versus $\varphi=\tfrac34$
(bad: $\ell_1 = b$, loss $\Delta$), with $\delta=\Delta=\ell_1^\star/4$.

## 7.4 The payoff identity: the stakes are a per-sample observable

The earlier route tried to make the follow/fallback decision *hard* by making
$\ell_1(p,q)$ hard to test. On this family that cannot work, for a reason worth a lemma.
Classify each arrival by its role in its own cell, relative to the advice's predicted
direction:
$$c(X) \;=\; \begin{cases} +1 & X \text{ is the advice-favored specialist of its cell,} \\
-1 & X \text{ is the disfavored specialist,} \\ 0 & X \text{ is flexible.}\end{cases}$$

> **Lemma 2 (payoff identity).** For every type distribution $p$ on the family — any
> profile $\{(\theta_i,\varepsilon_i)\}$, and any truth biases $s_i\in[0,1]$, matching
> the advice's magnitudes or not —
> $$\mathbb E_p[c] \;=\; \frac2N\sum_i \theta_i\,(s_i-\tfrac12)\,\hat d_i
> \;=\; 2\cdot\frac{\mathbb E_p[\mathrm{Mimic}]-\mathbb E_p[B]}{\mathrm{OPT}}.$$
> *The expected advantage of following the advice is half the mean of a bounded, per-sample
> observable.* (Verified to three decimals by `verify_witness_gap.py` for
> homogeneous wrong-fraction sweeps, and by
> `verify_budget_stakes_hetero.py` for random heterogeneous and
> magnitude-mismatched profiles.)

*Proof.* The advice-favored and disfavored specialists of cell $i$ have masses
$\theta_i\,(\tfrac12\pm(s_i-\tfrac12)\hat d_i)/N$, where $\hat d_i$ is the advice
direction; so cell $i$ contributes $2\theta_i(s_i-\tfrac12)\hat d_i/N$ to
$\mathbb E[c]$, while by the cell constants its follow-advantage is
$\theta_i(s_i-\tfrac12)\hat d_i$. Sum over cells and divide by
$\mathrm{OPT}=N$. $\qed$

<!--REV
id: 6-03
role: P2 领域审稿人
level: 建议
kind: 闭式常数无推导
mark: cell $i$ has
quote: In closed form (verified numerically), cell $i$ has OPT = 1 + theta_i, baseline 1 + theta_i/2
note: 整节的定量结论都建立在这三个 cell 常数上，正文只说「闭式（数值验证过）」而不给推导。审稿人要么自己推一遍，要么要求补附录。
fix: 把两行推导放进附录，正文指过去；数值验证保留但不作为唯一依据。
-->

## 7.5 The budget–stakes law

**Symbols.** One quantity carries the stakes and one pair carries its two directions.
For a scenario pair $(G,\mathrm{Bd})$ sharing an advice, $g$ is the **payoff gap** — the
difference in follow-advantage between the two scenarios — while $\delta$ and $\Delta$ are
the gain under $G$ and the loss under $\mathrm{Bd}$ separately, the objects Lemma 1 is
stated in. By definition $g=\delta+\Delta$, so $\min(\delta,\Delta)\le g/2$ always, with
equality exactly when the pair is **balanced**. The flip pairs of (i) are balanced —
flipping the cells of $W$ moves each $s_i$ symmetrically about $\tfrac12$, giving
$\delta=\Delta=g/2$ — so on them $\min(\delta,\Delta)=\Theta(g)$ and the two halves below
constrain the same quantity. On an unbalanced pair (ii) is governed by the smaller of the
two directions, and it is $\min(\delta,\Delta)$, not $g$, that sets the budget.

> **Theorem 1 (budget–stakes law, heterogeneous).** On any cell family with profile
> $\{(\theta_i,\varepsilon_i)\}$ and specialist mass $\sigma^2$:
>
> **(i) (Impossibility below the budget — any rule.)** Let $G,\mathrm{Bd}$ be the
> scenario pair that flips the advice-agreement of a cell set $W$ whose signals are at
> most $\varepsilon_W$, with payoff gap $g=\tfrac2N\sum_{i\in W}\theta_i\varepsilon_i$.
> Every test-and-fallback algorithm $A_k$, deciding by *any* measurable rule on the
> prefix, with $k \,=\, o\!\big(1/(\varepsilon_W\,g)\big)$ has
> $\eta_c+\eta_r \ge 1-o(1)$: it forgoes the upside or eats the loss.
>
> **(ii) (The budget suffices — an explicit rule.)** For *any* pair of truth profiles —
> magnitudes need not match the advice — on which following gains $\ge\delta$ and loses
> $\ge\Delta$, the **directional test** — follow iff $\sum_{j\le k} c(X_j) > 0$ —
> achieves $\eta_c+\eta_r \le \epsilon_0$ once
> $k \ge C\,(\sigma^2/\min(\delta,\Delta)^2)\log(1/\epsilon_0)$. In particular $k$ is
> *independent of $n$* for constant stakes.
>
> The two sides meet up to logarithms whenever the stakes are carried, at comparable
> signal levels, by a constant fraction of the specialist mass (Cauchy--Schwarz:
> $g^2 \le \tfrac4N\sigma^2_W\sum_W\theta_i\varepsilon_i^2$, $\sigma^2_W$ the flipped
> mass) — in particular for the canonical pair, giving the critical budget
> $$k^* \;=\; \tilde\Theta\!\big(\sigma^2/g^2\big),$$
> which at homogeneous parameters is the earlier $\tilde\Theta(\theta/\delta^2)$.

<!--REV
id: 6-04
role: P4 体例校对
level: 必改
kind: 赌注符号在定理内部就不一致
quote: payoff gap $g=\frac2N\sum_{i\in W}\theta_i\varepsilon_i$ ... on which following gains $\ge\delta$ and loses $\ge\Delta$ ... $k \ge C(\sigma^2/\min(\delta,\Delta)^2)$
note: Theorem 1 的 (i) 用 g、(ii) 用 delta/Delta，而结论写成 sigma^2/g^2。三者的关系（g 与 min(delta,Delta) 是否同阶）没有写明，读者无法确认两侧真的在比较同一个量。
fix: 在定理陈述前统一符号，并写明 (i) 的 g 与 (ii) 的 min(delta,Delta) 在何种意义下同阶——这正是两侧能相接的关键，不能留给读者推断。
-->

*Proof of (ii).* By Lemma 2, $\mathbb E[c] \ge 2\delta$ under the gain scenario and
$\le -2\Delta$ under the loss scenario, for any truth profile;
$\mathrm{Var}(c) \le \mathbb P(\text{specialist}) = \sigma^2$; Bernstein's inequality
gives error $\exp(-\Omega(k\min(\delta,\Delta)^2/\sigma^2))$ on both sides. $\qed$

<!--REV
id: 6-05
role: P5 审稿意见预演
level: 必改
kind: 主定理只有证明草图
quote: *Proof sketch of (i).*
note: 本文的核心定理，下界一侧只给了 proof sketch（耦合、每样本 Hellinger、张量化、代入 Lemma 1）。TALG 的审稿人对主定理通常要求完整证明；作者自己的 PROOF STATUS 备注里也写着」typeset the two short proofs in the appendix」，这件事还没做。
fix: 把 (i) 的完整证明写进附录：耦合的构造、per-sample Hellinger 的那步等式如何得到、张量化与 joint convexity 的引用出处，以及 o(1) 的含义。既然作者自己说这两个证明很短，补上的成本远小于被要求 major revision 的成本。
-->

*Proof of (i), in outline (in full in Appendix B).* Couple the two scenarios; the
per-sample laws differ only on the specialists of the flipped cells, and the per-sample
squared Hellinger distance is exactly
$H^2 = \sum_{i\in W}\tfrac{2\theta_i}{N}\big(1-\sqrt{1-4\varepsilon_i^2}\big)
\in [4,8]\cdot\sum_{i\in W}\theta_i\varepsilon_i^2/N \le 4\,\varepsilon_W\,g$.
Tensorizing the Bhattacharyya coefficient and passing to total variation gives
$\gamma_k \le \sqrt{k\,H^2} = o(1)$ whenever $k = o(1/(\varepsilon_W g))$, and Lemma 1
turns that into $\eta_c+\eta_r\ge 1-o(1)$. $\qed$

Numerically (§`verify_witness_gap.py`, $\theta=0.6$, $\varepsilon=0.3$, $\delta=0.056$):
the directional test reaches $\eta_c+\eta_r \approx 0.06$ at $k=100$ and $0.007$ at
$k=200$, and stays flat as $n$ grows from $3{,}200$ to $320{,}000$ at fixed $k=200$ —
the budget really is $n$-free once the stakes are constant. The heterogeneous claims are
verified separately (`verify_budget_stakes_hetero.py`): the payoff identity holds
for random profiles and for magnitude-mismatched truths; $1-\rho_{\mathrm{base}}=
\sigma^2/2$ exactly; the per-sample Hellinger distance sits inside its $[4,8]$ bounds;
and three families with $\sigma^2\in\{0.13,0.24,0.42\}$ produce decision-error curves
that *coincide* as a function of $k g^2/\sigma^2$ alone ($0.30/0.15/0.02/0.001$ at
$kg^2/\sigma^2=\tfrac14/1/4/8$) — the budget–stakes scaling is the whole story. Section
5.4 carries the rule from the hard family to the benchmark itself, where the plug-in
payoff must additionally survive a concavity bias at the capacity kinks — it does, with
a bootstrap calibration that still uses no problem constants.

## 7.6 The wall, quantified: strong baselines price the test out of the horizon

Stakes are capped by the slack: $g \le \rho_{\mathrm{perfect}}-\rho_{\mathrm{base}}
\le 2\varepsilon_{\max}(1-\rho_{\mathrm{base}}) = \varepsilon_{\max}\,\sigma^2$. Theorem 1
places the feasibility frontier at $g \asymp \sigma/\sqrt k$: a prefix of length $k$
resolves stakes down to $\sigma/\sqrt k$ and no further. With the whole instance as
prefix ($k=n$), the constant-free threshold is
$$g^{*} \;=\; \sigma/\sqrt n \;=\; \sqrt{2(1-\rho_{\mathrm{base}})/n}\,:$$

> **Corollary (uncapturable upsides).** On strong-baseline families satisfying the
> matching condition of Theorem 1 — the stakes carried at comparable signal levels by a
> constant fraction of the specialist mass — every advice upside smaller than
> $\Theta\big(\sqrt{(1-\rho_{\mathrm{base}})/n}\,\big)$ is uncapturable by any
> test-and-fallback rule at any prefix length $k \le n$ — the information needed to decide
> does not exist inside the instance. (Theorem 1(ii) — stakes above the frontier *are*
> resolvable — is unconditional; it is the impossibility direction, and hence this
> corollary, that inherits the condition.)

At the parameters of our benchmark (§3: $\rho_{\mathrm{base}}\approx0.99$, $n=2000$) the
threshold is $g^{*}\approx 0.003$, and the measured upsides are $<0.01$ (F3) — the
empirical wall sits in the regime the corollary governs. This is the **scissors** of **Figure 8**
(`results/impossibility_frontier.png`), now with the correct mechanism: the *potential*
upside (perfect advice minus baseline) grows as the baseline weakens, while the upside a
feasible test can safely capture is pinned by the $\sqrt{(1-\rho_{\mathrm{base}})/n}$
resolution — **the structure that makes the baseline strong is the structure that starves

<!--REV
id: 6-06
role: P2 领域审稿人
level: 必改
kind: 推论继承了未声明的条件
mark: is uncapturable by any
quote: Corollary (uncapturable upsides): every advice upside smaller than Theta(sqrt((1-rho_base)/n)) is uncapturable by any test-and-fallback rule at any prefix length k <= n
note: 这是全文最强、也最会被引用的一句。它由」Theorem 1 places the feasibility frontier at g ~ sigma/sqrt(k)」推出，而这个 frontier 的」and no further」方向来自 (i)，因而继承了 §7.5 那个 Cauchy-Schwarz 条件；推论本身却是无条件陈述的。
fix: 把条件写进推论（on families where the two sides of Theorem 1 meet），或把它降为 under the conditions of Theorem 1。这一处不改，§7.8 的诚实声明会与推论直接冲突。
-->
the test of signal.**

![The budget–stakes scissors: as the baseline weakens (left), the potential upside of perfect advice grows, while the upside a feasible test can safely capture stays pinned near zero — the empirical test's resolution sits far above the break-even margin wherever the upside exists.](../../results/impossibility_frontier.png){width=100%}

## 7.7 Why the field's rules hit the wall earlier: distance-testing is the wrong statistic

The algorithms of [Choo24, BEM26] do not run the directional test; they threshold the
plug-in distance $\hat\ell_1(\hat p_k, q)$. That class is blind far before Theorem 1(i)
bites: at $k \ll r$ the empirical $\hat p_k$ is $k$ atoms of mass $1/k$, so
$\hat\ell_1 \approx 2$ *regardless of the advice's quality* (numerically: $1.908$ vs
$1.913$ on the two canonical scenarios whose true $\ell_1$ differ by $0.225$). Any
threshold therefore either always accepts or always rejects — the §5.3 pathology, now
explained. The same blindness is measurable on the benchmark generator itself: holding
the true error at $\ell_1\approx0.11$ and growing the support from $r=8$ to $512$ at
fixed $k=200$, the plug-in estimate inflates from $0.17$ to $1.22$ — twelve times the
truth — while the payoff rule of §5.4 keeps deciding, staying within the prefix cost of
the floor at both good and bad advice (**Figure 9**).

![The blindness curve on the benchmark generator: at fixed true $\ell_1\approx0.11$ and $k=200$, the plug-in $\hat\ell_1$ inflates with the support size while the payoff rule keeps deciding at both good (left) and bad (right) advice.](../../results/directional_rsweep.png){width=100%}

The deeper reason is the tolerant-testing barrier: estimating $\ell_1(p,q)$ to
constant accuracy at $r=\Theta(n)$ genuinely requires $\tilde\Theta(n/\log n)$ samples
[CJKL22]. The resolution of the apparent paradox — the *decision* is easy (Theorem 1(ii))
while the *distance* is hard — is Lemma 2: the payoff is a linear, per-sample functional,
and $\ell_1$ is not. The practical moral for algorithm designers is one sentence: **test
the payoff, not the prediction.**

We record the flip side honestly. The natural conjecture behind an earlier version of this
section — that tolerant-testing hardness makes the follow/fallback decision itself
impossible for *any* rule at $k = o(n/\log n)$ with $\Theta(1)$ stakes — is **refuted** by
Theorem 1(ii): no witness pair with $\gamma_k = o(1)$ and $\Theta(1)$ stakes exists on this
family, because by Lemma 2 a $\Theta(1)$ stake gap forces $\gamma_k \to 1$ at any
$k=\omega(1)$. The tolerant-testing hard instances evade Lemma 2 only by mismatching the
advice's per-cell magnitudes — precisely the regime in which distance and payoff decouple
and $\ell_1$ stops being the decision-relevant quantity.

## 7.8 Scope and honesty

Both halves of Theorem 1 use only elementary tools (Bernstein; Hellinger tensorization
plus Lemma 1) — deliberately: the earlier, stronger-sounding route through tolerant-testing
lower bounds is closed by §7.7, and we consider the refutation itself part of the
contribution. The law now allows fully heterogeneous cell profiles, and its achievability
side holds for arbitrary (magnitude-mismatched) truth distributions — neither homogeneity
nor the matched-magnitude advice model is load-bearing. Its two sides can separate, by
the factor $\sigma^2\varepsilon_W/g \ge 1$, when a scenario pair's stakes hide in an
asymptotically vanishing sliver of low-signal cells; closing that regime is open. The law
is stated for decomposable (disjoint-cell) families; by Lemma 2 the payoff is per-sample
observable on *every* such family, so no decomposable construction can restore a
super-$1/\delta^2$ barrier. Whether a *non-decomposable* family — long-range
dependence making the payoff a genuinely hard functional — can separate the budget from
$1/\delta^2$ is open. The directional test is analyzed here only on the cell family; a
dedicated novelty pass — whose venues, keywords and cut-off are stated in §9 — found no
payoff-testing acceptance rule in the adjacent literatures — the nearest lines test distances, switch on
regret, or select algorithms from whole-instance samples (§9) — though the statistical
skeleton of the upper half is, deliberately, classical. We credit Choo et al. for the constructive

<!--REV
id: 6-07
role: P5 审稿意见预演
level: 建议
kind: 不可核查的出处
quote: a dedicated novelty pass (recorded in the project archive) found no payoff-testing acceptance rule
note: project archive 对审稿人不存在。而这句支撑的是本文第二项新颖性主张。
fix: 把检索范围写进 §9（库、关键词、截止时间），正文指向 §9 而不是 archive。
-->
baseline-coupling their threshold already exhibits; our contribution is the two-sided,
rule-independent budget law, the payoff/distance separation, and the quantified wall.
