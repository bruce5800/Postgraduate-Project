"""Ground-truth degree predictors for MinPredictedDegree.

Orientation reminder (see docs/PHASE3_SPEC.md §1):
  L = online (arriving) types  ↔  Phase 3 papers' V
  R = offline (known) nodes    ↔  Phase 3 papers' U
MPD predicts the degrees of OFFLINE (R) nodes.
"""
from __future__ import annotations
import numpy as np


def type_graph_degree(type_adj: list[list[int]], n_right: int) -> np.ndarray:
    """Expected-degree predictor (the 'MPD' predictor, ACI §7).

    μ*(r) = number of types ℓ adjacent to offline node r in the type graph.
    For uniform i.i.d. with m = |L|, this equals the expected realized degree.
    """
    mu = np.zeros(n_right, dtype=np.float64)
    for neighbors in type_adj:
        for r in neighbors:
            mu[r] += 1.0
    return mu


def instance_degree(instance_adj: list[list[int]], n_right: int) -> np.ndarray:
    """Perfect-oracle predictor (the 'MinDegree' predictor, ACI §7).

    Returns the TRUE realized degree of each offline node r in the instance graph
    = number of arrived online nodes adjacent to r. This is the consistency
    ceiling: MPD given this predictor is MinDegree.
    """
    deg = np.zeros(n_right, dtype=np.float64)
    for neighbors in instance_adj:
        for r in neighbors:
            deg[r] += 1.0
    return deg
