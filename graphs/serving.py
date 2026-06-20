"""Serving topology for the AI-inference-serving instantiation (Phase 4).

Online bipartite matching, instantiated as request routing in an inference
serving system:

  offline (R)  = serving resources — e.g. MoE experts, model replicas, or
                 KV-cache shards — each with a CAPACITY c (it can serve up to c
                 requests this window, hence b-matching rather than 1-matching).
  online (L)   = request *types* (prompt categories / token classes); the live
                 instance is a stream of requests drawn from a traffic
                 distribution p over types.
  edge (ℓ, r)  = resource r can serve request-type ℓ (capability / cache affinity).
  a match      = route a request to a capable, non-saturated resource.
  goodput      = fraction of requests served = our competitive ratio vs the
                 best possible (b-matching OPT).

Two things make this a faithful instantiation rather than a relabel:
  - the traffic distribution p is NON-uniform (Zipfian head/tail), so the
    Choo/BEM "predicted type histogram" is literally a traffic forecast, and a
    bad forecast is a STALE/ drifted one — the natural error mode in serving;
  - resources have capacity c (b-matching), the real serving element; capacity
    is itself a form of robustness, which lets us study capacity vs algorithmic
    robustness (see scripts/run_serving.py).
"""
from __future__ import annotations
import numpy as np


def serving_topology(
    n_resources: int,
    n_types: int,
    deg: int,
    rng: np.random.Generator,
    zipf_exponent: float = 1.0,
) -> tuple[list[list[int]], np.ndarray]:
    """Build a serving topology.

    Each of the n_types request types can be served by `deg` resources (a sparse
    capability set, like MoE top-k routing or cache affinity), chosen uniformly
    at random from the n_resources resources. Traffic popularity over types
    follows Zipf with the given exponent (a few request types dominate).

    Returns (type_adj, p) where:
      - type_adj[ℓ] = sorted list of resources that can serve request-type ℓ
      - p           = traffic distribution over types (sums to 1)
    Use with sample_instance(type_adj, m, rng, p=p) and capacity-c matching.
    """
    if deg > n_resources:
        raise ValueError(f"deg={deg} exceeds n_resources={n_resources}")
    type_adj = [
        sorted(rng.choice(n_resources, size=deg, replace=False).tolist())
        for _ in range(n_types)
    ]
    ranks = np.arange(1, n_types + 1, dtype=float)
    weights = ranks ** (-zipf_exponent)
    p = weights / weights.sum()
    return type_adj, p
