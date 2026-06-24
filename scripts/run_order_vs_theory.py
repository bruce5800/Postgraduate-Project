"""Engage ACI (Aamand-Chen-Indyk 2022) Appendix D directly.

ACI Corollary D.2: on CLV-B graphs, MPD with a noisy degree predictor μ matches at
most  n − LIS(p[μ])  fewer nodes (in expectation) than MPD given the true expected
degrees, where p[μ] is the true weights ORDERED BY μ and LIS is the longest
non-decreasing subsequence. So ACI already establishes (i) the loss is governed by
an ORDER quantity (n−LIS), not magnitude, and (ii) a monotone (order-preserving)
predictor has p[μ] sorted ⇒ LIS=n ⇒ n−LIS=0 ⇒ zero loss. Our order-error finding
must therefore be framed NOT as 'order matters' (ACI has it) but as:
  (a) how TIGHT is ACI's n−LIS upper bound empirically (actual loss vs the bound);
  (b) which order measure best PREDICTS the loss — ACI's n−LIS vs Kendall-τ;
  (c) the cross-error-model COLLAPSE that ACI does not address.

This script measures, per (error model, η): the actual MPD matching loss vs the
unperturbed predictor, the ACI quantity n−LIS, and Kendall-τ — on CLV-B/Zipf.

Outputs: results/order_vs_theory.json, results/order_vs_theory.png
"""
from __future__ import annotations
import bisect
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import kendalltau

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.synthetic import clvb_zipf_bipartite
from iid_sampler import sample_instance
from algorithms.min_predicted_degree import mpd_rank
from algorithms._common import greedy_with_permutation
from predictions.degree_truth import type_graph_degree
from predictions import error_models as em

MODELS = ["random_flip", "systematic_bias", "adversarial", "distribution_drift"]
MODEL_LABEL = {"random_flip": "random flip", "systematic_bias": "systematic bias",
               "adversarial": "adversarial", "distribution_drift": "distribution drift"}


def _lis_nondecreasing(seq) -> int:
    """Longest non-decreasing subsequence length (patience sorting)."""
    tails: list[float] = []
    for x in seq:
        i = bisect.bisect_right(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


def _n_minus_lis(mu_true: np.ndarray, order: np.ndarray) -> int:
    """ACI's n − LIS(p[μ]): true weights in MPD's processing order, then the
    minimum deletions to sortedness = n − (longest non-decreasing subseq)."""
    seq = mu_true[order]
    return len(seq) - _lis_nondecreasing(seq.tolist())


def _perturb(model, mu, mu_alt, eta, rng):
    if model == "random_flip":
        return em.random_flip(mu, eta, rng)
    if model == "systematic_bias":
        return em.systematic_bias(mu, eta, rng)
    if model == "adversarial":
        return em.adversarial(mu, eta, rng)
    return em.distribution_drift(mu, mu_alt, eta, rng)


def main(n=1000, exponent=1.0, n_trials=40, seed=0):
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    etas = np.round(np.arange(0.0, 1.01, 0.1), 2)
    rng_graph, rng_inst, rng_alt, rng_seed, rng_pert = np.random.default_rng(seed).spawn(5)

    # Pre-generate paired trials.
    trials = []
    for _ in range(n_trials):
        type_adj = clvb_zipf_bipartite(n, exponent, rng_graph)
        instance_adj, types = sample_instance(type_adj, m=n, rng=rng_inst)
        mu_true = type_graph_degree(type_adj, n)          # ACI's "expected degrees"
        mu_alt = type_graph_degree(clvb_zipf_bipartite(n, exponent, rng_alt), n)
        ts = int(rng_seed.integers(0, 2**31 - 1))
        # reference: MPD with the true predictor
        rank0 = mpd_rank(mu_true, np.random.default_rng(ts))
        base_size = greedy_with_permutation(instance_adj, rank0)
        trials.append((instance_adj, mu_true, mu_alt, ts, base_size))

    res = {"n": n, "exponent": exponent, "n_trials": len(trials), "etas": etas.tolist(), "models": {}}
    t0 = time.time()
    for model in MODELS:
        rows = {"eta": [], "loss": [], "n_minus_lis": [], "kendall": []}
        for eta in etas:
            losses, nlis, ktau = [], [], []
            for (instance_adj, mu_true, mu_alt, ts, base_size) in trials:
                mu_p, _ = _perturb(model, mu_true, mu_alt, float(eta), rng_pert)
                rng_tb = np.random.default_rng(ts)
                rank = mpd_rank(mu_p, rng_tb)
                size = greedy_with_permutation(instance_adj, rank)
                losses.append(base_size - size)
                # MPD processing order = ascending rank
                order = np.argsort(rank, kind="stable")
                nlis.append(_n_minus_lis(mu_true, order))
                tau, _ = kendalltau(mu_true, mu_p)
                ktau.append(0.0 if np.isnan(tau) else (1.0 - tau) / 2.0)
            rows["eta"].append(float(eta))
            rows["loss"].append(float(np.mean(losses)))
            rows["n_minus_lis"].append(float(np.mean(nlis)))
            rows["kendall"].append(float(np.mean(ktau)))
        res["models"][model] = rows
        print(f"  {model:18s} loss(η1)={rows['loss'][-1]:6.1f}  "
              f"n-LIS(η1)={rows['n_minus_lis'][-1]:6.1f}  kτ(η1)={rows['kendall'][-1]:.3f}")

    (out_dir / "order_vs_theory.json").write_text(json.dumps(res, indent=2))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        colors = {"random_flip": "C0", "systematic_bias": "C2",
                  "adversarial": "C3", "distribution_drift": "C1"}

        fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
        # (A) actual loss vs ACI's n−LIS bound (all model×η points) + y=x bound.
        ax = axes[0]
        mx = 0.0
        for model in MODELS:
            r = res["models"][model]
            ax.scatter(r["n_minus_lis"], r["loss"], color=colors[model], s=28,
                       label=MODEL_LABEL[model], alpha=0.8)
            mx = max(mx, max(r["n_minus_lis"]))
        ax.plot([0, mx], [0, mx], "k--", alpha=0.6, label="ACI bound: loss ≤ n−LIS")
        ax.set_xlabel("ACI Appendix D quantity  n − LIS(p[μ])")
        ax.set_ylabel("actual MPD matching loss")
        ax.set_title("ACI's n−LIS is a valid but LOOSE upper bound\n(actual loss far below the bound)")
        ax.grid(True, alpha=0.3); ax.legend(fontsize=8, loc="upper left")
        # (B) loss vs Kendall-τ — the cross-model collapse.
        ax = axes[1]
        for model in MODELS:
            r = res["models"][model]
            ax.plot(r["kendall"], r["loss"], "o-", color=colors[model], markersize=4,
                    label=MODEL_LABEL[model])
        ax.set_xlabel("predictor order error  (Kendall-τ distance)")
        ax.set_ylabel("actual MPD matching loss")
        ax.set_title("Loss collapses onto Kendall-τ across all four error models\n"
                     "(the unification ACI does not provide)")
        ax.grid(True, alpha=0.3); ax.legend(fontsize=8, loc="upper left")
        fig.savefig(out_dir / "order_vs_theory.png", dpi=120, bbox_inches="tight")
        plt.close(fig)
        print("\nsaved: order_vs_theory.png")
    except ImportError:
        print("(matplotlib unavailable)")
    print(f"saved: results/order_vs_theory.json  (elapsed {time.time()-t0:.1f}s)")


if __name__ == "__main__":
    main()
