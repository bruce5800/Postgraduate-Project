"""Reproduce Borodin et al. (2018) Fig 9, restricted to SimpleGreedy and Ranking.

ER bipartite, n=1000, c ∈ {0.1, 0.3, ..., 14.9} (75 points), 100 trials per c.
Each trial: 1 type graph + 1 i.i.d. instance, compute ratio against OPT (HK).

Independent RNG streams (numpy 1.25+ spawn) for graph / instance / algo
so that adding algorithms later does not perturb earlier results.
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
from optimal import max_matching_size


def main(n: int = 1000, n_trials: int = 100, seed: int = 0) -> None:
    cs = np.round(np.arange(0.1, 15.0, 0.2), 2)
    rng_graph, rng_instance, rng_algo = np.random.default_rng(seed).spawn(3)

    results = {
        "n": n,
        "n_trials": n_trials,
        "seed": seed,
        "cs": cs.tolist(),
        "simple_greedy": {"mean": [], "std": []},
        "ranking": {"mean": [], "std": []},
    }

    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    t0 = time.time()

    for ci, c in enumerate(cs):
        sg_ratios, rk_ratios = [], []
        for _ in range(n_trials):
            type_adj = erdos_renyi_bipartite(n, float(c), rng_graph)
            instance_adj, _ = sample_instance(type_adj, m=n, rng=rng_instance)
            opt = max_matching_size(instance_adj, n_right=n)
            if opt == 0:
                sg_ratios.append(1.0)
                rk_ratios.append(1.0)
                continue
            sg = simple_greedy(instance_adj, n_right=n)
            rk = ranking(instance_adj, n_right=n, rng=rng_algo)
            sg_ratios.append(sg / opt)
            rk_ratios.append(rk / opt)

        sg_m, sg_s = float(np.mean(sg_ratios)), float(np.std(sg_ratios))
        rk_m, rk_s = float(np.mean(rk_ratios)), float(np.std(rk_ratios))
        results["simple_greedy"]["mean"].append(sg_m)
        results["simple_greedy"]["std"].append(sg_s)
        results["ranking"]["mean"].append(rk_m)
        results["ranking"]["std"].append(rk_s)

        elapsed = time.time() - t0
        eta = elapsed / (ci + 1) * (len(cs) - ci - 1)
        print(
            f"[{ci+1:2d}/{len(cs)}] c={c:5.2f}  "
            f"SG={sg_m:.4f}±{sg_s:.4f}  Rk={rk_m:.4f}±{rk_s:.4f}  "
            f"elapsed={elapsed:5.1f}s  eta={eta:5.1f}s"
        )

    out_json = out_dir / "er_full.json"
    out_json.write_text(json.dumps(results, indent=2))
    print(f"\nsaved: {out_json}")

    # Plot
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 5))
        sg_m = np.array(results["simple_greedy"]["mean"])
        sg_s = np.array(results["simple_greedy"]["std"])
        rk_m = np.array(results["ranking"]["mean"])
        rk_s = np.array(results["ranking"]["std"])
        ax.plot(cs, sg_m, label="SimpleGreedy", marker="o", markersize=3)
        ax.fill_between(cs, sg_m - sg_s, sg_m + sg_s, alpha=0.2)
        ax.plot(cs, rk_m, label="Ranking", marker="s", markersize=3)
        ax.fill_between(cs, rk_m - rk_s, rk_m + rk_s, alpha=0.2)
        ax.set_xlabel("c (avg degree = c, p = c/n)")
        ax.set_ylabel("competitive ratio (alg / OPT)")
        ax.set_title(f"Erdős–Rényi bipartite, n={n}, {n_trials} trials per c")
        ax.grid(True, alpha=0.3)
        ax.legend()
        out_png = out_dir / "er_full.png"
        fig.savefig(out_png, dpi=120, bbox_inches="tight")
        print(f"saved: {out_png}")
    except ImportError:
        print("(matplotlib not available — skipping plot)")


if __name__ == "__main__":
    main()
