"""Prefix-cache-aware routing on a real LLM trace (Mooncake, FAST'25).

Each request carries a list of KV-cache block hashes (`hash_ids`); requests that
share a leading run of blocks share a cached prefix (RadixAttention semantics).
Each replica holds a block cache with LRU eviction. Routing a request to a replica
yields a cache HIT for the longest leading run of its blocks already cached there
(no prefill recompute); the request's blocks are then inserted (LRU). The metric
is the cache hit fraction = cached prefix blocks / total prefix blocks.

Routers contrast REACTIVE vs STABLE placement — the key axis for caching, opposite
to load balancing (where reactive wins, see run_serving_dynamic.py):
  - cache_affinity : reactive — route to the replica with the longest current match
  - least_loaded   : reactive, cache-blind
  - consistent_hash: stable — hash the prefix signature to a fixed replica
  - forecast_home  : stable, prediction-based — a forecast of signature popularity
                     places signatures to balance predicted load
  - adaptive       : prefix-test the forecast, then follow the placement or fall
                     back to consistent_hash
"""
from __future__ import annotations
import math
from collections import OrderedDict

import numpy as np


def _leading_match(cache: OrderedDict, hids: list[int]) -> int:
    m = 0
    for h in hids:
        if h in cache:
            m += 1
        else:
            break
    return m


def _insert(cache: OrderedDict, hids: list[int], cap_blocks: int) -> None:
    for h in hids:
        if h in cache:
            cache.move_to_end(h)
        else:
            cache[h] = 1
            if len(cache) > cap_blocks:
                cache.popitem(last=False)


def signature(hids: list[int], k: int) -> tuple[int, ...]:
    """The prefix family key = first k blocks (block 0 is shared by all, so k≥2)."""
    return tuple(hids[:k])


def _shash(sig: tuple[int, ...]) -> int:
    """Deterministic hash of a signature (Python's hash() is salted per process)."""
    h = 1469598103934665603
    for x in sig:
        h = (h ^ (int(x) & 0xFFFFFFFF)) * 1099511628211 & 0xFFFFFFFFFFFFFFFF
    return h


def run_router(reqs, choose, n_rep: int, cap_blocks: int) -> float:
    """choose(hids, caches, load) -> replica index. Returns cache hit fraction."""
    caches = [OrderedDict() for _ in range(n_rep)]
    load = np.zeros(n_rep, dtype=np.int64)
    hit, tot = 0, 0
    for hids in reqs:
        r = choose(hids, caches, load)
        hit += _leading_match(caches[r], hids)
        tot += len(hids)
        _insert(caches[r], hids, cap_blocks)
        load[r] += 1
    return hit / max(1, tot)


# ----------------------------- reactive routers ---------------------------

def cache_affinity_chooser(n_rep):
    def choose(hids, caches, load):
        best, best_key = 0, None
        for i in range(n_rep):
            key = (_leading_match(caches[i], hids), -load[i])
            if best_key is None or key > best_key:
                best_key = key
                best = i
        return best
    return choose


def least_loaded_chooser(n_rep):
    def choose(hids, caches, load):
        return int(np.argmin(load))
    return choose


# ----------------------------- stable routers -----------------------------

def consistent_hash_chooser(n_rep, k):
    def choose(hids, caches, load):
        return _shash(signature(hids, k)) % n_rep
    return choose


def home_chooser(home_map, n_rep, k):
    """Route by a precomputed signature->replica home (fallback: hash)."""
    def choose(hids, caches, load):
        s = signature(hids, k)
        return home_map.get(s, _shash(s) % n_rep)
    return choose


def build_forecast_home(sig_counts: dict, n_rep: int) -> dict:
    """Place signatures on replicas to balance predicted load: greedy
    longest-processing-time (assign each signature, heaviest first, to the
    currently lightest replica)."""
    home: dict = {}
    rep_load = np.zeros(n_rep, dtype=np.float64)
    for s, c in sorted(sig_counts.items(), key=lambda kv: -kv[1]):
        r = int(np.argmin(rep_load))
        home[s] = r
        rep_load[r] += c
    return home


# ------------------------------- adaptive ---------------------------------

def run_adaptive(reqs, home_map, q_sig_dist, sig_index, n_rep, cap_blocks, k,
                 beta=0.696, prefix_k=None):
    """Mimic the forecast placement on a prefix, test the observed signature
    distribution against q, then keep following placement or fall back to
    consistent_hash. Returns (hit_fraction, followed)."""
    n = len(reqs)
    r_types = len(q_sig_dist)
    if prefix_k is None:
        prefix_k = int(round(math.sqrt(n) * math.log2(r_types + 1) + 1))
    prefix_k = min(prefix_k, n)
    tau = 2.0 * (1.0 - beta) / (1.0 + beta)
    eps = tau / 2.0

    home = home_chooser(home_map, n_rep, k)
    chash = consistent_hash_chooser(n_rep, k)
    caches = [OrderedDict() for _ in range(n_rep)]
    load = np.zeros(n_rep, dtype=np.int64)
    prefix_counts = np.zeros(r_types, dtype=np.float64)
    followed = None
    hit, tot = 0, 0
    for i, hids in enumerate(reqs):
        if i < prefix_k:
            s = signature(hids, k)
            if s in sig_index:
                prefix_counts[sig_index[s]] += 1.0
            r = home(hids, caches, load)
        else:
            if followed is None:
                phat = prefix_counts / max(1, prefix_k)
                emp_l1 = float(np.abs(phat - q_sig_dist).sum())
                followed = emp_l1 <= (tau - eps)
            r = home(hids, caches, load) if followed else chash(hids, caches, load)
        hit += _leading_match(caches[r], hids)
        tot += len(hids)
        _insert(caches[r], hids, cap_blocks)
        load[r] += 1
    return hit / max(1, tot), bool(followed)
