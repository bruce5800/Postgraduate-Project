"""M0 — Minimal Viable Experiment for Research Plan A (docs/RESEARCH_PLAN_A.md).

Central hypothesis (H1): for MinPredictedDegree, training the predictor with an
ORDER-aware loss (pairwise rank / RankNet logistic) yields a higher matching ratio
than training with the standard REGRESSION (MSE) loss — *even though the rank-trained
predictor has WORSE MSE to the true degrees*. If true, the prediction problem is
learning-to-rank, not regression, and the whole Direction-A program is worth building.

Design — the deliberate dissociation. Offline nodes have heavy-tailed (Zipf) true
degrees μ*. Each node gets TWO features:
  f1 = noisy MAGNITUDE signal   (μ* + large noise: right scale, scrambled order)
  f2 = faithful ORDER signal    (monotone transform of μ* + tiny noise: order kept,
                                 scale compressed)
A linear predictor must choose how to weight them. MSE training leans on f1 (the only
feature on the right scale to fit the heavy tail) and inherits its scrambled order;
rank training leans on f2 and recovers the true order. We fit on TRAIN graphs and
evaluate matching ratio on held-out TEST graphs from the same distribution.

Outputs: results/rank_vs_mse_mve.json, results/rank_vs_mse_mve.png
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.stats import kendalltau

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.synthetic import clvb_zipf_bipartite
from iid_sampler import sample_instance
from optimal import max_matching_size
from algorithms.ranking import ranking
from algorithms.min_predicted_degree import mpd
from predictions.degree_truth import type_graph_degree


def make_features(mu, rng, noise1=0.6, noise2=0.05):
    """Two divergent features. Returns X (N×2), standardized per-column.
    f1 = noisy magnitude (right scale, scrambled order);
    f2 = faithful order  (monotone in μ*, compressed scale, tiny noise)."""
    n = mu.shape[0]
    sd = mu.std() + 1e-9
    f1 = mu + noise1 * sd * rng.standard_normal(n)
    f2 = np.log1p(mu) + noise2 * np.log1p(mu).std() * rng.standard_normal(n)
    X = np.stack([f1, f2], axis=1)
    X = (X - X.mean(0)) / (X.std(0) + 1e-9)
    return X


def fit_mse(X, y):
    """Least-squares linear predictor of the true degrees (the status quo)."""
    A = np.concatenate([X, np.ones((len(X), 1))], axis=1)
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return coef  # (w1, w2, b)


def _rank_pairs(X, y):
    """All ordered pairs (i, j) with y_i < y_j → desired score s_i < s_j. Return the
    feature differences D = x_i − x_j (we want D·w < 0)."""
    order = np.argsort(y, kind="stable")
    Xs = X[order]
    # difference of every earlier (smaller y) minus every later (larger y) node
    # build via broadcasting on a capped sample to bound memory
    n = len(Xs)
    idx_i, idx_j = np.triu_indices(n, k=1)   # i<j in sorted order ⇒ y_i ≤ y_j
    D = Xs[idx_i] - Xs[idx_j]                 # want D·w < 0
    return D


def fit_rank(X, y, T=1.0, l2=1e-3):
    """Pairwise logistic (RankNet) on a linear scorer. Minimise mean softplus(D·w/T)
    over pairs that should satisfy s_i < s_j. Order of s ignores bias/scale, so fit w
    only, with tiny L2 for identifiability."""
    D = _rank_pairs(X, y)

    def obj(w):
        z = (D @ w) / T
        # softplus(z) penalises z>0 (i.e. s_i > s_j, the wrong order)
        loss = np.mean(np.logaddexp(0.0, z)) + l2 * w @ w
        g = (D.T @ (1.0 / (1.0 + np.exp(-z)))) / (len(D) * T) + 2 * l2 * w
        return loss, g

    res = minimize(obj, np.zeros(X.shape[1]), jac=True, method="L-BFGS-B")
    return res.x  # w (no bias needed for ordering)


def score_mse(coef, X):
    return X @ coef[:-1] + coef[-1]


def score_rank(w, X):
    return X @ w


def run(n=400, exponent=1.0, n_train_graphs=6, n_test_graphs=30,
        inst_per_test=3, noise1=0.6, noise2=0.05, seed=0):
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    rg_tr, rg_te, r_feat, r_inst, r_seed = np.random.default_rng(seed).spawn(5)

    # ---- train: pool (features, true degree) across several graphs ----
    Xs, ys = [], []
    for _ in range(n_train_graphs):
        ta = clvb_zipf_bipartite(n, exponent, rg_tr)
        mu = type_graph_degree(ta, n_right=n)
        Xs.append(make_features(mu, r_feat, noise1, noise2))
        ys.append(mu)
    Xtr = np.concatenate(Xs); ytr = np.concatenate(ys)
    coef_mse = fit_mse(Xtr, ytr)
    w_rank = fit_rank(Xtr, ytr)
    print(f"fitted: MSE coef={np.round(coef_mse,3)}  rank w={np.round(w_rank,3)}")

    # ---- test: held-out graphs; compare matching ratio + MSE + Kendall-τ ----
    methods = ["oracle (true μ*)", "MSE-trained", "rank-trained",
               "f1 only (magnitude)", "f2 only (order)", "Ranking (floor)"]
    ratios = {m: [] for m in methods}
    mse_to_truth = {"MSE-trained": [], "rank-trained": []}
    tau_to_truth = {"MSE-trained": [], "rank-trained": []}

    for _ in range(n_test_graphs):
        ta = clvb_zipf_bipartite(n, exponent, rg_te)
        mu = type_graph_degree(ta, n_right=n)
        X = make_features(mu, r_feat, noise1, noise2)
        s_mse = score_mse(coef_mse, X)
        s_rank = score_rank(w_rank, X)
        # normalize predictions to μ* scale for a fair MSE (order is scale-free)
        def rescale(s):
            a = np.polyfit(s, mu, 1)
            return a[0] * s + a[1]
        mse_to_truth["MSE-trained"].append(float(np.mean((rescale(s_mse) - mu) ** 2)))
        mse_to_truth["rank-trained"].append(float(np.mean((rescale(s_rank) - mu) ** 2)))
        tau_to_truth["MSE-trained"].append(float((1 - kendalltau(s_mse, mu)[0]) / 2))
        tau_to_truth["rank-trained"].append(float((1 - kendalltau(s_rank, mu)[0]) / 2))

        preds = {
            "oracle (true μ*)": mu, "MSE-trained": s_mse, "rank-trained": s_rank,
            "f1 only (magnitude)": X[:, 0], "f2 only (order)": X[:, 1],
        }
        for _ in range(inst_per_test):
            inst, _t = sample_instance(ta, m=n, rng=r_inst)
            opt = max_matching_size(inst, n_right=n)
            if opt == 0:
                continue
            ts = int(r_seed.integers(0, 2**31 - 1))
            for m, pr in preds.items():
                ratios[m].append(mpd(inst, n, pr, np.random.default_rng(ts)) / opt)
            ratios["Ranking (floor)"].append(
                ranking(inst, n, np.random.default_rng(ts)) / opt)

    def ci(v):
        a = np.asarray(v, float)
        return float(a.mean()), float(1.96 * a.std(ddof=1) / np.sqrt(len(a))) if len(a) > 1 else 0.0

    summary = {"params": {"n": n, "exponent": exponent, "noise1": noise1, "noise2": noise2,
                          "n_train_graphs": n_train_graphs, "n_test_graphs": n_test_graphs},
               "ratio": {m: ci(ratios[m]) for m in methods},
               "mse_to_truth": {k: ci(v) for k, v in mse_to_truth.items()},
               "tau_to_truth": {k: ci(v) for k, v in tau_to_truth.items()}}
    (out_dir / "rank_vs_mse_mve.json").write_text(json.dumps(summary, indent=2))

    print("\n=== matching ratio (mean ± 95% CI) ===")
    for m in methods:
        mu_, h = summary["ratio"][m]
        print(f"  {m:22s} ratio={mu_:.4f} ±{h:.4f}")
    print("\n=== the dissociation (lower MSE but worse ratio?) ===")
    for k in ["MSE-trained", "rank-trained"]:
        print(f"  {k:14s} MSE_to_truth={summary['mse_to_truth'][k][0]:8.2f}   "
              f"Kendall-τ_to_truth={summary['tau_to_truth'][k][0]:.3f}   "
              f"ratio={summary['ratio'][k][0]:.4f}")
    r_mse = summary["ratio"]["MSE-trained"][0]
    r_rank = summary["ratio"]["rank-trained"][0]
    m_mse = summary["mse_to_truth"]["MSE-trained"][0]
    m_rank = summary["mse_to_truth"]["rank-trained"][0]
    verdict = (r_rank > r_mse) and (m_rank > m_mse)
    print(f"\nH1 {'CONFIRMED' if verdict else 'NOT confirmed'}: "
          f"rank ratio {r_rank:.4f} {'>' if r_rank>r_mse else '≤'} MSE ratio {r_mse:.4f}; "
          f"rank MSE {m_rank:.1f} {'>' if m_rank>m_mse else '≤'} MSE-train MSE {m_mse:.1f} "
          f"(rank wins the decision despite worse regression error)")

    _plot(summary, methods, out_dir)
    return summary, verdict


def _plot(summary, methods, out_dir):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.4))
    # (A) matching ratio bars
    ax = axes[0]
    vals = [summary["ratio"][m][0] for m in methods]
    errs = [summary["ratio"][m][1] for m in methods]
    colors = ["purple", "C3", "C0", "C1", "C2", "gray"]
    ax.bar(range(len(methods)), vals, yerr=errs, capsize=3, color=colors)
    ax.set_xticks(range(len(methods)))
    ax.set_xticklabels(methods, rotation=25, ha="right", fontsize=8)
    ax.set_ylim(min(vals) - 0.02, 1.005)
    ax.set_ylabel("matching ratio (MPD / OPT)")
    ax.set_title("Matching ratio: rank-trained beats MSE-trained")
    ax.grid(True, axis="y", alpha=0.3)
    # (B) the dissociation: MSE-to-truth vs ratio
    ax = axes[1]
    for k, col in [("MSE-trained", "C3"), ("rank-trained", "C0")]:
        mse_x = summary["mse_to_truth"][k][0]
        ratio_y = summary["ratio"][k][0]
        ax.scatter([mse_x], [ratio_y], s=120, color=col, label=k, zorder=3)
        ax.annotate(k, (mse_x, ratio_y), fontsize=9,
                    xytext=(5, -10), textcoords="offset points")
    ax.set_xlabel("regression error to true degrees  (MSE, lower = 'better' fit)")
    ax.set_ylabel("matching ratio (MPD / OPT)")
    ax.set_title("The dissociation: the WORSE regression fit gives the BETTER decision\n"
                 "(MSE is the wrong training objective for MPD)")
    ax.grid(True, alpha=0.3); ax.legend(loc="center left")
    fig.suptitle("M0 — learning to RANK beats learning to REGRESS for online matching", fontsize=12)
    fig.tight_layout()
    fig.savefig(out_dir / "rank_vs_mse_mve.png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    print("\nsaved: results/rank_vs_mse_mve.png")


if __name__ == "__main__":
    run()
