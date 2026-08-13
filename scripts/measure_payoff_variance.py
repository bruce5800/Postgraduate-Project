"""Measure the per-sample variance sigma^2 of the DirectionalTest decision
statistic on the benchmark's few-types family.

Paper §5.4 applies the budget-stakes law of §7 to the paper's own rule: resolving
stakes g needs a prefix of k ~ sigma^2/g^2, where sigma^2 is the per-sample variance
of the decision statistic d_hat.  §7 bounds sigma^2 by the specialist mass on the
*cell* family; the benchmark's few-types family is a different construction, so the
constant has to be measured rather than assumed.

The statistic (algorithms/test_and_match.directional_test_and_match) is

    d_hat = [V_corr(p_hat) - V_rank(p_hat)] / n,

a deterministic functional of the prefix's empirical type distribution p_hat, plus
simulation noise that the caller can drive to zero (n_sims / n_null are compute, not
samples).  Its sampling law is therefore exactly the law of the functional under
p_hat ~ Multinomial(k, p)/k, which is what we sample here.  If the budget-stakes
scaling governs the rule, Var(d_hat) ~ sigma^2/k, i.e. k * Var(d_hat) is flat in k;
that flat value is the sigma^2 quoted in §5.4.

Usage: python3 scripts/measure_payoff_variance.py
Output: results/payoff_variance.json
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.synthetic import few_types_bipartite
from iid_sampler import sample_instance
from algorithms.ranking import ranking
from predictions.type_advice import true_type_counts, build_advice_matching

N, R = 2000, 8
KS = [50, 100, 200, 400, 800]
N_DRAWS = 400          # independent prefixes per k
N_SIMS = 24            # Ranking shuffles per evaluation (simulation noise -> 0)
N_NULL = 64            # bootstrap redraws for the Jensen correction


def d_hat(phat, *, n, slots, type_adj, n_types, k, rng, n_sims, n_null):
    """The rule's decision statistic at a given empirical distribution."""
    v_obs = float(np.minimum(n * phat, slots).sum())
    boot = np.empty(n_null)
    for j in range(n_null):
        pt = rng.multinomial(k, phat) / k
        boot[j] = float(np.minimum(n * pt, slots).sum())
    v_corr = 2.0 * v_obs - float(boot.mean())

    counts = np.floor(n * phat).astype(np.int64)
    rem = n - int(counts.sum())
    if rem > 0:
        frac = n * phat - np.floor(n * phat)
        counts[np.argsort(-frac)[:rem]] += 1
    stream = np.repeat(np.arange(n_types), counts)
    v_rank = 0.0
    for _ in range(n_sims):
        s_ = stream.copy()
        rng.shuffle(s_)
        v_rank += float(ranking([type_adj[l] for l in s_], n, rng))
    v_rank /= n_sims
    return (v_corr - v_rank) / n


def main():
    rng = np.random.default_rng(20260813)
    type_adj = few_types_bipartite(N, R, rng)
    _, types = sample_instance(type_adj, m=N, rng=rng)
    c_star = true_type_counts(types, n_types=R)
    _, partners = build_advice_matching(type_adj, c_star, n_right=N)
    slots = np.array([len(p) for p in partners], dtype=np.float64)
    p_true = c_star / c_star.sum()          # the law the prefix is drawn from

    out = {"n": N, "r": R, "n_draws": N_DRAWS, "n_sims": N_SIMS,
           "n_null": N_NULL, "levels": []}
    for k in KS:
        vals = np.array([
            d_hat(rng.multinomial(k, p_true) / k, n=N, slots=slots,
                  type_adj=type_adj, n_types=R, k=k, rng=rng,
                  n_sims=N_SIMS, n_null=N_NULL)
            for _ in range(N_DRAWS)])
        var = float(vals.var(ddof=1))
        out["levels"].append({"k": k, "mean": float(vals.mean()),
                              "sd": float(vals.std(ddof=1)),
                              "var": var, "k_times_var": k * var})
        print(f"k={k:4d}  mean d={vals.mean():+.5f}  sd={vals.std(ddof=1):.5f}  "
              f"k*Var={k * var:.4f}")

    # How much of the spread above is simulation noise rather than sampling noise?
    # Hold p_hat fixed and vary only the rng: sampling noise is then zero.
    out["sim_floor"] = []
    for k in (200, 800):
        phat = rng.multinomial(k, p_true) / k
        v = np.array([
            d_hat(phat, n=N, slots=slots, type_adj=type_adj, n_types=R, k=k,
                  rng=rng, n_sims=N_SIMS, n_null=N_NULL)
            for _ in range(150)])
        out["sim_floor"].append({"k": k, "sd": float(v.std(ddof=1)),
                                 "var": float(v.var(ddof=1))})
        print(f"simulation-only noise at k={k}: sd={v.std(ddof=1):.5f}")

    kv = [lv["k_times_var"] for lv in out["levels"]]
    out["k_times_var_range"] = [float(min(kv)), float(max(kv))]
    print(f"\nk*Var over k: {min(kv):.4f}-{max(kv):.4f} (NOT flat -> the sigma^2/k "
          f"form of the cell family does not transfer verbatim to this estimator)")
    sd200 = next(lv["sd"] for lv in out["levels"] if lv["k"] == 200)
    print(f"sd at k=200 = {sd200:.4f}, against this family's stakes g = 0.02: "
          f"signal-to-noise {0.02 / sd200:.2f}")

    Path("results").mkdir(exist_ok=True)
    Path("results/payoff_variance.json").write_text(json.dumps(out, indent=1))
    print("wrote results/payoff_variance.json")


if __name__ == "__main__":
    main()
