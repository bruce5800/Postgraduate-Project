"""Reproduce Borodin et al. (2018) ER experiments (Fig 9, partial).

Algorithms: SimpleGreedy, Ranking, FeldmanEtAl, FeldmanEtAl(g).
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
from optimal import max_matching_size


ALGOS = ["simple_greedy", "ranking", "feldman_ng", "feldman_g"]


def main(n: int = 1000, n_trials: int = 100, seed: int = 0) -> None:
    cs = np.round(np.arange(0.1, 15.0, 0.2), 2)
    rng_graph, rng_instance, rng_algo = np.random.default_rng(seed).spawn(3)

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
            Mb, Mr = feldman_preprocess(type_adj, n_right=n)
            instance_adj, types = sample_instance(type_adj, m=n, rng=rng_instance)
            opt = max_matching_size(instance_adj, n_right=n)
            if opt == 0:
                for a in ALGOS:
                    per_algo[a].append(1.0)
                continue
            per_algo["simple_greedy"].append(simple_greedy(instance_adj, n) / opt)
            per_algo["ranking"].append(ranking(instance_adj, n, rng=rng_algo) / opt)
            per_algo["feldman_ng"].append(
                feldman_online(instance_adj, types, n, Mb, Mr) / opt
            )
            per_algo["feldman_g"].append(
                feldman_online_greedy(instance_adj, types, n, Mb, Mr) / opt
            )

        line = [f"[{ci+1:2d}/{len(cs)}] c={c:5.2f}"]
        for a in ALGOS:
            m, s = float(np.mean(per_algo[a])), float(np.std(per_algo[a]))
            results[a]["mean"].append(m)
            results[a]["std"].append(s)
            short = {"simple_greedy": "SG", "ranking": "Rk", "feldman_ng": "FNG", "feldman_g": "FG"}[a]
            line.append(f"{short}={m:.3f}")
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

        fig, ax = plt.subplots(figsize=(9, 5.5))
        style = {
            "simple_greedy": ("SimpleGreedy", "o", "-"),
            "ranking": ("Ranking", "s", "-"),
            "feldman_g": ("FeldmanEtAl(g)", "^", "-"),
            "feldman_ng": ("FeldmanEtAl", "v", "--"),
        }
        for a, (label, marker, ls) in style.items():
            m = np.array(results[a]["mean"])
            s = np.array(results[a]["std"])
            ax.plot(cs, m, label=label, marker=marker, markersize=3, linestyle=ls)
            ax.fill_between(cs, m - s, m + s, alpha=0.15)
        ax.set_xlabel("c (edge prob p = c/n)")
        ax.set_ylabel("competitive ratio (alg / OPT)")
        ax.set_title(f"Erdős–Rényi bipartite, n={n}, {n_trials} trials per c")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="lower right")
        out_png = out_dir / "er_full.png"
        fig.savefig(out_png, dpi=120, bbox_inches="tight")
        print(f"saved: {out_png}")
    except ImportError:
        print("(matplotlib not available — skipping plot)")


if __name__ == "__main__":
    main()
