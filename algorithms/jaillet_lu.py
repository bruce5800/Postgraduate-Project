"""JailletLu (Jaillet & Lu, 2014) for online bipartite matching under known i.i.d.

Pipeline:
  1. Solve LP (1) via the cap-3 max-flow trick (paper §2.5):
        s → r capacity 3, r → ℓ capacity 2, ℓ → t capacity 3
     Integral max flow f̃ gives the vertex solution f* = f̃ / 3 ∈ {0, 1/3, 2/3}.
  2. For each ℓ, the restricted neighborhood N'(ℓ) = {r : f*_{ℓ,r} > 0} has |N'(ℓ)| ≤ 3.
  3. Build a list-distribution D_ℓ over orderings of N'(ℓ):
       |N'(ℓ)| = 1: always the singleton list.
       |N'(ℓ)| = 2: ⟨r₁,r₂⟩ w.p. f*_{ℓ,r₁}, ⟨r₂,r₁⟩ w.p. f*_{ℓ,r₂};
                     remaining mass = dummy (leave unmatched).
       |N'(ℓ)| = 3: uniform over the 6 permutations.
  4. Online stage: sample list per arrival, match to first unmatched in list.
"""
from __future__ import annotations
import networkx as nx
import numpy as np


# ---------------------------- preprocessing -------------------------------

def _solve_cap3_flow(type_adj: list[list[int]], n_right: int) -> dict:
    """Solve max flow on the cap-3 network. Returns nx flow_dict."""
    g = nx.DiGraph()
    n_left = len(type_adj)
    for r in range(n_right):
        g.add_edge("s", ("r", r), capacity=3)
    for l in range(n_left):
        g.add_edge(("l", l), "t", capacity=3)
    for l, nbrs in enumerate(type_adj):
        for r in nbrs:
            g.add_edge(("r", r), ("l", l), capacity=2)
    _, flow = nx.maximum_flow(g, "s", "t")
    return flow


def jaillet_lu_preprocess(
    type_adj: list[list[int]], n_right: int
) -> tuple[list[list[int]], list[list[float]]]:
    """Returns (restricted_neighbors, restricted_probs).

    restricted_neighbors[ℓ] = list of r ∈ N'(ℓ), in any deterministic order.
    restricted_probs[ℓ]     = matching list of f*_{ℓ,r} values (each ∈ {1/3, 2/3}).
    Lengths are 0, 1, 2, or 3.
    """
    n_left = len(type_adj)
    flow = _solve_cap3_flow(type_adj, n_right)
    rn: list[list[int]] = [[] for _ in range(n_left)]
    rp: list[list[float]] = [[] for _ in range(n_left)]
    for l, nbrs in enumerate(type_adj):
        for r in nbrs:
            f_val = flow.get(("r", r), {}).get(("l", l), 0)
            if f_val > 0:  # f_val ∈ {1, 2}
                rn[l].append(r)
                rp[l].append(f_val / 3.0)
    return rn, rp


# ------------------------------ online stage ------------------------------

def _sample_list(
    neighbors: list[int], probs: list[float], rng: np.random.Generator
) -> list[int]:
    """Sample a list per the JailletLu rules. Empty list = dummy (skip)."""
    k = len(neighbors)
    if k == 0:
        return []
    if k == 1:
        # Single restricted neighbor: always try it.
        return [neighbors[0]]
    if k == 2:
        u = rng.random()
        if u < probs[0]:
            return [neighbors[0], neighbors[1]]
        if u < probs[0] + probs[1]:
            return [neighbors[1], neighbors[0]]
        return []  # dummy (only possible when probs[0] + probs[1] = 2/3)
    if k == 3:
        # Uniform over the 6 permutations.
        perm = rng.permutation(3)
        return [neighbors[i] for i in perm]
    raise ValueError(f"unexpected |N'(ℓ)| = {k}")


def jaillet_lu_online(
    instance_adj: list[list[int]],
    types: np.ndarray,
    n_right: int,
    rn: list[list[int]],
    rp: list[list[float]],
    rng: np.random.Generator,
) -> int:
    """Non-greedy: only match to neighbors in the sampled list."""
    matched = np.zeros(n_right, dtype=bool)
    size = 0
    for i in range(len(instance_adj)):
        l = int(types[i])
        lst = _sample_list(rn[l], rp[l], rng)
        for r in lst:
            if not matched[r]:
                matched[r] = True
                size += 1
                break
    return size


def jaillet_lu_online_greedy(
    instance_adj: list[list[int]],
    types: np.ndarray,
    n_right: int,
    rn: list[list[int]],
    rp: list[list[float]],
    rng: np.random.Generator,
) -> int:
    """Greedy: if list exhausted, fall back to any available neighbor of ℓ."""
    matched = np.zeros(n_right, dtype=bool)
    size = 0
    for i, neighbors in enumerate(instance_adj):
        l = int(types[i])
        lst = _sample_list(rn[l], rp[l], rng)
        target = -1
        for r in lst:
            if not matched[r]:
                target = r
                break
        if target == -1:
            for r in neighbors:
                if not matched[r]:
                    target = r
                    break
        if target != -1:
            matched[target] = True
            size += 1
    return size


def jaillet_lu_online_mpd(
    instance_adj: list[list[int]],
    types: np.ndarray,
    n_right: int,
    rn: list[list[int]],
    rp: list[list[float]],
    rng: np.random.Generator,
    rank: np.ndarray,
) -> int:
    """JailletLu(MPD) — ACI §7 augmentation.

    Identical to the greedy variant, except the fallback (when the sampled list
    has no available neighbor) picks the unmatched neighbor of MINIMUM MPD rank
    instead of an arbitrary one. `rank` is the MPD rank array (mpd_rank(mu, rng)).
    """
    matched = np.zeros(n_right, dtype=bool)
    size = 0
    for i, neighbors in enumerate(instance_adj):
        l = int(types[i])
        lst = _sample_list(rn[l], rp[l], rng)
        target = -1
        for r in lst:
            if not matched[r]:
                target = r
                break
        if target == -1:
            best_rank = np.iinfo(np.int64).max
            for r in neighbors:
                if not matched[r] and rank[r] < best_rank:
                    best_rank = rank[r]
                    target = r
        if target != -1:
            matched[target] = True
            size += 1
    return size
