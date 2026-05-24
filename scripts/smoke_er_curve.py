"""Smoke test (shape check): SimpleGreedy ratio across c for ER bipartite type graphs.

Paper Fig 10 / Discussion §5: SimpleGreedy on ER hits a global minimum around c=4.9
and is higher both for small c (sparse) and large c (dense). Verifies the U-shape.
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


def run(n: int = 1000, n_type_graphs: int = 20, seed: int = 0) -> None:
    cs = [0.5, 1.9, 4.9, 8.9, 14.9]
    rng = np.random.default_rng(seed)
    t0 = time.time()
    print(f"n={n}, trials per c = {n_type_graphs}")
    print(f"{'c':>6} | {'mean':>7} | {'std':>6}")
    print("-" * 28)
    results = {}
    for c in cs:
        ratios = []
        for _ in range(n_type_graphs):
            type_adj = erdos_renyi_bipartite(n, c, rng)
            instance_adj, _ = sample_instance(type_adj, m=n, rng=rng)
            sg = simple_greedy(instance_adj, n_right=n)
            opt = max_matching_size(instance_adj, n_right=n)
            ratios.append(sg / opt if opt > 0 else 1.0)
        results[c] = (float(np.mean(ratios)), float(np.std(ratios)))
        print(f"{c:>6.1f} | {results[c][0]:>7.4f} | {results[c][1]:>6.4f}")
    print()
    print(f"elapsed: {time.time()-t0:.1f}s")
    print()
    # Shape check: c=4.9 should be the local minimum vs both 1.9 and 14.9
    m1, m2, m3 = results[1.9][0], results[4.9][0], results[14.9][0]
    if m2 < m1 and m2 < m3:
        print(f"PASS: c=4.9 is a local minimum (1.9→{m1:.3f}, 4.9→{m2:.3f}, 14.9→{m3:.3f}).")
        print("Matches paper §5: 'greedy versions achieve a global minimum around c = 4.9'.")
    else:
        print(f"FAIL: expected U-shape with dip at c=4.9.")
        print(f"  got 1.9→{m1:.3f}, 4.9→{m2:.3f}, 14.9→{m3:.3f}")


if __name__ == "__main__":
    run()
