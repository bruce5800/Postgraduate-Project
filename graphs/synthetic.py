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


def left_regular_bipartite(n: int, d: int, rng: np.random.Generator) -> list[list[int]]:
    """d-regular-on-the-left bipartite type graph.

    Each ℓ ∈ L samples a uniformly random subset of d distinct vertices from R.
    |L| = |R| = n. Each ℓ has degree exactly d; the R-side degrees vary.
    """
    if d > n:
        raise ValueError(f"d={d} exceeds n={n}")
    return [rng.choice(n, size=d, replace=False).tolist() for _ in range(n)]
