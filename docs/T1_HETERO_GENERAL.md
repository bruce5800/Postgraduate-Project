# T1 generalization — the budget–stakes law on heterogeneous cell families (2026-07-28)

**Status: closed and verified** (`scripts/verify_budget_stakes_hetero.py`, all checks pass).
Generalizes the law of `docs/paper/06_theory.md` from homogeneous $(\theta,\varepsilon)$
cells to arbitrary per-cell profiles $\{(\theta_i,\varepsilon_i)\}$, and — a free bonus
that closes the planned T2 as well — drops the matched-magnitude restriction on the
achievability side. Nothing in the argument needed homogeneity; the right invariant is the
**specialist mass** $\sigma^2 = \sum_i \theta_i / N$, $N=\sum_i(1+\theta_i)=\mathrm{OPT}$.

## The four facts

1. **Payoff identity (verbatim, and magnitude-free).** With $c(X)\in\{+1,-1,0\}$ (advice-
   favored specialist / disfavored / flexible), for ANY truth biases $s_i$ (not only
   $\tfrac12\pm\varepsilon_i$ matching the advice):
   $$\mathbb E_p[c] \;=\; \frac{2}{N}\sum_i \theta_i\,(s_i-\tfrac12)\,\hat d_i
   \;=\; 2\cdot\frac{\text{follow-advantage}}{\mathrm{OPT}}.$$
   Verified: matched and arbitrary-$s_i$ profiles, sim vs formula to 3 decimals.

2. **Slack identity (exact).** $1-\rho_{\mathrm{base}} = \sigma^2/2$: the baseline slack
   *is* half the specialist mass. (Also $\sigma^2 = \operatorname{Var}$-bound on $c$ —
   the same quantity controls the slack and the estimator's noise. That coincidence is
   the whole law.) Max stakes: $\rho_{\mathrm{perf}}-\rho_{\mathrm{base}} =
   \sum\theta_i\varepsilon_i/N \le 2\varepsilon_{\max}(1-\rho_{\mathrm{base}})$.

3. **Hellinger weights (exact bounds).** For the scenario pair flipping cell set $W$:
   per-sample $H^2 \in [4,8]\cdot\sum_{i\in W}\theta_i\varepsilon_i^2/N$
   (per flipped cell: $2\tfrac{\theta_i}{N}(\sqrt{\tfrac12+\varepsilon_i}-
   \sqrt{\tfrac12-\varepsilon_i})^2 = \tfrac{2\theta_i}{N}(1-\sqrt{1-4\varepsilon_i^2})$).
   With payoff gap $g = \tfrac2N\sum_W\theta_i\varepsilon_i$ and flipped signals
   $\le\varepsilon_W$: $H^2 \le 4\varepsilon_W g$, so $\gamma_k \le \sqrt{2kH^2} = o(1)$
   whenever $k = o(1/(\varepsilon_W g))$ — the impossibility side via Lemma 1.

4. **Budget scaling (collapse).** Directional-test error is a function of
   $x = k g^2/\sigma^2$ alone: three heterogeneous families ($\sigma^2 \in
   \{0.13, 0.24, 0.42\}$, $m \in \{10^3, 4{\cdot}10^3, 1.6{\cdot}10^4\}$) give
   error $\approx 0.30 / 0.15 / 0.02 / 0.001$ at $x = \tfrac14/1/4/8$, coinciding to
   $\pm0.02$ across families. (Bernstein: error $\le \exp(-\Theta(k\delta^2/\sigma^2))$,
   $\operatorname{Var}(c)\le\Pr[\text{specialist}]=\sigma^2$.)

## The generalized theorem (as now stated in paper §7.5)

$k^* = \tilde\Theta(\sigma^2/g^2)$: below it no rule is simultaneously consistent and
robust (witness: the flip-pair, via facts 3 + Lemma 1); at it the directional test
succeeds for ANY truth profile with the stated stakes (facts 1 + 4). Sharp up to logs
whenever the stakes are carried at comparable signal by a constant fraction of the
specialist mass (Cauchy–Schwarz: $g^2 \le 4\sigma^2_W \cdot \sum_W\theta\varepsilon^2/N$);
when the stakes hide in a vanishing low-signal sliver the two sides can separate by the
factor $\sigma^2\varepsilon_W/g \ge 1$ — left open, stated honestly in §7.8.

**Corollary (cleaner than the homogeneous version).** The feasibility frontier is
$g \asymp \sigma/\sqrt k$; at full horizon $k=n$, no upside below
$$g^\* \;=\; \sigma/\sqrt n \;=\; \sqrt{2(1-\rho_{\mathrm{base}})/n}$$
is safely capturable by any rule — a constant-free threshold depending only on the
baseline slack and the horizon. Benchmark parameters ($\rho_{\mathrm{base}}\approx0.99$,
$n=2000$): $g^\*\approx 0.003$; measured upsides $<0.01$ (F3) sit at this scale.
