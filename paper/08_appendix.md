<!--
Paper appendices. A = reproduction (the [REPRO] target deferred to from §2.5, §6.1, §6.2,
§6.3, §5.4, §5.5); B = the deferred proof of Theorem 1(i), typeset from the sketch in §7.5
(sources: docs/T1_PROOF_SKELETON.md Lemma 1, docs/T1_HETERO_GENERAL.md fact 3).
Figure numbers here must match the built PDF (Fig 1-9, Table 1) — see build_paper.sh.
-->

# Reproduction

**Artifact.** The code, the request traces and the result files behind every figure and
table are packaged as `talg-artifact.zip`, released at

> `https://github.com/bruce5800/Postgraduate-Project/releases/tag/talg-submission-2026-08`

Unpack it and run the commands below from its root; `README.md` inside repeats the
essentials. The artifact also contains `budgetstakes/`, the Lean 4 development of
Appendix C (`lake build` replays the check). `results/` holds our own outputs, so a fresh run can be diffed against them
directly.

Every number in this paper is regenerated from a fixed seed by a single script. Almost
everything runs on a clean checkout of the artifact: the synthetic experiments generate
their own instances, and the request traces behind Sections 6.1, 6.3 and 8 are small
enough that we ship them with the artifact under `data/trace/`. One class is the
exception — the six real graphs of Section 6.2 (and the Phase-2 reproduction that reuses
them) are third-party datasets we do not redistribute, so they must be downloaded into
`data/realworld/` first. A dagger ($\dagger$) marks that class, and only that class, in
the map below; §A.4 says what each dataset is and where it comes from.

## Environment and conventions

- **Stack:** Python 3.12; NumPy 1.26, SciPy 1.13, NetworkX 3.3, Matplotlib (plots only).
- **Randomness:** every stream derives from one master seed (default `0`), spawned into
  independent reproducible sub-streams with NumPy's `default_rng(seed).spawn(k)` — one
  each for the graph, the arrival sequence, algorithm randomness and the perturbation.
- **Paired trials:** within a comparison every algorithm and every error level reuses the
  same graph, arrival sequence, $\mathrm{OPT}$ and tie-break seed.
- **Confidence intervals:** 95% normal-approximation half-widths over trials.
- **Flow decompositions.** Feldman, Jaillet–Lu and the serving advice $b$-matching consume
  the *decomposition* of a maximum flow, which — unlike the flow value — is not unique.
  Their networks label nodes with integers rather than strings, so the decomposition
  NetworkX returns is stable across runs; under string labels it followed the interpreter's
  per-process string hashing and every derived number moved between runs of the same
  script (Section 2.5).
- Runtimes below are wall-clock on one machine (Apple M4 Pro, 12 cores). The scripts are
  single-threaded apart from NumPy's own vectorization, so they scale with single-core
  speed.

## Result → script map

Each row names a *stem*. Unless the row says otherwise, its script is
`run_<stem>.py` under `scripts/`, and its outputs are `<stem>.json` and
`<stem>.png` under `results/`.

| Paper object | Script stem (or path) | $\approx$ time |
|---|---|---|
| **Table 1** (unified benchmark) | `unified_benchmark`, then `scripts/plot_unified_panels.py` for the panel charts and `_tables.md` | 100 s |
| **Fig. 1** (order error vs the ACI bound) | `order_vs_theory` | 30 s |
| §4 collapse statistics ($\rho_S$, $r$) | derived from `order_vs_theory.json`: rank and linear correlation of `kendall` against `loss`, pooled over all four models and all eleven levels | — |
| **Figs. 2–3** (envelope; prefix pathology) | `choo_bem` | 20 min |
| §5.3 recalibration | `recalibration` | 1.5 min |
| **Figs. 4, 5, 9** (payoff rule; $r$-sweep) | `directional_test` | 12 min |
| §5.4 decision-statistic variance | `measure_payoff_variance.py` (not a `run_` script) | 30 min |
| §5.5 eager-combiner mechanism check | `tests/test_combiner_small.py` (console) | 2 s |
| **Fig. 6** (real predictor) | `real_predictor` | 15 s |
| **Fig. 7** (six real graphs) $\dagger$ | `realworld_robustness`, plus its `_tables.md` | 65 s |
| §6.3 rank vs regression training | `rank_vs_mse_mve`, `rank_when_it_matters`, `rank_real_trace` | 40 s |
| **Fig. 8** (budget–stakes scissors) | `impossibility_frontier` | 6 s |
| §7 numerical verification | `scripts/verify_witness_gap.py` and `verify_budget_stakes_hetero.py` (console) | seconds |
| §8 serving case study | `serving`, `serving_trace`, `serving_dynamic`, `prefix_cache`, `serving_slo_probe` | varies |
| Phase-2 reproduction of [Bor18] | `er_full`, `left_regular`, `realworld` $\dagger$ | 35 min |

Scripts live under `scripts/` and write to `results/`; all are run from the project root.
Seven hand-verifiable correctness anchors live under `tests/` (`for t in tests/test_*.py;
do python3 "$t"; done`).

## Order of execution

Two dependencies are not self-evident: `plot_unified_panels.py` and
`run_consistency_robustness.py` both consume `results/unified_benchmark.json` and must run
after `run_unified_benchmark.py`. Everything else is independent.

```bash
# self-contained (clean checkout, no external data)
python3 scripts/run_unified_benchmark.py       # Table 1 (data)
python3 scripts/plot_unified_panels.py         # Table 1 (panel charts; needs the line above)
python3 scripts/run_order_vs_theory.py         # Fig 1
python3 scripts/run_directional_test.py        # Figs 4, 5, 9
python3 scripts/run_impossibility_frontier.py  # Fig 8
python3 scripts/verify_witness_gap.py          # Lemma 2, directional test, plug-in blindness
python3 scripts/verify_budget_stakes_hetero.py # heterogeneous profiles, slack identity
python3 scripts/measure_payoff_variance.py     # decision-statistic sd quoted in 5.4
python3 scripts/run_choo_bem.py                # Figs 2, 3   (~20 min)

# run on the traces shipped in data/trace/
python3 scripts/run_real_predictor.py          # Fig 6
python3 scripts/run_rank_real_trace.py         # 6.3, real-feature arm

# require data/realworld/ to be downloaded first (see A.4)
python3 scripts/run_realworld_robustness.py    # Fig 7
```

## Data provenance

The request traces ship with the artifact under `data/trace/`. The third-party graph
datasets do not, and must be placed under `data/realworld/` before the daggered scripts
will run.

- **Real graphs (Section 6.2).** Six graphs from the Network Repository
  (networkrepository.com): socfb-Caltech36, socfb-Reed98, bio-CE-GN, bio-CE-PG,
  econ-beause and econ-mbeaflw, downloaded as MatrixMarket or edge-list files,
  reduced to simple undirected graphs, and made bipartite by a random balanced partition.
- **Traces (Sections 6.1, 6.3, 8).** Wikipedia "top articles per day" for four days from
  the Wikimedia REST pageviews API (`data/trace/wiki/`; the live day is the truth, earlier
  days are the 1-, 7- and 30-day-stale forecasts); the Azure LLM inference trace from
  Microsoft's public Azure dataset release (`data/trace/azure_llm/`; context and generated
  token counts with timestamps); and the Mooncake conversation trace
  (`data/trace/mooncake/`; per-request prefix-cache block hashes). The Wikipedia data is a
  snapshot of a live source rather than a static benchmark, so exact reproduction requires
  the same snapshot, not merely the same API.

# Proof of Theorem 1(i)

Section 7.5 gives the argument in outline; we record it in full here, since it is the
lower half of the paper's main theorem. Recall the setting: a cell family with profile
$\{(\theta_i,\varepsilon_i)\}_{i\le m}$, specialist mass
$\sigma^2 = \sum_i\theta_i/N$ with $N=\sum_i(1+\theta_i)=\mathrm{OPT}$, and a scenario
pair $(G,\mathrm{Bd})$ that shares one advice and flips the advice-agreement of a cell set
$W$ whose per-cell signals satisfy $\varepsilon_i \le \varepsilon_W$. Its payoff gap is
$g=\tfrac2N\sum_{i\in W}\theta_i\varepsilon_i$.

**Claim.** Every test-and-fallback algorithm $A_k$ that decides by an arbitrary measurable
(possibly randomized) function of the prefix $X_{1:k}$ and the advice, with
$k=o\!\big(1/(\varepsilon_W g)\big)$, has $\eta_c+\eta_r \ge 1-o(1)$.

*Proof.* By Lemma 1 it suffices to show $\gamma_k := \mathrm{TV}(\mathcal L_G,\mathcal
L_{\mathrm{Bd}}) = o(1)$, where $\mathcal L_\cdot$ is the law of the prefix under each
scenario; Lemma 1 then gives $(1-\eta_c)\le\eta_r+\gamma_k+o(1)$, i.e.
$\eta_c+\eta_r\ge 1-o(1)$.

*Step 1 (the coupling).* Arrivals are i.i.d., so $\mathcal L_G = P^{\otimes k}$ and
$\mathcal L_{\mathrm{Bd}} = Q^{\otimes k}$ for the two per-arrival laws $P,Q$ on the type
set. The two scenarios differ only in the specialist bias $s_i$ of the cells in $W$:
outside $W$, and on every flexible type, $P$ and $Q$ assign identical mass, and the
coupling that leaves those arrivals untouched is exact there. Inside a flipped cell
$i\in W$, the two specialist types carry masses $\tfrac{\theta_i}{N}(\tfrac12+\varepsilon_i)$
and $\tfrac{\theta_i}{N}(\tfrac12-\varepsilon_i)$ under $P$, and the same two masses
swapped under $Q$.

*Step 2 (per-sample Hellinger distance).* Writing $H^2(P,Q)=\sum_x(\sqrt{P(x)}-\sqrt{Q(x)})^2$,
only the $2|W|$ swapped atoms contribute, and cell $i$ contributes
$$2\,\frac{\theta_i}{N}\Big(\sqrt{\tfrac12+\varepsilon_i}-\sqrt{\tfrac12-\varepsilon_i}\Big)^{2}
\;=\; \frac{2\theta_i}{N}\Big(1-\sqrt{1-4\varepsilon_i^{2}}\Big),$$
using $(\sqrt a-\sqrt b)^2 = a+b-2\sqrt{ab}$ with $a+b=1$ and $ab=\tfrac14-\varepsilon_i^2$.
Since $2t \le 1-\sqrt{1-4t} \le 4t$ for $t=\varepsilon_i^2\in[0,\tfrac14]$,
$$H^2(P,Q) \;=\; \sum_{i\in W}\frac{2\theta_i}{N}\Big(1-\sqrt{1-4\varepsilon_i^{2}}\Big)
\;\in\; [4,8]\cdot\frac{1}{N}\sum_{i\in W}\theta_i\varepsilon_i^{2}.$$
Bounding each $\varepsilon_i$ by $\varepsilon_W$ in one factor,
$$H^2(P,Q) \;\le\; \frac{8}{N}\sum_{i\in W}\theta_i\varepsilon_i^{2}
\;\le\; 4\varepsilon_W\cdot\frac{2}{N}\sum_{i\in W}\theta_i\varepsilon_i
\;=\; 4\,\varepsilon_W\,g .$$

*Step 3 (tensorization).* With $h^2 := H^2/2 = 1-\mathrm{BC}(P,Q)$ the normalized squared
Hellinger distance, the Bhattacharyya coefficient of a product measure is the product of
the coefficients, so $1-h^2(P^{\otimes k},Q^{\otimes k}) = (1-h^2(P,Q))^k$ and hence
$h^2(P^{\otimes k},Q^{\otimes k}) \le k\,h^2(P,Q)$.

*Step 4 (to total variation).* The standard comparison
$\mathrm{TV}\le h\sqrt{2-h^{2}}\le\sqrt2\,h$ gives
$$\gamma_k \;\le\; \sqrt2\,h(P^{\otimes k},Q^{\otimes k}) \;\le\; \sqrt{2k\,h^2(P,Q)}
\;=\; \sqrt{k\,H^2(P,Q)} \;\le\; \sqrt{4k\,\varepsilon_W\,g}.$$
Steps 3–4, chained with Lemma 1, are machine-checked in the form
$(1-\eta_c)\le\eta_r+\sqrt{2k\,(1-\mathrm{BC}(P,Q))}$ for arbitrary finite $P,Q$ and
every $[0,1]$-valued rule on the $k$-prefix (`Scenario.master_tradeoff_iid`, Appendix C);
Steps 1–2 are the explicit evaluation on the family.

*Step 5 (conclusion).* If $k=o\!\big(1/(\varepsilon_W g)\big)$ then
$k\,\varepsilon_W g\to0$, so $\gamma_k\to0$: the prefix is asymptotically uninformative
about which scenario is in force, and Lemma 1 converts that into
$\eta_c+\eta_r\ge1-o(1)$. Here $o(1)$ is taken along any sequence of families and prefix
lengths with $k\varepsilon_W g\to0$; the $o(1)$ inside Lemma 1 additionally absorbs the
$O(k/n)$ contribution of the prefix itself to the ratio, which is why the sublinearity
assumption $k=o(n)$ is in force. $\qed$

**Where the two halves meet.** Theorem 1(ii) spends
$k=O(\sigma^2/\min(\delta,\Delta)^2)$, while (i) forbids $k=o(1/(\varepsilon_W g))$. On a
balanced pair $\min(\delta,\Delta)=g/2$, so the gap between the two is the ratio
$\sigma^2\varepsilon_W/g$. Cauchy–Schwarz on the definition of $g$ gives
$g^2 \le \tfrac4N\,\sigma_W^2\sum_{i\in W}\theta_i\varepsilon_i^2$ with $\sigma_W^2$ the
flipped mass, so that ratio is $\Theta(1)$ — and the two sides agree up to logarithms —
exactly when the stakes are carried, at comparable signal levels, by a constant fraction
of the specialist mass. When instead they hide in a vanishing sliver of low-signal cells
the ratio can diverge; that regime is open (Section 7.8).

# Machine-checked statements

The statistical chain behind Section 7 is formalized in Lean 4 (v4.33.0) over Mathlib, in
the `budgetstakes/` directory of the artifact: seven files, 66 theorems and lemmas, no
`sorry`. `lake build` replays the check in about a minute once the Mathlib cache is
fetched, and the repository's continuous integration runs it on every commit. The
development is deliberately self-contained — a distribution is a vector of real weights on
a finite type, expectations are finite sums, and independence enters through a single
combinatorial identity, $\sum_{x\in\Omega^k}\prod_i g(x_i)=\big(\sum_\omega g(\omega)\big)^k$ —
so that a reader can audit it without measure theory. The table maps the paper's
statements to theorem names.

| Statement in the paper | Lean theorem | Form proved |
|------|----------|----------|
| Lemma 2 (payoff identity), §7.4 | `CellFamily.payoff_identity` | heterogeneous profile, arbitrary truth biases, from the cell constants |
| $1-\rho_{\mathrm{base}}=\sigma^2/2$, §7.3 | `CellFamily.`\allowbreak`slack_eq_half_specialistMass` | exact |
| affine law and $\rho_{\mathrm{perfect}}-\rho_{\mathrm{base}}\le 2\varepsilon_{\max}(1-\rho_{\mathrm{base}})$, §7.3 | `CellFamily.affine_law`, `CellFamily.`\allowbreak`rhoPerfect_sub_rhoBase_le_slack` | exact |
| Lemma 1 (master trade-off), §7.2 | `Scenario.master_tradeoff` | exact, no $o(1)$: $(1-\eta_c)\le\eta_r+\mathrm{TV}$ for every $[0,1]$-valued rule on a finite prefix space |
| Theorem 1(ii), upper half | `FinDist.`\allowbreak`iid_prob_sum_nonpos_le` | finite Chernoff, $P^{\otimes k}(\sum c\le0)\le e^{-k\mu^2/4}$ for $\lvert c\rvert\le1$, $\mu=\mathbb E[c]$; with $\mu\ge2\min(\delta,\Delta)$ this is error $\le e^{-k\min(\delta,\Delta)^2}$ |
| Theorem 1(ii), $\sigma^2$-scaling | `FinDist.`\allowbreak`iid_prob_sum_nonpos_le_cheb` | exact prefix variance $k\,\mathrm{Var}(c)$ and Chebyshev, error $\le\mathrm{Var}(c)/(k\mu^2)$; with $\mathrm{Var}(c)\le\mathbb E[c^2]=\sigma^2$ this is $\sigma^2/(4k\min(\delta,\Delta)^2)$ |
| Theorem 1(i): Appendix B Steps 3–4 chained with Lemma 1 | `Scenario.`\allowbreak`master_tradeoff_iid` | $(1-\eta_c)\le\eta_r+\sqrt{2k\,(1-\mathrm{BC}(P,Q))}$ for arbitrary finite $P,Q$ and every rule on the $k$-prefix (tensorization `bc_iid`, comparison `tvDist_iid_le`) |
| Remark in §7.8 (random order), lower half | `FinDist.`\allowbreak`shuffled_iid_expect` | a uniformly shuffled i.i.d. sample has the product law |
| Remark in §7.8 (random order), upper half | `RandomOrder.`\allowbreak`ro_prob_sum_nonpos_le` | without-replacement prefix sum: variance $\le k\,\mathbb E_{\mathrm{pop}}[c^2]$, error $\le\mathbb E_{\mathrm{pop}}[c^2]/(k\mu^2)$ |

What is *not* formalized, so that the certificate is not over-read: (a) the cell constants
of §7.3 ($\mathrm{OPT}=1+\theta_i$, baseline $1+\theta_i/2$, follow gain
$\theta_i\lvert s_i-\tfrac12\rvert$), which the development takes as the definition of the
model; (b) Steps 1–2 of Appendix B — the explicit evaluation
$1-\mathrm{BC}=\tfrac1N\sum_{i\in W}\theta_i\big(1-\sqrt{1-4\varepsilon_i^2}\big)$ and the
$[2t,4t]$ bounds — two lines of algebra on the page; (c) Bernstein's inequality, i.e. the
$\sigma^2$-dependence *inside the exponent* of Theorem 1(ii) (the $\sigma^2$ scaling is
certified at Chebyshev grade only); (d) the $o(1)$ bookkeeping of the prefix's own $O(k/n)$
contribution, which the formal statements avoid by defining values as post-decision
ratios; and (e) exponential tails under random order, which we cite rather than reprove.
Nothing about the matching algorithms themselves is formalized: the development is about
the statistics of testing advice, which is what the law is.
