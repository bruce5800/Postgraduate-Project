<!--
Draft §7 — the impossibility theorem (C5, Direction C). THE NEW CENTERPIECE.
Sources: docs/T1_PROOF_SKELETON.md, T1_W1_single_cell.md, T1_W3_construction.md,
T1_W2_W3a_closeout.md, direction_c_advisor_talk.md. Figure 7 = impossibility_frontier.png.

[PROOF STATUS — for the authors, delete before submission]
Write the statements and the proof ARCHITECTURE now. Lemma 1 is rigorous and given in
full. Lemma 2 (reduction) is clean. The construction uses W1 (verified) + the affine law
(verified) + the tolerant-testing lower bound (Canonne et al. 2022, cited). ONE routine
step (naming the two witness distributions) + an advisor pass remain before the full proof
is typeset; the section flags this honestly as "deferred to Appendix / in preparation".
Do NOT present T1 as a fully typeset theorem until that step and the advisor sign-off.

Differentiation to defend (put up front): Choo's threshold τ=2(n̂/n−β)−ε already couples to
the baseline β CONSTRUCTIVELY; our result is an INFORMATION-THEORETIC lower bound holding
for ANY prefix rule — that is what Lemma 2 buys.
-->

# 7. The Impossibility Theorem: Why the Wall Is Necessary

Every experiment above met the same wall: on average-case matching the advice-free baseline
is near-optimal, so predictions buy robustness insurance rather than performance, and — for
the test-and-fallback algorithms — no acceptance threshold both captures the (tiny) upside
and stays safe (§5.3). We now show this is not a property of a particular threshold, graph
generator, or algorithm, but a *theorem*: on strong-baseline instances no test-and-fallback
algorithm whose test inspects only a sublinear prefix can be both consistent and robust.

**Relation to prior work.** The algorithms we bound are those of Choo et al. [Choo24] and
Burathep–Erlebach–Moses [BEM26]; both give *upper* bounds (algorithms) in the random-arrival
model and no lower bound there. Choo et al.'s only lower bound (their Thm 3.1) is the generic
*adversarial* indistinguishability — no algorithm is $1$-consistent and $>\tfrac12$-robust —
driven by an adversarial instance, not by the statistical resolution of a sublinear test.
Notably their acceptance threshold $\tau = 2(\hat n/n-\beta)-\varepsilon$ already *couples*
to the baseline ratio $\beta$, but *constructively*; we turn that observation into a two-sided
impossibility. The consistency/robustness *lower bounds* in the with-predictions literature
[WZ20] are of a different genre — problem-intrinsic Pareto frontiers, not gated by a test —
and the accuracy-to-ratio relation studied elsewhere is a *positive* monotone curve, not an
impossibility. The engine we invoke is the sample-complexity of **tolerant** distribution
testing [CJKL22, JHW18, VV11]; to our knowledge, connecting its lower side to the *value of
advice in an online algorithm*, and identifying that testability and baseline-strength are
the *same* structural regime, is new.

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

The inequality is the two-sided core: with an *uninformative* prefix ($\gamma_k=o(1)$) one
cannot be both near-fully-consistent ($\eta_c\to0$) and robust ($\eta_r\to0$). The whole
question is whether, on strong-baseline instances, $\gamma_k$ can be $o(1)$ while
$\delta,\Delta$ stay meaningful. The rest of the section shows this is *forced*.

## 7.3 The reduction to tolerant testing (any rule, not just a threshold)

The prefix $X_{1:k}$ is *literally* $k$ i.i.d. samples from the type distribution $p$. In
the construction below (§7.4), following $\sigma$ helps by $\delta=\Theta(1)$ exactly when
$\ell_1(p,q)\le a$ and hurts by $\Delta=\Theta(1)$ exactly when $\ell_1(p,q)\ge b$, for the
advice $q$ and constants $a<b$. Hence a $(1-o(1))$-consistent, $(\rho_{\mathrm{base}}-o(1))$-
robust $A_k$ must, from $k$ samples of $p$, decide whether $\ell_1(p,q)\le a$ or $\ge b$ —
i.e. it solves **tolerant identity testing** to the known $q$ with gap $[a,b]$. This is what
makes the bound information-theoretic: $D$ is an *arbitrary* function of the $k$ samples, so
the lower bound below rules out *every* rule, not only the empirical-$\ell_1$ threshold of
[Choo24, BEM26].

> **Lemma 2 (tolerant testing lower bound [CJKL22]).** Distinguishing $\ell_1(p,q)\le a$ from
> $\ell_1(p,q)\ge b$ for a known $q$ over support $r$, with error $\le \tfrac13$, requires
> $\tilde\Theta\!\big(\tfrac{\sqrt r}{b^2}+\tfrac{r}{\log r}\max\{\tfrac{a}{b^2},(\tfrac{a}{b^2})^2\}\big)$
> samples. For *constant* tolerances ($a,b=\Theta(1)$, $a<b$) this is $\tilde\Theta(r/\log r)$.

Crucially our "good" side is a $\Theta(1)$ *ball* ($a>0$), not the point $q$: this puts us in
the **tolerant** regime ($\tilde\Theta(r/\log r)$), not the non-tolerant one ($\sqrt r$,
which would defeat the theorem). The affine law of §7.4 guarantees $a>0$.

## 7.4 The construction and the affine law

The family is a disjoint union of $m=\Theta(n)$ independent **rare-resource cells**, each a
distinct type, so the support is $r=\Theta(n)$ and each type is seen $O(1)$ times. A cell has
resources $\{a_i,b_i\}$, a flexible request (neighborhood $\{a_i,b_i\}$) that must be routed
before a specialist ($\{a_i\}$ or $\{b_i\}$, present with probability $\theta$) is seen; the
right route depends on the future specialist. In closed form (verified numerically), per cell
$\mathrm{OPT}=1+\theta$, baseline $=1+\theta/2$, and following the advice gains or loses
exactly $\theta\lvert s-\tfrac12\rvert$ over the baseline according to whether the advice's
*direction* is right, where $s$ is the specialist bias; the advice-to-truth distance is
$\ell_1=2\theta\lvert s-\hat s\rvert$.

These aggregate cleanly. Summing over cells yields an **exact affine law** (proven; verified
to three decimals):
$$\mathbb E[\text{follow-ratio}] \;=\; \rho_{\mathrm{perfect}} - \tfrac12\,\ell_1(p,q),
\qquad \ell_1^\star \;=\; 2\big(\rho_{\mathrm{perfect}}-\rho_{\mathrm{base}}\big),$$
where $\rho_{\mathrm{perfect}}$ is the all-correct-direction ratio and $\ell_1^\star$ is the
break-even. Consequently "following gains $\ge\delta$" $\iff \ell_1\le a:=\ell_1^\star-2\delta$
and "loses $\ge\Delta$" $\iff \ell_1\ge b:=\ell_1^\star+2\Delta$: the gap $b-a=2(\delta+\Delta)$
is $\Theta(1)$, and $a>0$ whenever $\delta<\ell_1^\star/2=\rho_{\mathrm{perfect}}-
\rho_{\mathrm{base}}$ — i.e. as long as we do not demand the *full* upside. Choosing
$\delta=\Delta=(\rho_{\mathrm{perfect}}-\rho_{\mathrm{base}})/4$ gives $a=\ell_1^\star/2>0$ and
a $\Theta(1)$ gap, placing us squarely in the tolerant regime of Lemma 2.

With $r=\Theta(n)$ and constant $[a,b]$, Lemma 2 gives sample complexity
$\tilde\Theta(n/\log n)$; so any $A_k$ with $k=o(n/\log n)$ has $\gamma_k=o(1)$ on the
resulting witness pair, and Lemma 1 forces $\eta_c+\eta_r\ge 1-o(1)$.

## 7.5 The theorem

> **Theorem 1.** For every test budget $k=o(n/\log n)$ there is a known-i.i.d. matching
> family with $r=\Theta(n)$ types and baseline strength $\rho_{\mathrm{base}}=1-\Theta(1)$
> on which no test-and-fallback algorithm $A_k$ — *any* rule on the prefix, not only an
> empirical-$\ell_1$ threshold — is simultaneously $(1-o(1))$-consistent and
> $(\rho_{\mathrm{base}}-o(1))$-robust. The achievable (robustness, consistency) region
> collapses to the point $(\rho_{\mathrm{base}},\rho_{\mathrm{base}})$.

Together with the trivial strong-baseline side (small $r\Rightarrow\rho_{\mathrm{base}}\to1
\Rightarrow$ upside $\to0$, nothing to capture), this is the **scissors** of **Figure 7**
(`results/impossibility_frontier.png`): the *potential* upside (perfect advice minus baseline)
grows as the baseline weakens, while the upside a *sublinear test can safely capture* stays
pinned near zero — because the empirical-$\ell_1$ resolution at $k=\sqrt n$ sits far above the
break-even margin wherever the upside exists. The single sentence is: **the structure that
makes the prefix test feasible (few, high-count types) is the structure that makes the
baseline near-optimal**, so wherever you can test the advice you do not need it.

<!-- PROOF STATUS (delete before submission): Lemma 1 is complete and given above. Lemma 2 is
cited. The construction's constants (W1) and the affine law (W3a) are proven and numerically
verified (docs/T1_W1_single_cell.md, T1_W2_W3a_closeout.md). One routine step — exhibiting the
two witness distributions p_G (ℓ1=a) and p_Bd (ℓ1=b) from the tolerant-testing hard instance
inside this cell family — remains, together with an advisor pass on the reduction. Full proof
to appear in Appendix; do not typeset Theorem 1 as final until both are done. -->

**Scope and honesty.** The strong form is for the $r=\Theta(n)$ regime — which is the only
regime with an upside to contest, so it is the right regime; a version biting at constant $r$
is open. The reduction inherits the empirical-$\ell_1$ modeling of the test (Section 2.2). We
credit Choo et al. for the constructive baseline-coupling their threshold already exhibits;
our contribution is the two-sided, rule-independent impossibility and the identification of
testability with baseline strength.
