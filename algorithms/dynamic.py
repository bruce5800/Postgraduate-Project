"""Dynamic (windowed) serving simulation — requests occupy a slot for a duration.

This deepens the static b-matching: instead of assuming all requests are
concurrent forever, each request holds a resource slot for a real service
duration (from the trace's generated-token count) and frees it when it finishes.
An event-driven loop processes arrivals in time order, releasing finished
requests before each arrival. A resource has `capacity` concurrent slots.

Metric: goodput = served / total arrivals (the admission/serve rate) — the
standard serving metric, which sidesteps the hard dynamic offline optimum.

Policies contrast resource *scope*:
  - least_loaded   : forecast-free; among ALL capable resources with a free slot,
                     pick the least loaded (a real load balancer).
  - blind_forecast : route only to the forecast-PREFERRED resources for the type;
                     if all are busy, drop. Rigid — fragile to a bad forecast.
  - adaptive       : run blind on a prefix, test the forecast against the observed
                     type stream, then keep following it or switch to least_loaded.
"""
from __future__ import annotations
import heapq
import math

import numpy as np


def simulate(arr_t, arr_type, arr_dur, type_adj, n_right, capacity, choose) -> int:
    """Event-driven serving. `choose(l, load)` returns a resource or None.
    Returns the number of served requests."""
    load = np.zeros(n_right, dtype=np.int64)
    heap: list[tuple[float, int]] = []
    served = 0
    for t, l, dur in zip(arr_t, arr_type, arr_dur):
        while heap and heap[0][0] <= t:
            _, r = heapq.heappop(heap)
            load[r] -= 1
        r = choose(int(l), load)
        if r is not None and load[r] < capacity:
            load[r] += 1
            heapq.heappush(heap, (t + dur, r))
            served += 1
    return served


def _least_loaded_chooser(type_adj, capacity, base_rank):
    def choose(l, load):
        best, best_key = None, None
        for r in type_adj[l]:
            if load[r] < capacity:
                key = (load[r], base_rank[r])
                if best_key is None or key < best_key:
                    best_key = key
                    best = r
        return best
    return choose


def _forecast_chooser(preferred, capacity, base_rank):
    """Route only to the type's forecast-preferred resources (a subset)."""
    def choose(l, load):
        best, best_key = None, None
        for r in preferred[l]:
            if load[r] < capacity:
                key = (load[r], base_rank[r])
                if best_key is None or key < best_key:
                    best_key = key
                    best = r
        return best
    return choose


def served_least_loaded(arr_t, arr_type, arr_dur, type_adj, n_right, capacity, rng):
    base_rank = rng.permutation(n_right)
    return simulate(arr_t, arr_type, arr_dur, type_adj, n_right, capacity,
                    _least_loaded_chooser(type_adj, capacity, base_rank))


def served_blind_forecast(arr_t, arr_type, arr_dur, type_adj, preferred, n_right, capacity, rng):
    base_rank = rng.permutation(n_right)
    return simulate(arr_t, arr_type, arr_dur, type_adj, n_right, capacity,
                    _forecast_chooser(preferred, capacity, base_rank))


def served_adaptive(arr_t, arr_type, arr_dur, type_adj, preferred, q, n_right,
                    capacity, rng, beta=0.696, alpha=0.05, prefix_k=None):
    """Prefix-test the forecast distribution q against the observed prefix, then
    follow the forecast (blind) or switch to least_loaded. BEM threshold."""
    n = len(arr_t)
    n_types = len(type_adj)
    base_rank = rng.permutation(n_right)
    forecast_choose = _forecast_chooser(preferred, capacity, base_rank)
    ll_choose = _least_loaded_chooser(type_adj, capacity, base_rank)

    if prefix_k is None:
        prefix_k = int(round(math.sqrt(n) * math.log2(n_types + 1) + 1))
    prefix_k = min(prefix_k, n)
    # BEM-style threshold with n̂/n ≈ 1 in this serving regime (a near-perfect
    # forecast can route nearly all requests).
    tau = 2.0 * (1.0 - beta) / (1.0 + beta)
    eps = tau / 2.0

    load = np.zeros(n_right, dtype=np.int64)
    heap: list[tuple[float, int]] = []
    served = 0
    prefix_counts = np.zeros(n_types, dtype=np.float64)
    followed = None
    for i, (t, l, dur) in enumerate(zip(arr_t, arr_type, arr_dur)):
        l = int(l)
        while heap and heap[0][0] <= t:
            _, r = heapq.heappop(heap)
            load[r] -= 1
        if i < prefix_k:
            prefix_counts[l] += 1.0
            r = forecast_choose(l, load)
        else:
            if followed is None:
                phat = prefix_counts / max(1, prefix_k)
                emp_l1 = float(np.abs(phat - q).sum())
                followed = emp_l1 <= (tau - eps)
            r = forecast_choose(l, load) if followed else ll_choose(l, load)
        if r is not None and load[r] < capacity:
            load[r] += 1
            heapq.heappush(heap, (t + dur, r))
            served += 1
    return served, bool(followed)
