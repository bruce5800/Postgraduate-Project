"""Capacity-c (b-matching) versions of the online algorithms — serving setting.

Each resource r may serve up to `capacity` requests. The only change from the
1-matching code is that a boolean `matched[r]` becomes a counter `load[r]`, and a
resource is available iff `load[r] < capacity`. This generalizes the whole family:
SimpleGreedy / Ranking / MinPredictedDegree are `greedy_with_capacity` with an
identity / random / degree-derived rank; FollowPrediction / TestAndMatch mimic a
b-matching advice and fall back to capacity-aware Ranking.
"""
from __future__ import annotations
import math

import networkx as nx
import numpy as np


# ---------------------- greedy family (rank-driven) -----------------------

def greedy_with_capacity(
    instance_adj: list[list[int]],
    rank: np.ndarray,
    n_right: int,
    capacity: int,
) -> int:
    """Route each request to its lowest-rank capable resource with free capacity."""
    load = np.zeros(n_right, dtype=np.int64)
    size = 0
    for neighbors in instance_adj:
        best, best_rank = -1, np.iinfo(np.int64).max
        for r in neighbors:
            if load[r] < capacity and rank[r] < best_rank:
                best_rank = rank[r]
                best = r
        if best != -1:
            load[best] += 1
            size += 1
    return size


# --------------------- b-matching advice (for Mimic) ----------------------

def build_advice_b_matching(
    type_adj: list[list[int]], chat: np.ndarray, n_right: int, capacity: int
) -> tuple[int, list[list[int]]]:
    """Max b-matching on the advice graph (ĉ[l] copies of type l, resources cap c).

    Returns (n_hat, partners): partners[l] is the list of resources the advice
    b-matching routed type-l requests to (resource r repeated f(ℓ→r) times). Since
    the b-matching respects capacity, every resource appears ≤ c times across all
    partners, so mimicking it never overflows.
    """
    n_types = len(type_adj)
    partners: list[list[int]] = [[] for _ in range(n_types)]
    g = nx.DiGraph()
    any_edge = False
    for l in range(n_types):
        c = int(round(float(chat[l])))
        if c <= 0:
            continue
        g.add_edge("s", ("l", l), capacity=c)
        for r in type_adj[l]:
            g.add_edge(("l", l), ("r", r), capacity=c)
            any_edge = True
    if not any_edge:
        return 0, partners
    for r in range(n_right):
        g.add_edge(("r", r), "t", capacity=capacity)
    n_hat, flow = nx.maximum_flow(g, "s", "t")
    for l in range(n_types):
        fl = flow.get(("l", l), {})
        for r, f in fl.items():
            if f > 0:
                partners[l].extend([r[1]] * int(f))
    return int(n_hat), partners


# ----------------- follow-prediction & test-and-match ---------------------

def follow_prediction_capacity(
    instance_adj: list[list[int]],
    types: np.ndarray,
    n_right: int,
    partners: list[list[int]],
    chat: np.ndarray,
    capacity: int,
) -> int:
    """Blind trust: mimic the advice b-matching for every request."""
    load = np.zeros(n_right, dtype=np.int64)
    budget = chat.astype(np.int64).copy()
    ptr = np.zeros(len(chat), dtype=np.int64)
    size = 0
    for i in range(len(instance_adj)):
        l = int(types[i])
        if budget[l] <= 0:
            continue
        budget[l] -= 1
        p = partners[l]
        if ptr[l] < len(p):
            r = p[ptr[l]]
            ptr[l] += 1
            if load[r] < capacity:
                load[r] += 1
                size += 1
    return size


def test_and_match_capacity(
    instance_adj: list[list[int]],
    types: np.ndarray,
    n_right: int,
    partners: list[list[int]],
    chat: np.ndarray,
    n_hat: int,
    capacity: int,
    rng: np.random.Generator,
    beta: float = 0.696,
    variant: str = "bem",
    alpha: float = 0.05,
    eps: float | None = None,
    prefix_k: int | None = None,
) -> tuple[int, dict]:
    """Capacity-aware TestAndMatch: mimic a prefix, test the forecast, then keep
    mimicking or fall back to capacity-aware Ranking. Same thresholds as the
    1-matching version (algorithms/test_and_match.py)."""
    n = len(instance_adj)
    n_types = len(chat)
    load = np.zeros(n_right, dtype=np.int64)
    size = 0

    perm = rng.permutation(n_right)
    base_rank = np.empty(n_right, dtype=np.int64)
    base_rank[perm] = np.arange(n_right)

    def baseline_step(neighbors):
        nonlocal size
        best, br = -1, np.iinfo(np.int64).max
        for r in neighbors:
            if load[r] < capacity and base_rank[r] < br:
                br = base_rank[r]
                best = r
        if best != -1:
            load[best] += 1
            size += 1

    if variant == "choo":
        early = (n_hat / n) <= beta
        tau = 2.0 * (n_hat / n - beta)
    elif variant == "bem":
        early = (n_hat / n) < alpha
        tau = 2.0 * (n_hat / n) * (1.0 - beta) / (1.0 + beta)
    else:
        raise ValueError(variant)
    if eps is None:
        eps = tau / 2.0
    info = {"variant": variant, "n_hat_ratio": n_hat / n, "tau": tau}

    if early or tau <= 0:
        for nb in instance_adj:
            baseline_step(nb)
        info.update(followed=False, early_exit=True, prefix_k=0, emp_l1=None)
        return size, info

    if prefix_k is None:
        prefix_k = int(round(math.sqrt(n) * math.log2(n_types + 1) + 1))
    prefix_k = min(prefix_k, n)

    budget = chat.astype(np.int64).copy()
    ptr = np.zeros(n_types, dtype=np.int64)

    def mimic_step(l):
        nonlocal size
        if budget[l] <= 0:
            return
        budget[l] -= 1
        p = partners[l]
        if ptr[l] < len(p):
            r = p[ptr[l]]
            ptr[l] += 1
            if load[r] < capacity:
                load[r] += 1
                size += 1

    prefix_counts = np.zeros(n_types, dtype=np.float64)
    for i in range(prefix_k):
        l = int(types[i])
        mimic_step(l)
        prefix_counts[l] += 1.0

    phat = prefix_counts / prefix_k
    q = chat / float(chat.sum())
    emp_l1 = float(np.abs(phat - q).sum())
    followed = emp_l1 <= (tau - eps)

    for i in range(prefix_k, n):
        if followed:
            mimic_step(int(types[i]))
        else:
            baseline_step(instance_adj[i])

    info.update(followed=followed, early_exit=False, prefix_k=prefix_k, emp_l1=emp_l1)
    return size, info
