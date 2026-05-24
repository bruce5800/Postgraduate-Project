"""Reproduce Borodin et al. (2018) ER experiments (Fig 9, core-4 algorithms).

Algorithms: SimpleGreedy, Ranking, FeldmanEtAl(/g), JailletLu(/g).  Six lines.
ER bipartite, n=1000, c ∈ {0.1, 0.3, ..., 14.9}, 100 trials per c.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.synthetic import erdos_renyi_bipartite
from iid_sampler import sample_instance
from algorithms.greedy import simple_greedy
from algorithms.ranking import ranking
from algorithms.feldman import feldman_preprocess, feldman_online, feldman_online_greedy
from algorithms.jaillet_lu import (
    jaillet_lu_preprocess,
    jaillet_lu_online,
    jaillet_lu_online_greedy,
)
from optimal import max_matching_size


ALGOS = ["simple_greedy", "ranking", "feldman_ng", "feldman_g", "jaillet_ng", "jaillet_g"]
SHORT = {
    "simple_greedy": "SG", "ranking": "Rk",
    "feldman_ng": "FNG", "feldman_g": "FG",
    "jaillet_ng": "JNG", "jaillet_g": "JG",
}


def main(n: int = 1000, n_trials: int = 100, seed: int = 0) -> None:
    cs = np.round(np.arange(0.1, 15.0, 0.2), 2)
    rng_graph, rng_instance, rng_rk, rng_jl = np.random.default_rng(seed).spawn(4)

    results: dict = {
        "n": n,
        "n_trials": n_trials,
        "seed": seed,
        "cs": cs.tolist(),
        **{a: {"mean": [], "std": []} for a in ALGOS},
    }

    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    t_start = time.time()

    for ci, c in enumerate(cs):
        per_algo: dict[str, list[float]] = {a: [] for a in ALGOS}
        for _ in range(n_trials):
            type_adj = erdos_renyi_bipartite(n, float(c), rng_graph)
            f_Mb, f_Mr = feldman_preprocess(type_adj, n_right=n)
            j_rn, j_rp = jaillet_lu_preprocess(type_adj, n_right=n)
            instance_adj, types = sample_instance(type_adj, m=n, rng=rng_instance)
            opt = max_matching_size(instance_adj, n_right=n)
            if opt == 0:
                for a in ALGOS:
                    per_algo[a].append(1.0)
                continue
            per_algo["simple_greedy"].append(simple_greedy(instance_adj, n) / opt)
            per_algo["ranking"].append(ranking(instance_adj, n, rng=rng_rk) / opt)
            per_algo["feldman_ng"].append(
                feldman_online(instance_adj, types, n, f_Mb, f_Mr) / opt
            )
            per_algo["feldman_g"].append(
                feldman_online_greedy(instance_adj, types, n, f_Mb, f_Mr) / opt
            )
            per_algo["jaillet_ng"].append(
                jaillet_lu_online(instance_adj, types, n, j_rn, j_rp, rng_jl) / opt
            )
            per_algo["jaillet_g"].append(
                jaillet_lu_online_greedy(instance_adj, types, n, j_rn, j_rp, rng_jl) / opt
            )

        line = [f"[{ci+1:2d}/{len(cs)}] c={c:5.2f}"]
        for a in ALGOS:
            m, s = float(np.mean(per_algo[a])), float(np.std(per_algo[a]))
            results[a]["mean"].append(m)
            results[a]["std"].append(s)
            line.append(f"{SHORT[a]}={m:.3f}")
        elapsed = time.time() - t_start
        eta = elapsed / (ci + 1) * (len(cs) - ci - 1)
        line.append(f"elapsed={elapsed:5.1f}s  eta={eta:5.1f}s")
        print("  ".join(line))

    out_json = out_dir / "er_full.json"
    out_json.write_text(json.dumps(results, indent=2))
    print(f"\nsaved: {out_json}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 6))
        style = {
            "simple_greedy": ("SimpleGreedy", "o", "-", "C0"),
            "ranking": ("Ranking", "s", "-", "C1"),
            "feldman_g": ("FeldmanEtAl(g)", "^", "-", "C2"),
            "feldman_ng": ("FeldmanEtAl", "v", "--", "C3"),
            "jaillet_g": ("JailletLu(g)", "D", "-", "C4"),
            "jaillet_ng": ("JailletLu", "x", "--", "C5"),
        }
        for a, (label, marker, ls, color) in style.items():
            m = np.array(results[a]["mean"])
            s = np.array(results[a]["std"])
            ax.plot(cs, m, label=label, marker=marker, markersize=3, linestyle=ls, color=color)
            ax.fill_between(cs, m - s, m + s, alpha=0.12, color=color)
        ax.set_xlabel("c (edge prob p = c/n)")
        ax.set_ylabel("competitive ratio (alg / OPT)")
        ax.set_title(f"Erdős–Rényi bipartite, n={n}, {n_trials} trials per c — Borodin et al. (2018) Fig 9 partial reproduction")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="lower right", ncol=2)
        out_png = out_dir / "er_full.png"
        fig.savefig(out_png, dpi=120, bbox_inches="tight")
        print(f"saved: {out_png}")
    except ImportError:
        print("(matplotlib not available)")


if __name__ == "__main__":
    main()
