# T1 — the witness step FAILS, and refutes the theorem as stated (2026-07-27)

**Status: major honest finding.** Attempting the "one routine step" (exhibit the witness
pair $(p_G, p_{\mathrm{Bd}})$ for §B.6 step 3) revealed that **no such pair exists** on the
matched-magnitude cell family — and, stronger, that **Theorem B.6 is false on that family**:
an explicit test-and-fallback rule with prefix $k = O(\log n)$ is simultaneously
$(1-o(1))$-consistent and $(\rho_{\mathrm{base}}-o(1))$-robust. Verified numerically
(`scripts/verify_witness_gap.py`, table below). Lemmas B.1–B.3 are untouched and true;
the break is in how Lemma B.4's reduction connects to the tolerant-testing lower bound.
A true replacement theorem (a sharp *budget–stakes* law) survives and is stated in §5.

This supersedes the "routine last step" verdicts in `T1_W2_W3a_closeout.md` and
`T1_PROOF_SKELETON.md` §6, and the status wording in thesis §9.5/§B.7, `docs/paper/06_theory.md`,
and the README.

---

## 1. What the step required

§B.6 step 3 needs two instance distributions on the §B.4 family, sharing the advice $q$:
$G$ supported on $\{\ell_1(p,q) \le a\}$ (following gains $\delta$) and $\mathrm{Bd}$ on
$\{\ell_1(p,q) \ge b\}$ (following loses $\Delta$), with prefix laws satisfying
$\gamma_k = \mathrm{TV} = o(1)$ for all $k = o(n/\log n)$. Lemma B.1 would then force
$\eta_c + \eta_r \ge 1 - o(1)$.

## 2. The obstruction: on this family, the payoff is a per-sample observable

Work on the §B.4 family: $m$ cells, contention $\theta$, signal $\varepsilon$, advice
directions $\hat d_i \in \{\pm 1\}$ (from $q$), truth directions $d_i$; type masses
$F_i: 1/N$, favored/disfavored specialists $\theta(\tfrac12 \pm \varepsilon d_i \hat d_i)/N$,
$N = m(1+\theta)$. Define the three-valued statistic on a single arrival $X$:

$$c(X) \;=\; \begin{cases} +1 & X \text{ is the advice-favored specialist of its cell} \\ -1 & X \text{ is the disfavored specialist} \\ 0 & X \text{ is flexible.} \end{cases}$$

> **Lemma G1 (the payoff identity).** For every $p$ in the family,
> $$\mathbb E_p[c] \;=\; \frac{2\theta\varepsilon}{1+\theta}\cdot\frac1m\sum_i d_i\hat d_i
> \;=\; 2\cdot\Bigl(\frac{\mathbb E_p[\mathrm{Mimic}] - \mathbb E_p[B]}{\mathrm{OPT}}\Bigr).$$
> *The follow-advantage is exactly half the mean of a bounded per-sample observable.*

*Proof.* The favored specialist of cell $i$ has mass $\theta(\tfrac12+\varepsilon d_i\hat d_i)/N$
and the disfavored $\theta(\tfrac12-\varepsilon d_i\hat d_i)/N$, so cell $i$ contributes
$2\theta\varepsilon d_i\hat d_i/N$ to $\mathbb E[c]$. By Lemma B.2 the per-cell follow-advantage
is $\theta\varepsilon d_i\hat d_i$, and $\mathrm{OPT} = N$. Compare the two sums. $\blacksquare$

> **Lemma G2 (no witness pair exists).** Let $G, \mathrm{Bd}$ be any two instance
> distributions on the family (mixtures allowed) with stake gap
> $g := \delta + \Delta = \Theta(1)$ as in Lemma B.1. Then their length-$k$ prefix laws obey
> $$\gamma_k \;\ge\; 1 - 2\exp(-c\,k\,g^2), \qquad c = c(\theta) > 0.$$
> In particular $\gamma_k \to 1$ for every $k = \omega(1)$: the pair needed by §B.6 step 3
> ($\gamma_k = o(1)$ at $k = o(n/\log n)$ with $\Theta(1)$ stakes) does not exist.

*Proof.* By G1, under every $p$ in the support of $G$ the per-sample mean of $c$ is
$\ge 2\delta$, and under $\mathrm{Bd}$ it is $\le -2\Delta$; the empirical mean
$\bar c_k$ of the $k$ i.i.d. prefix samples concentrates within $O(1/\sqrt k)$ (Hoeffding,
$|c|\le1$) around its conditional mean under either mixture. The event
$\{\bar c_k > \delta - \Delta\}$ then separates the two laws up to $2\exp(-\Theta(kg^2))$.
$\blacksquare$

## 3. The counter-algorithm (refutes Theorem B.6 on this family)

**DirectionalTest-and-Match:** observe the prefix, compute $S = \sum_{j\le k} c(X_j)$;
**follow iff $S > 0$**, else fall back to Ranking. By G1 + Hoeffding it errs with probability
$\exp(-\Theta(k g^2))$ on both sides, so $k = \Theta(\log n)$ (or any $k = \omega(1)$, for
$o(1)$ error) gives $(1-o(1))$-consistency **and** $(\rho_{\mathrm{base}}-o(1))$-robustness on
the family — with $k$ *independent of $n$* for constant error. Theorem B.6 claimed this is
impossible for every $k = o(n/\log n)$.

**Numerical verification** (`verify_witness_gap.py`; $\theta=0.6$, $\varepsilon=0.3$,
$\varphi \in \{\tfrac14,\tfrac34\}$, i.e. $\ell_1 \in \{a, b\}$, stakes $\delta=\Delta=0.056$):

| check | result |
|---|---|
| payoff identity $\mathbb E[c] = 0.225(1-2\varphi)$ | matches to 3 decimals at $\varphi \in \{0,\tfrac14,\tfrac12,\tfrac34,1\}$ |
| $\eta_c+\eta_r$ at $m{=}2000$: $k{=}100 / 200 / 400$ | $0.061\; /\; 0.007\; /\; 0.000$ |
| fixed $k{=}200$, $n = 3\,200 \to 320\,000$ | $\eta_c+\eta_r \approx 0.01$, **flat in $n$** |
| plug-in $\hat\ell_1(\hat p_k, q)$ at $k{=}200$, $r{=}6000$ | $1.908$ vs $1.913$ across the two sides — **blind** (true $\ell_1$: $0.113$ vs $0.338$) |

The last row is the half of the old story that *survives*: the **empirical-$\ell_1$-threshold
class** (what Choo/BEM actually run) genuinely cannot see the difference at $k \ll r$. The
directional statistic can — because it estimates the *payoff*, not the *distance*.

## 4. Where the old argument breaks (and what it leaves intact)

- **Lemmas B.1, B.2, B.3 are true as stated.** Nothing in this note touches them.
- **Lemma B.4 is true but weaker than it looks:** the tester it extracts is only guaranteed
  correct **under the promise** $p \in$ the matched-magnitude family. The CJKL
  $\tilde\Theta(r/\log r)$ lower bound is for testers on (essentially) all of $\Delta([r])$;
  its moment-matched hard instances have *mismatched* magnitudes and lie **outside the
  promise**. A promise-restricted tester does not contradict the lower bound — and on this
  promise, tolerant identity testing costs $O(1/g^2)$ samples, not $\tilde\Theta(r/\log r)$,
  because (G1) $\ell_1(p,q)$ restricted to the family is an *affine function of an estimable
  bounded linear statistic*.
- **The affine law is a double-edged sword.** The exactness celebrated in
  `T1_W2_W3a_closeout.md` ("stakes $\iff \ell_1$") is precisely what collapses $\ell_1$ onto
  an observable and hands the algorithm a cheap test. The construction dies of its own
  exactness — and the obstruction is intrinsic to *any* disjoint-cell family: stakes there
  are always a bounded linear functional of $p$, hence always estimable at $k = O(1/g^2)$.
- **The empirical results (Ch. 4–6) are untouched** — they measured real algorithms
  (ℓ₁-threshold rules), which Check 5 confirms are blind. What is refuted is only the leap
  from "the ℓ₁ threshold fails" to "every rule fails".

## 5. What is true instead: a sharp budget–stakes law (T1′)

On the cell family the right statement is a **matching pair of bounds around
$k^* = \Theta(1/g^2)$**, $g = \delta+\Delta$ the stakes:

> **T1′ (lower half — impossibility below the budget).** For any two scenario mixtures with
> stake gap $g$, one per-sample law pair has squared Hellinger distance $O(g^2)$, so
> $\gamma_k \le O(\sqrt{k}\,g)$; by Lemma B.1, **every** rule with $k = o(1/g^2)$ has
> $\eta_c + \eta_r \ge 1 - o(1)$.
>
> **T1′ (upper half — the budget suffices).** DirectionalTest-and-Match with
> $k = O(g^{-2}\log(1/\epsilon))$ attains $\eta_c + \eta_r \le \epsilon$ (§3).

**Corollary (the true strong-baseline impossibility — the regime the thesis cares about).**
Stakes are capped by the baseline slack: $g \le 2(\rho_{\mathrm{perfect}} - \rho_{\mathrm{base}})
= \Theta(1-\rho_{\mathrm{base}})$. Hence the required budget
$k^* = \Omega\bigl((1-\rho_{\mathrm{base}})^{-2}\bigr)$: **on strong-baseline instances the
necessary prefix exceeds the entire horizon once $(1-\rho_{\mathrm{base}})^2 n \to 0$** — no
feasible test-and-fallback (by *any* rule, at *any* $k \le n$) captures the upside. This is a
true, two-sided, any-rule impossibility, and it matches Chapter 6 quantitatively: there
$\rho_{\mathrm{base}} \approx 0.99$, so $k^* \gtrsim 10^4 > n = 2000$ — the empirical wall is
the $k \le n < k^*$ regime of T1′.

The scissors survives with a cleaner blade: *the prefix must pay the inverse square of the
stakes; where the baseline is strong, that price exceeds the instance itself.* The
$\tilde\Theta(n/\log n)$ tolerant-testing machinery exits the proof (it remains correct and
citable as context for why *distance* testing is hard; it just is not the mechanism here).

## 6. Fallout — statements that must be revised before any submission

1. `thesis/en/09_*` + `zh/09_*` (Ch. 9): theorem statement + §9.5 status ("one routine step").
2. `thesis/en/B_proof_details.md` + zh: §B.5–B.7 (reduction, Theorem B.6, status).
3. `docs/paper/06_theory.md`: the theorem section and its PROOF STATUS notes.
4. `README.md`: "Theorem (Ch. 9)" bullet + project-status row for C (T1).
5. `docs/interactive/impossibility_explainer.html` (+ zh): Gadget C teaches the
   $n/\log n$ sampling wall as *the* mechanism; hero/TLDR state the theorem. Needs reframing
   around T1′ once the direction is chosen.
6. `docs/advisor_talk/thesis_overview_talk.md`: theorem-status lines.
7. `T1_PROOF_SKELETON.md` / `T1_W2_W3a_closeout.md`: superseded-by pointers added (done).

## 7. Options going forward (decision needed — user + advisor)

- **A (recommended): reframe Ch. 9 around T1′.** Keep Lemmas B.1–B.3 verbatim; replace the
  tolerant-testing reduction with the Hellinger lower half; add DirectionalTest-and-Match as
  a small *positive* contribution ("test the payoff, not the prediction") plus the plug-in-ℓ₁
  blindness lemma explaining why Choo/BEM's own rule hits the wall. Strictly true, matches
  every experiment, arguably a better story (an impossibility *with its matching algorithm*).
  Needs: a novelty pass on payoff-testing rules in the learning-augmented literature.
- **B (minimal surgery): restrict the theorem to empirical-ℓ₁-threshold rules.** Provable via
  Check 5's mechanism (plug-in $\hat\ell_1 \approx 2$ regardless of advice quality at
  $k \ll r$). Honest but weaker; leaves the "any rule" question open — except it is now
  *answered negatively* on cell families by §3, which the text would have to admit anyway.
- **C: hunt a non-decomposable construction** where the payoff is a genuinely
  hard-to-estimate functional (long-range dependence between cells). Open-ended research;
  the G1 obstruction says decomposable families can never work. Not an MSc-timeline bet;
  state as an open problem under A or B.

**Submission implication:** the previous advice ("close the theorem before submitting")
is now load-bearing: the draft as written would have been refereed against a false theorem.
Nothing goes out before Ch. 9 is reframed and the advisor has seen this note.
