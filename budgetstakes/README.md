# budgetstakes — a Lean 4 formalization of the budget–stakes law

Machine-checked companion to the paper *The Limits of Predictions for Online Bipartite
Matching: A Unified Experimental Study and a Budget–Stakes Law* (Zhuolun Li, 2026) and to
the thesis outlook (§10.2). Everything the paper's §7 rests on — the payoff identity, the
slack identity, the affine law, the master trade-off inequality, and **both halves of the
budget–stakes law at the abstract level** — is proved here and accepted by the Lean 4 kernel.

| | |
|---|---|
| Toolchain | Lean `v4.33.0`, Mathlib `v4.33.0` (pinned in `lakefile.toml` / `lean-toolchain`) |
| Size | 7 files, **66 theorems/lemmas, 0 `sorry`** (`grep -c sorry Budgetstakes/*.lean`) |
| Design | finite probability only — a `FinDist` is a vector of real weights; no measure theory, no external Lean projects |
| Check | `lake exe cache get && lake build` (≈ 30 s after the Mathlib cache); CI: `.github/workflows/lean_action_ci.yml` |

Proof scripts were drafted with LLM assistance (Anthropic's Claude) and revised by the
author; what certifies them is the kernel check, not their provenance.

## File map (one file per stage)

| File | Stage | Content | #thm |
|---|---|---|---|
| `PayoffIdentity.lean` | 1 | `CellFamily` (heterogeneous cells `θᵢ ∈ (0,1]`, `eᵢ ∈ [−½,½]`); **payoff identity** `E[score] = 2·stakes`; **slack identity** `1 − ρ_base = σ²/2` | 4 |
| `AffineLaw.lean` | 2 | **affine law** `ρ_follow = ρ_perfect − ℓ₁/2`; `ρ_follow − ρ_base = stakes`; `ρ_perfect − ρ_base ≤ ε σ²` | 7 |
| `MasterTradeoff.lean` | 3 | `FinDist`, `expect`, `tvDist`; **coupling bound** `E_P D − E_Q D ≤ TV`; `Scenario` and the **master trade-off** `(1 − η_c) ≤ η_r + TV(L_G, L_Bd)`, exact | 8 |
| `Chernoff.lean` | 4 | `sum_prod_eq_pow` (the one independence identity); `iid` product law; **finite Chernoff** `P^k(∑c ≤ 0) ≤ exp(−kμ²/4)` — Theorem 1(ii), Hoeffding-weak | 9 |
| `Hellinger.lean` | 5 | Bhattacharyya coefficient, **tensorization** `bc(P^k,Q^k) = bc^k`, `TV² ≤ 2(1−bc)`, Bernoulli; `TV(P^k,Q^k) ≤ √(2k(1−bc))`; **`master_tradeoff_iid`** — Theorem 1(i), abstract core | 11 |
| `RandomOrder.lean` | 7 | `variance`, **Chebyshev**; exact `Var(∑c(xᵢ)) = k·Var(c)` under `iid` ⇒ **σ²-sharp scaling at Chebyshev grade**; shuffling an i.i.d. prefix is law-invariant (lower bound transfers to random order); **random-order model**: uniform permutations, exchangeability via transitivity (no counting), finite-population variance `≤ k·E_pop[c²]`, `Pr(∑ ≤ 0) ≤ E_pop[c²]/(kμ²)` | 27 |

## Paper ↔ Lean

| Paper statement | Lean name |
|---|---|
| Lemma 2, payoff identity | `CellFamily.payoff_identity` |
| §7.3, `1 − ρ_base = σ²/2` | `CellFamily.slack_eq_half_specialistMass` |
| affine law `ρ_follow = ρ_perfect − ℓ₁/2` | `CellFamily.affine_law` |
| Lemma 1, master trade-off (exact, non-asymptotic) | `Scenario.master_tradeoff` |
| Theorem 1(ii), achievability (Hoeffding-weak constants) | `FinDist.iid_prob_sum_nonpos_le` |
| Theorem 1(ii), σ²-sharp scaling (Chebyshev grade) | `FinDist.iid_prob_sum_nonpos_le_cheb` |
| Theorem 1(i), impossibility (abstract core) | `Scenario.master_tradeoff_iid` |
| Random-order model (T5): upper bound | `RandomOrder.ro_prob_sum_nonpos_le` |
| Random-order model (T5): lower-bound transfer | `FinDist.shuffled_iid_expect` |

## What is *not* formalized (honest boundary)

* The cell-family instantiation of the Hellinger computation,
  `1 − bc = (1/N)·∑_{i∈W} θᵢ(1 − √(1 − 4eᵢ²))` (planned Stage 5b) — the abstract bound is
  proved for arbitrary finite `P, Q`; the concrete evaluation is in the paper.
* Bernstein's inequality (Stage 6): the σ²-sharp *exponential* tail. The σ²-sharp
  *scaling* is proved at Chebyshev grade (`1/δ` instead of `log 1/δ`).
* The `o(1)` prefix bookkeeping of the paper's ratio statements; here values are
  post-decision ratios, which makes the inequalities exact.
* Exponential tails under random order (Hoeffding's convex-order theorem / Serfling);
  the Yao-style reduction of the random-order lower bound is stated at the level of laws
  (`shuffled_iid_expect`), the instance-dependent-stakes `o(1)` is paper-level.
* Nothing about the matching algorithms themselves (values of Mimic/Ranking on graphs);
  the formalization is about the statistics of testing advice, which is what the law is.

## Layout

```
budgetstakes/
├── Budgetstakes.lean            # root import
├── Budgetstakes/
│   ├── Basic.lean
│   ├── PayoffIdentity.lean      # Stage 1
│   ├── AffineLaw.lean           # Stage 2
│   ├── MasterTradeoff.lean      # Stage 3
│   ├── Chernoff.lean            # Stage 4
│   ├── Hellinger.lean           # Stage 5
│   └── RandomOrder.lean         # Stage 7
├── lakefile.toml · lean-toolchain · lake-manifest.json
└── .github/workflows/lean_action_ci.yml
```

License: Apache-2.0 (see `LICENSE`).
