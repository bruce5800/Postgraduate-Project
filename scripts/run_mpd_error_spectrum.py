"""RQ2 headline experiment: MPD competitive ratio vs prediction-error strength.

For each graph family and each of the four error models, sweep error strength
η ∈ [0,1] and plot the empirical competitive ratio of MinPredictedDegree given
the perturbed degree predictor. Two theoretical anchors bound every curve:

    η = 0  →  MPD(true type-graph degree)        (its natural operating point)
    MinDegree (perfect realized-degree oracle)   = consistency ceiling
    Ranking (random predictor)                   = robustness floor

Trials are PAIRED: all (model, η) cells reuse the same per-trial graph, instance,
OPT, and MPD tie-break seed, so differences are attributable to μ perturbation
alone.

Outputs per graph family:
  results/mpd_spectrum_<graph>.json
  results/mpd_spectrum_<graph>.png            ratio vs η, 4 models + anchors
  results/mpd_methodological_<graph>.png      ratio vs L1 magnitude, 4 overlaid
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.synthetic import left_regular_bipartite, clvb_zipf_bipartite
from iid_sampler import sample_instance
from algorithms.min_predicted_degree import mpd
from algorithms.ranking import ranking
from optimal import max_matching_size
from predictions.degree_truth import type_graph_degree, instance_degree
from predictions import error_models as em


MODELS = ["random_flip", "systematic_bias", "adversarial", "distribution_drift"]
MODEL_LABEL = {
    "random_flip": "random flip",
    "systematic_bias": "systematic bias",
    "adversarial": "adversarial",
    "distribution_drift": "distribution drift",
}


def _perturb(model, mu, mu_alt, eta, rng):
    if model == "random_flip":
        return em.random_flip(mu, eta, rng)
    if model == "systematic_bias":
        return em.systematic_bias(mu, eta, rng)
    if model == "adversarial":
        return em.adversarial(mu, eta, rng)
    if model == "distribution_drift":
        return em.distribution_drift(mu, mu_alt, eta, rng)
    raise ValueError(model)


def run_family(name, gen, n, n_trials, etas, seed):
    master = np.random.default_rng(seed)
    rng_graph, rng_inst, rng_alt, rng_seed, rng_pert = master.spawn(5)
    trial_seeds = rng_seed.integers(0, 2**31 - 1, size=n_trials)

    # Pre-generate paired trials with shared OPT / anchors.
    trials = []
    anchor_mindeg, anchor_ranking, anchor_mpd0 = [], [], []
    for t in range(n_trials):
        type_adj = gen(rng_graph)
        instance_adj, types = sample_instance(type_adj, m=n, rng=rng_inst)
        opt = max_matching_size(instance_adj, n_right=n)
        if opt == 0:
            continue
        mu_true = type_graph_degree(type_adj, n_right=n)
        mu_alt = type_graph_degree(gen(rng_alt), n_right=n)  # drift reference
        mu_realized = instance_degree(instance_adj, n_right=n)
        ts = int(trial_seeds[t])
        anchor_mindeg.append(mpd(instance_adj, n, mu_realized, np.random.default_rng(ts)) / opt)
        anchor_ranking.append(ranking(instance_adj, n, np.random.default_rng(ts)) / opt)
        anchor_mpd0.append(mpd(instance_adj, n, mu_true, np.random.default_rng(ts)) / opt)
        trials.append((instance_adj, types, opt, mu_true, mu_alt, ts))

    res = {
        "graph": name, "n": n, "n_trials": len(trials), "seed": seed,
        "etas": list(etas),
        "anchor_mindegree": float(np.mean(anchor_mindeg)),
        "anchor_ranking": float(np.mean(anchor_ranking)),
        "anchor_mpd0": float(np.mean(anchor_mpd0)),
        "models": {},
    }

    for model in MODELS:
        ratio_mean, ratio_std, l1_mean, order_mean = [], [], [], []
        for eta in etas:
            ratios, l1s, ords = [], [], []
            for (instance_adj, types, opt, mu_true, mu_alt, ts) in trials:
                mu_p, errs = _perturb(model, mu_true, mu_alt, float(eta), rng_pert)
                size = mpd(instance_adj, n, mu_p, np.random.default_rng(ts))
                ratios.append(size / opt)
                l1s.append(errs["l1"])
                ords.append(errs["order_error"])
            ratio_mean.append(float(np.mean(ratios)))
            ratio_std.append(float(np.std(ratios)))
            l1_mean.append(float(np.mean(l1s)))
            order_mean.append(float(np.mean(ords)))
        res["models"][model] = {
            "ratio_mean": ratio_mean, "ratio_std": ratio_std,
            "l1_mean": l1_mean, "order_error_mean": order_mean,
        }
        print(f"  [{name}] {model:18s} "
              f"η0={ratio_mean[0]:.3f} → η1={ratio_mean[-1]:.3f}  "
              f"(order_err η1={order_mean[-1]:.3f})")
    return res


def plot_family(res, out_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    name = res["graph"]
    etas = np.array(res["etas"])
    colors = {"random_flip": "C0", "systematic_bias": "C2",
              "adversarial": "C3", "distribution_drift": "C1"}

    # Plot 1: ratio vs η, with anchors.
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.axhline(res["anchor_mindegree"], ls=":", color="k", alpha=0.7,
               label=f"MinDegree (ceiling) = {res['anchor_mindegree']:.3f}")
    ax.axhline(res["anchor_ranking"], ls="--", color="gray", alpha=0.7,
               label=f"Ranking (floor) = {res['anchor_ranking']:.3f}")
    for model in MODELS:
        m = np.array(res["models"][model]["ratio_mean"])
        s = np.array(res["models"][model]["ratio_std"])
        ax.plot(etas, m, marker="o", markersize=4, color=colors[model],
                label=MODEL_LABEL[model])
        ax.fill_between(etas, m - s, m + s, alpha=0.12, color=colors[model])
    ax.set_xlabel("error strength η")
    ax.set_ylabel("competitive ratio (MPD / OPT)")
    ax.set_title(f"MPD performance vs prediction-error strength — {name} (n={res['n']}, {res['n_trials']} trials)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower left", fontsize=9)
    fig.savefig(out_dir / f"mpd_spectrum_{name}.png", dpi=120, bbox_inches="tight")
    plt.close(fig)

    # Plot 2: ratio vs ORDER-ERROR (methodological). Tests whether MPD's ratio is
    # governed by Kendall-τ order-error alone, independent of which model made it.
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.axhline(res["anchor_ranking"], ls="--", color="gray", alpha=0.7,
               label=f"Ranking floor = {res['anchor_ranking']:.3f}")
    for model in MODELS:
        oe = np.array(res["models"][model]["order_error_mean"])
        m = np.array(res["models"][model]["ratio_mean"])
        ax.plot(oe, m, marker="s", markersize=5, color=colors[model],
                linestyle="none", label=MODEL_LABEL[model], alpha=0.8)
    ax.set_xlabel("predictor order-error  (normalized Kendall-τ distance)")
    ax.set_ylabel("competitive ratio (MPD / OPT)")
    ax.set_title(f"Ratio collapses onto order-error — {name}\n"
                 f"(systematic bias pinned at order-error 0; magnitude is irrelevant)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower left", fontsize=9)
    fig.savefig(out_dir / f"mpd_methodological_{name}.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


def main(n=1000, n_trials=100, seed=0, zipf_exponent=1.0):
    etas = np.round(np.arange(0.0, 1.01, 0.1), 2)
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)

    families = {
        "left_regular": lambda rng: left_regular_bipartite(n, 5, rng),
        "clvb_zipf": lambda rng: clvb_zipf_bipartite(n, zipf_exponent, rng),
    }

    t0 = time.time()
    for name, gen in families.items():
        print(f"\n=== {name} ===")
        res = run_family(name, gen, n, n_trials, etas, seed)
        (out_dir / f"mpd_spectrum_{name}.json").write_text(json.dumps(res, indent=2))
        plot_family(res, out_dir)
        print(f"  saved: mpd_spectrum_{name}.{{json,png}}, mpd_methodological_{name}.png")
    print(f"\ntotal elapsed: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
