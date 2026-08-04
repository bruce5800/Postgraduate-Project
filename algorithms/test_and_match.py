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
        prefix_k = int(round(math.sqrt(n) * math.log2(n_types + 1) + 1))
    prefix_k = min(prefix_k, n)

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


def directional_test_and_match(
    type_adj: list[list[int]],
    instance_adj: list[list[int]],
    types: np.ndarray,
    n_right: int,
    partners: list[list[int]],
    chat: np.ndarray,
    rng: np.random.Generator,
    prefix_k: int | None = None,
    n_sims: int = 4,
    n_null: int = 16,
    margin: float = 0.0,
) -> tuple[int, dict]:
    """Test-and-fallback that tests the PAYOFF, not the prediction.

    Same commit-once flow as `test_and_match` (Mimic during the prefix, then a
    single follow/fallback decision), but the decision compares plug-in payoff
    estimates and needs NO problem constants (no worst-case beta, no tau):

        d = [V_corr(p-hat) - V_rank(p-hat)]/n,   follow iff >= margin,

    where V_mimic(p) = sum_l min(n*p_l, slots_l) is the exact closed form of the
    mimic stepper's value under counts n*p (partners are disjoint), V_rank(p-hat)
    is Ranking simulated on a stream with the observed counts over the public
    type graph, and V_corr is the BOOTSTRAP-BIAS-CORRECTED plug-in: V_mimic is
    concave, so honest k-sample noise drags the plug-in down at the capacity
    kinks (Jensen) and a naive "follow iff plug-in payoff > 0" rejects even
    perfect advice. The standard bootstrap correction anchored at p-hat itself
    (V_corr = 2*V(p-hat) - mean_j V(p~_j), p~_j prefix-sized empirical redraws
    from p-hat) measures the kink geometry AT the observed distribution — an
    advice-anchored null would over-correct exactly for mildly-bad advice,
    where the true distribution sits in the locally linear region.

    Public-information early exit (parity with Choo's n-hat/n <= beta test):
    before spending the prefix, simulate Ranking on the advice-count stream; if
    even a CORRECT advice would not beat the baseline ((n_hat - V_rank(q))/n
    <= 0), fall back immediately without mimicking the prefix.

    Uses only the prefix, the public type graph, and the advice — no realized
    future information. Simulation error is compute, not samples (n_sims/n_null
    can be raised freely); the information-theoretic error lives in p-hat.
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

    if prefix_k is None:
        prefix_k = int(round(math.sqrt(n) * math.log2(n_types + 1) + 1))
    prefix_k = min(prefix_k, n)

    slots = np.array([len(p) for p in partners], dtype=np.float64)
    n_hat = float(slots.sum())

    from algorithms.ranking import ranking as _ranking

    def rank_on_counts(counts: np.ndarray) -> float:
        stream = np.repeat(np.arange(n_types), counts.astype(np.int64))
        v = 0.0
        for _ in range(n_sims):
            s_ = stream.copy()
            rng.shuffle(s_)
            v += float(_ranking([type_adj[l] for l in s_], n_right, rng))
        return v / n_sims

    # Public-information early exit: if even a CORRECT advice would not beat
    # the baseline, don't spend the prefix mimicking it.
    chat_counts = np.clip(np.round(chat), 0, None)
    adv_payoff = (n_hat - rank_on_counts(chat_counts)) / n
    if adv_payoff <= 0.0:
        for nb in instance_adj:
            size += baseline_step(nb)
        info = {"variant": "directional", "prefix_k": 0, "n_sims": n_sims,
                "n_null": n_null, "d_hat": adv_payoff, "adv_payoff": adv_payoff,
                "followed": False, "early_exit": True, "emp_l1": None}
        return size, info

    step = _mimic_stepper(chat, partners, matched)
    prefix_counts = np.zeros(n_types, dtype=np.float64)
    for i in range(prefix_k):
        l = int(types[i])
        size += step(l)
        prefix_counts[l] += 1.0
    phat = prefix_counts / prefix_k

    # Plug-in Mimic payoff under the observed prefix distribution (closed form),
    # bootstrap-bias-corrected at p-hat (concavity/Jensen at the capacity kinks).
    v_obs = float(np.minimum(n * phat, slots).sum())
    boot = np.empty(n_null)
    for j in range(n_null):
        pt = rng.multinomial(prefix_k, phat) / prefix_k
        boot[j] = float(np.minimum(n * pt, slots).sum())
    v_corr = 2.0 * v_obs - float(boot.mean())

    # Ranking under the observed distribution (fluid counts, largest remainder).
    counts_obs = np.floor(n * phat).astype(np.int64)
    rem = n - int(counts_obs.sum())
    if rem > 0:
        frac = n * phat - np.floor(n * phat)
        counts_obs[np.argsort(-frac)[:rem]] += 1
    v_rank_obs = rank_on_counts(counts_obs)

    d_hat = (v_corr - v_rank_obs) / n
    followed = d_hat >= margin

    for i in range(prefix_k, n):
        if followed:
            size += step(int(types[i]))
        else:
            size += baseline_step(instance_adj[i])

    info = {"variant": "directional", "prefix_k": prefix_k, "n_sims": n_sims,
            "n_null": n_null, "d_hat": d_hat, "adv_payoff": adv_payoff,
            "v_obs": v_obs / n, "v_corr": v_corr / n,
            "v_rank_obs": v_rank_obs / n,
            "followed": followed, "early_exit": False, "emp_l1": None}
    return size, info
