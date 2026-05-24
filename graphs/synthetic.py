"""Synthetic type graphs for the known i.i.d. model."""
from __future__ import annotations
import numpy as np


def erdos_renyi_bipartite(n: int, c: float, rng: np.random.Generator) -> list[list[int]]:
    """Bipartite Erdős–Rényi type graph G_{n,n,p} with p = c/n.

    Returns adjacency as adj[l] = sorted list of right-neighbor indices for type l.
    |L| = |R| = n.
    """
    p = c / n
    mask = rng.random((n, n)) < p
    return [np.flatnonzero(mask[l]).tolist() for l in range(n)]
