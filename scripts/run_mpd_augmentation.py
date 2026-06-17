"""Phase 3b: (MPD)-augmented known-i.i.d. algorithms vs their (g) and base forms.

ACI §7 claims the (MPD) augmentation — using the min-predicted-degree rule
(with type-graph degrees) where the base non-greedy algorithm would skip —
"always beats the base algorithms and often beats the greedy (g) versions."

We test this for FeldmanEtAl and JailletLu on the two graph families where
offline-degree information carries signal (clvb_zipf strongest, left_regular
milder). Paired trials: the three variants of each algorithm share the same
JailletLu list-sampling / MPD tie-break randomness, isolating the fallback rule.

Outputs per graph family:
  results/mpd_augment_<graph>.json
  results/mpd_augment_<graph>.png    horizontal bar chart, sorted by ratio
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
from optimal import max_matching_size
from algorithms.greedy import simple_greedy
from algorithms.ranking import ranking
from algorithms.min_predicted_degree import mpd, mpd_rank
from algorithms.feldman import (
    feldman_preprocess, feldman_online, feldman_online_greedy, feldman_online_mpd,
)
from algorithms.jaillet_lu import (
    jaillet_lu_preprocess, jaillet_lu_online, jaillet_lu_online_greedy,
    jaillet_lu_online_mpd,
)
from predictions.degree_truth import type_graph_degree, instance_degree


ALGOS = [
    "Ranking", "SimpleGreedy", "MPD", "MinDegree",
    "FeldmanEtAl", "FeldmanEtAl(g)", "FeldmanEtAl(MPD)",
    "JailletLu", "JailletLu(g)", "JailletLu(MPD)",
]


def run_family(name, gen, n, n_trials, seed):
    master = np.random.default_rng(seed)
    rng_graph, rng_inst, rng_seed = master.spawn(3)
    seeds = rng_seed.integers(0, 2**31 - 1, size=(n_trials, 2))

    acc = {a: [] for a in ALGOS}
    for t in range(n_trials):
        type_adj = gen(rng_graph)
        f_Mb, f_Mr = feldman_preprocess(type_adj, n_right=n)
        j_rn, j_rp = jaillet_lu_preprocess(type_adj, n_right=n)
        mu = type_graph_degree(type_adj, n_right=n)

        instance_adj, types = sample_instance(type_adj, m=n, rng=rng_inst)
        opt = max_matching_size(instance_adj, n_right=n)
        if opt == 0:
            continue
        mu_real = instance_degree(instance_adj, n_right=n)
        s_rank, s_jl = int(seeds[t, 0]), int(seeds[t, 1])
        rank = mpd_rank(mu, np.random.default_rng(s_rank))

        acc["Ranking"].append(ranking(instance_adj, n, np.random.default_rng(s_rank)) / opt)
        acc["SimpleGreedy"].append(simple_greedy(instance_adj, n) / opt)
        acc["MPD"].append(mpd(instance_adj, n, mu, np.random.default_rng(s_rank)) / opt)
        acc["MinDegree"].append(mpd(instance_adj, n, mu_real, np.random.default_rng(s_rank)) / opt)

        acc["FeldmanEtAl"].append(feldman_online(instance_adj, types, n, f_Mb, f_Mr) / opt)
        acc["FeldmanEtAl(g)"].append(feldman_online_greedy(instance_adj, types, n, f_Mb, f_Mr) / opt)
        acc["FeldmanEtAl(MPD)"].append(
            feldman_online_mpd(instance_adj, types, n, f_Mb, f_Mr, rank) / opt)

        # JailletLu variants share the SAME list-sampling randomness (s_jl).
        acc["JailletLu"].append(
            jaillet_lu_online(instance_adj, types, n, j_rn, j_rp, np.random.default_rng(s_jl)) / opt)
        acc["JailletLu(g)"].append(
            jaillet_lu_online_greedy(instance_adj, types, n, j_rn, j_rp, np.random.default_rng(s_jl)) / opt)
        acc["JailletLu(MPD)"].append(
            jaillet_lu_online_mpd(instance_adj, types, n, j_rn, j_rp, np.random.default_rng(s_jl), rank) / opt)

    res = {"graph": name, "n": n, "n_trials": n_trials, "seed": seed,
           "mean": {a: float(np.mean(acc[a])) for a in ALGOS},
           "std": {a: float(np.std(acc[a])) for a in ALGOS}}
    return res


def report(res):
    name = res["graph"]
    print(f"\n=== {name} (n={res['n']}, {res['n_trials']} trials) ===")
    ordered = sorted(ALGOS, key=lambda a: -res["mean"][a])
    for a in ordered:
        print(f"  {a:20s} {res['mean'][a]:.4f} ± {res['std'][a]:.4f}")
    # The ACI §7 claim, checked per algorithm.
    print("  -- ACI §7 claim (MPD) ≥ (g) ≥ base --")
    for base in ["FeldmanEtAl", "JailletLu"]:
        b, g, m = res["mean"][base], res["mean"][f"{base}(g)"], res["mean"][f"{base}(MPD)"]
        ok = "OK" if (m >= g - 1e-9 and g >= b - 1e-9) else "VIOLATED"
        print(f"  {base:12s} base={b:.4f}  (g)={g:.4f}  (MPD)={m:.4f}   [{ok}]")


def plot_family(res, out_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    name = res["graph"]
    ordered = sorted(ALGOS, key=lambda a: res["mean"][a])  # ascending for barh
    vals = [res["mean"][a] for a in ordered]
    errs = [res["std"][a] for a in ordered]

    def color(a):
        if "(MPD)" in a:
            return "C2"
        if "(g)" in a:
            return "C0"
        if a in ("MPD", "MinDegree", "Ranking"):
            return "C4"
        return "C3"  # base non-greedy

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(ordered, vals, xerr=errs, color=[color(a) for a in ordered],
            alpha=0.85, error_kw={"alpha": 0.4})
    ax.set_xlabel("competitive ratio (alg / OPT)")
    ax.set_xlim(min(vals) - 0.03, 1.0)
    ax.set_title(f"(MPD)-augmentation vs (g) and base — {name}\n"
                 f"green=(MPD)  blue=(g)  red=base non-greedy  purple=degree/random refs")
    ax.grid(True, axis="x", alpha=0.3)
    for i, (v, a) in enumerate(zip(vals, ordered)):
        ax.text(v + 0.002, i, f"{v:.3f}", va="center", fontsize=8)
    fig.savefig(out_dir / f"mpd_augment_{name}.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


def main(n=1000, n_trials=100, seed=0, zipf_exponent=1.0):
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    families = {
        "left_regular": lambda rng: left_regular_bipartite(n, 5, rng),
        "clvb_zipf": lambda rng: clvb_zipf_bipartite(n, zipf_exponent, rng),
    }
    t0 = time.time()
    for name, gen in families.items():
        res = run_family(name, gen, n, n_trials, seed)
        (out_dir / f"mpd_augment_{name}.json").write_text(json.dumps(res, indent=2))
        report(res)
        plot_family(res, out_dir)
    print(f"\ntotal elapsed: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
