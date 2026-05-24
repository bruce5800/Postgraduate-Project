"""Ranking (Karp–Vazirani–Vazirani, STOC 1990).

Sample a uniformly random permutation of R prior to seeing online nodes,
then match each arrival to its lowest-ranked unmatched neighbor.
"""
from __future__ import annotations
import numpy as np

from algorithms._common import greedy_with_permutation


def ranking(
    instance_adj: list[list[int]],
    n_right: int,
    rng: np.random.Generator,
) -> int:
    """KVV Ranking. Returns matching size."""
    perm = rng.permutation(n_right)
    # perm[k] = which right-node sits at rank k
    # We need the inverse: rank[r] = position of r in perm
    rank = np.empty(n_right, dtype=np.int64)
    rank[perm] = np.arange(n_right)
    return greedy_with_permutation(instance_adj, rank)
