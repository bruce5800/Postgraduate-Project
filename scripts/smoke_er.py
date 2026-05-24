"""Smoke test: SimpleGreedy vs OPT on ER bipartite type graphs at c=4.9.

Paper Fig 16: SimpleGreedy ratio ≈ 0.83 at c=4.9, n=1000.
Acceptance: mean ratio falls in [0.80, 0.86].
"""
from __future__ import annotations
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.synthetic import erdos_renyi_bipartite
from iid_sampler import sample_instance
from algorithms.greedy import simple_greedy
from optimal import max_matching_size


def run(n: int = 1000, c: float = 4.9, n_type_graphs: int = 20, seed: int = 0) -> None:
    rng = np.random.default_rng(seed)
    ratios = []
    t0 = time.time()
    for k in range(n_type_graphs):
        type_adj = erdos_renyi_bipartite(n, c, rng)
        instance_adj, _ = sample_instance(type_adj, m=n, rng=rng)
        sg = simple_greedy(instance_adj, n_right=n)
        opt = max_matching_size(instance_adj, n_right=n)
        ratios.append(sg / opt if opt > 0 else 0.0)
        print(f"  trial {k+1:2d}/{n_type_graphs}: SG={sg}  OPT={opt}  ratio={ratios[-1]:.4f}")
    mean = float(np.mean(ratios))
    std = float(np.std(ratios))
    elapsed = time.time() - t0
    print()
    print(f"n={n}, c={c}, trials={n_type_graphs}")
    print(f"SimpleGreedy / OPT  mean = {mean:.4f}  std = {std:.4f}")
    print(f"elapsed: {elapsed:.1f}s")
    print()
    if 0.80 <= mean <= 0.86:
        print(f"PASS: mean {mean:.4f} is within paper band [0.80, 0.86] (Fig 16 ≈ 0.83).")
    else:
        print(f"FAIL: mean {mean:.4f} is OUTSIDE expected band [0.80, 0.86].")


if __name__ == "__main__":
    run()
