"""Shared online matching primitives."""
from __future__ import annotations
import numpy as np


def greedy_with_permutation(
    instance_adj: list[list[int]],
    rank: np.ndarray,
) -> int:
    """Match each arriving left node to its lowest-ranked unmatched neighbor.

    rank[r] gives the rank of right node r; ties broken by smaller rank wins.
    Returns the matching size.
    """
    n_right = len(rank)
    matched = np.zeros(n_right, dtype=bool)
    size = 0
    for neighbors in instance_adj:
        best = -1
        best_rank = np.iinfo(np.int64).max
        for r in neighbors:
            if not matched[r] and rank[r] < best_rank:
                best_rank = rank[r]
                best = r
        if best != -1:
            matched[best] = True
            size += 1
    return size
