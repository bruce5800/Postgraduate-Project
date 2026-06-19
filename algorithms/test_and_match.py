"""FollowPrediction (blind Mimic) and TestAndMatch (Choo 2024 / BEM 2026).

- follow_prediction: the 'blindly trust the advice' extreme — Algorithm 2 (Mimic)
  run on every arrival, no test, no fallback. Great when advice is perfect, can
  fall below the no-advice baseline when advice is bad.
- test_and_match: the adaptive algorithm. Mimic a sublinear prefix, estimate the
  L1 distance between the predicted and observed type distributions on that
  prefix, and either keep mimicking (advice deemed good) or switch to a baseline
  (Ranking). Two variants:
    'choo' — early-exit if n̂/n ≤ β; threshold τ = 2(n̂/n − β).
    'bem'  — early-exit if n̂/n < α; threshold τ = 2(n̂/n)(1−β)/(1+β).

Practical note (Choo §5, BEM): the paper's L1 estimator (Jiao et al.) has no
off-the-shelf implementation; the authors themselves use an empirical-L1
proof-of-concept. We do the same — empirical L1 on the prefix — and document it.
"""
from __future__ import annotations
import math

import numpy as np


def _mimic_stepper(chat: np.ndarray, partners: list[list[int]], matched: np.ndarray):
    """Return a closure that mimics one arrival of type l, updating `matched`.
    Returns 1 if a match was made, else 0."""
    budget = chat.astype(np.int64).copy()
    ptr = np.zeros(len(chat), dtype=np.int64)

    def step(l: int) -> int:
        if budget[l] <= 0:
            return 0
        budget[l] -= 1
        p = partners[l]
        if ptr[l] < len(p):
            r = p[ptr[l]]
            ptr[l] += 1
            if not matched[r]:
                matched[r] = True
                return 1
        return 0

    return step


def follow_prediction(
    instance_adj: list[list[int]],
    types: np.ndarray,
    n_right: int,
    partners: list[list[int]],
    chat: np.ndarray,
) -> int:
    """Blind trust: Mimic on every arrival. Returns matching size."""
    matched = np.zeros(n_right, dtype=bool)
    step = _mimic_stepper(chat, partners, matched)
    size = 0
    for i in range(len(instance_adj)):
        size += step(int(types[i]))
    return size


def _baseline_ranking(n_right: int, rng: np.random.Generator):
    """Return (base_rank array, step closure) for Ranking on a shared `matched`."""
    perm = rng.permutation(n_right)
    base_rank = np.empty(n_right, dtype=np.int64)
    base_rank[perm] = np.arange(n_right)
    return base_rank


def test_and_match(
    instance_adj: list[list[int]],
    types: np.ndarray,
    n_right: int,
    partners: list[list[int]],
    chat: np.ndarray,
    n_hat: int,
    rng: np.random.Generator,
    beta: float = 0.696,
    variant: str = "bem",
    alpha: float = 0.05,
    eps: float | None = None,
    prefix_k: int | None = None,
) -> tuple[int, dict]:
    """TestAndMatch / Test-and-Match+. Returns (matching size, info dict).

    info: variant, n_hat_ratio, tau, eps, prefix_k, emp_l1, followed, early_exit.
    """
    n = len(instance_adj)
    n_types = len(chat)
    matched = np.zeros(n_right, dtype=bool)
    size = 0

    base_rank = _baseline_ranking(n_right, rng)

    def baseline_step(neighbors: list[int]) -> int:
        best, br = -1, np.iinfo(np.int64).max
        for r in neighbors:
            if not matched[r] and base_rank[r] < br:
                br = base_rank[r]
                best = r
        if best != -1:
            matched[best] = True
            return 1
        return 0

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

    info = {"variant": variant, "n_hat_ratio": n_hat / n, "tau": tau, "eps": eps}

    if early or tau <= 0:
        for nb in instance_adj:
            size += baseline_step(nb)
        info.update(followed=False, early_exit=True, prefix_k=0, emp_l1=None)
        return size, info

    if prefix_k is None:
        prefix_k = min(n, int(round(math.sqrt(n) * math.log2(n_types + 1) + 1)))

    step = _mimic_stepper(chat, partners, matched)
    prefix_counts = np.zeros(n_types, dtype=np.float64)
    for i in range(prefix_k):
        l = int(types[i])
        size += step(l)
        prefix_counts[l] += 1.0

    phat = prefix_counts / prefix_k
    q = chat / float(chat.sum())
    emp_l1 = float(np.abs(phat - q).sum())
    followed = emp_l1 <= (tau - eps)

    for i in range(prefix_k, n):
        if followed:
            size += step(int(types[i]))
        else:
            size += baseline_step(instance_adj[i])

    info.update(followed=followed, early_exit=False, prefix_k=prefix_k, emp_l1=emp_l1)
    return size, info
