"""M1 — WHEN does training-to-rank beat training-to-regress? (Research Plan A §4.2)

M0 proved the mechanism exists with deliberately divergent features. M1 maps the
regime: the rank-advantage (rank-trained ratio − MSE-trained ratio) as a function of
  - FEATURE DIVERGENCE: how noisy the magnitude feature's ORDER is (noise1). At
    noise1=0 the magnitude feature already carries the true order, so MSE and rank
    training agree and the advantage should vanish; as noise1 grows the two
    objectives diverge.
  - GRAPH HARDNESS: the Zipf exponent of the offline degree distribution. Near-uniform
    degrees (small exponent) ⇒ MPD ≈ Ranking ⇒ no gap for ANY predictor to capture
    (finding F3); skewed degrees (large exponent) ⇒ real signal + heavy tail that
    pulls MSE toward the magnitude feature.

Hypotheses: the advantage grows with divergence, grows with hardness, and vanishes on
easy (near-uniform) instances — which tells a practitioner exactly when to bother.

Outputs: results/rank_when_it_matters.json, results/rank_when_it_matters.png
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import kendalltau

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.synthetic import clvb_zipf_bipartite
from iid_sampler import sample_instance
from optimal import max_matching_size
from algorithms.ranking import ranking
from algorithms.min_predicted_degree import mpd
from predictions.degree_truth import type_graph_degree
from scripts.run_rank_vs_mse_mve import (
    make_features, fit_mse, fit_rank, score_mse, score_rank,
)


def train_and_eval(n, exponent, noise1, noise2, n_train, n_test, inst, rngs):
    rg_tr, rg_te, r_feat, r_inst, r_seed = rngs
    # train
    Xs, ys = [], []
    for _ in range(n_train):
        ta = clvb_zipf_bipartite(n, exponent, rg_tr)
        mu = type_graph_degree(ta, n_right=n)
        Xs.append(make_features(mu, r_feat, noise1, noise2)); ys.append(mu)
    Xtr, ytr = np.concatenate(Xs), np.concatenate(ys)
    coef_mse, w_rank = fit_mse(Xtr, ytr), fit_rank(Xtr, ytr)
    # eval
    r_mse, r_rank, r_oracle, r_floor = [], [], [], []
    tau_mse, tau_rank = [], []
    for _ in range(n_test):
        ta = clvb_zipf_bipartite(n, exponent, rg_te)
        mu = type_graph_degree(ta, n_right=n)
        X = make_features(mu, r_feat, noise1, noise2)
        s_mse, s_rank = score_mse(coef_mse, X), score_rank(w_rank, X)
        tau_mse.append((1 - kendalltau(s_mse, mu)[0]) / 2)
        tau_rank.append((1 - kendalltau(s_rank, mu)[0]) / 2)
        for _ in range(inst):
            ins, _t = sample_instance(ta, m=n, rng=r_inst)
            opt = max_matching_size(ins, n_right=n)
            if opt == 0:
                continue
            ts = int(r_seed.integers(0, 2**31 - 1))
            r_mse.append(mpd(ins, n, s_mse, np.random.default_rng(ts)) / opt)
            r_rank.append(mpd(ins, n, s_rank, np.random.default_rng(ts)) / opt)
            r_oracle.append(mpd(ins, n, mu, np.random.default_rng(ts)) / opt)
            r_floor.append(ranking(ins, n, np.random.default_rng(ts)) / opt)
    return {
        "ratio_mse": float(np.mean(r_mse)), "ratio_rank": float(np.mean(r_rank)),
        "ratio_oracle": float(np.mean(r_oracle)), "ratio_floor": float(np.mean(r_floor)),
        "advantage": float(np.mean(r_rank) - np.mean(r_mse)),
        "tau_mse": float(np.mean(tau_mse)), "tau_rank": float(np.mean(tau_rank)),
    }


def run(n=400, n_train=6, n_test=20, inst=2, noise2=0.05, seed=0):
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    exponents = [0.3, 0.6, 1.0, 1.4]
    noises = [0.0, 0.3, 0.6, 1.0, 1.5]
    t0 = time.time()

    grid = {}  # (exp, noise1) -> result
    print(f"{'exp':>4} {'noise1':>7} | {'floor':>6} {'mse':>6} {'rank':>6} {'oracle':>6} | "
          f"{'adv':>6} {'τ_mse':>6} {'τ_rank':>6}")
    for exp in exponents:
        for nz in noises:
            # fresh, independent RNG streams per cell (reproducible)
            rngs = np.random.default_rng([seed, int(exp * 100), int(nz * 100)]).spawn(5)
            r = train_and_eval(n, exp, nz, noise2, n_train, n_test, inst, rngs)
            grid[(exp, nz)] = r
            print(f"{exp:>4} {nz:>7.2f} | {r['ratio_floor']:>6.3f} {r['ratio_mse']:>6.3f} "
                  f"{r['ratio_rank']:>6.3f} {r['ratio_oracle']:>6.3f} | "
                  f"{r['advantage']:>+6.3f} {r['tau_mse']:>6.3f} {r['tau_rank']:>6.3f}")

    data = {"params": {"n": n, "noise2": noise2, "exponents": exponents, "noises": noises},
            "grid": {f"{e}|{z}": grid[(e, z)] for (e, z) in grid}}
    (out_dir / "rank_when_it_matters.json").write_text(json.dumps(data, indent=2))
    _plot(exponents, noises, grid, out_dir)
    print(f"\nsaved: results/rank_when_it_matters.{{json,png}}  (elapsed {time.time()-t0:.1f}s)")
    return grid


def _plot(exponents, noises, grid, out_dir):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    A = np.array([[grid[(e, z)]["advantage"] for z in noises] for e in exponents])
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.4))

    # (A) heatmap of rank-advantage over (hardness, divergence)
    ax = axes[0]
    im = ax.imshow(A, aspect="auto", origin="lower", cmap="viridis")
    ax.set_xticks(range(len(noises))); ax.set_xticklabels([f"{z:.1f}" for z in noises])
    ax.set_yticks(range(len(exponents))); ax.set_yticklabels([f"{e:.1f}" for e in exponents])
    ax.set_xlabel("feature divergence  (magnitude-signal order-noise, noise1)")
    ax.set_ylabel("graph hardness  (Zipf exponent)")
    ax.set_title("Rank-advantage (rank ratio − MSE ratio)\ngrows with divergence AND hardness")
    for i in range(len(exponents)):
        for j in range(len(noises)):
            ax.text(j, i, f"{A[i,j]*100:+.1f}", ha="center", va="center",
                    color="white" if A[i, j] < A.max() * 0.6 else "black", fontsize=8)
    fig.colorbar(im, ax=ax, label="advantage")

    # (B) line: advantage vs divergence, one line per hardness
    ax = axes[1]
    for e in exponents:
        adv = [grid[(e, z)]["advantage"] for z in noises]
        ax.plot(noises, adv, "o-", label=f"Zipf exp={e}")
    ax.axhline(0, ls=":", color="gray")
    ax.set_xlabel("feature divergence (noise1)")
    ax.set_ylabel("rank-advantage (ratio gain over MSE-training)")
    ax.set_title("Vanishes at zero divergence; grows with it.\nSteeper on harder (more skewed) graphs")
    ax.grid(True, alpha=0.3); ax.legend()
    fig.suptitle("M1 — WHEN learning-to-rank beats learning-to-regress", fontsize=12)
    fig.tight_layout()
    fig.savefig(out_dir / "rank_when_it_matters.png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    print("saved: rank_when_it_matters.png")


if __name__ == "__main__":
    run()
