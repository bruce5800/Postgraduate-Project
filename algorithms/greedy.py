"""SimpleGreedy: GreedyWithPermutation under the identity (alphabetical) permutation."""
from __future__ import annotations
import numpy as np

from algorithms._common import greedy_with_permutation


def simple_greedy(instance_adj: list[list[int]], n_right: int) -> int:
    """Match each arriving node to its smallest-indexed unmatched neighbor."""
    rank = np.arange(n_right)
    return greedy_with_permutation(instance_adj, rank)
