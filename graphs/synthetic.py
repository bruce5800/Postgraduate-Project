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


def clvb_zipf_bipartite(
    n: int,
    exponent: float,
    rng: np.random.Generator,
    C: float | None = None,
) -> list[list[int]]:
    """Symmetric Chung–Lu–Vu bipartite type graph with Zipf offline degrees.

    Offline (R) node r_i (i = 1..n) has expected degree d_i = C · i^(-exponent).
    Edge {ℓ, r_i} present independently with probability d_i / n.
    This makes the OFFLINE (R) degree distribution heavy-tailed (Zipf), which is
    where MinPredictedDegree shows its strongest signal (ACI §7).

    Defaults match Aamand–Chen–Indyk (2022) §7: C = n/2.

    Note the orientation: in our code L = online (arriving) types, R = offline
    (known) nodes. MPD predicts the R-side degrees, so the Zipf law is imposed on
    R (columns).
    """
    if C is None:
        C = n / 2.0
    i = np.arange(1, n + 1, dtype=float)
    d = C * i ** (-exponent)              # expected degree per offline node r_i
    p_edge = np.clip(d / n, 0.0, 1.0)     # edge prob for column r_i
    mask = rng.random((n, n)) < p_edge[None, :]  # rows = L types, cols = R offline
    return [np.flatnonzero(mask[l]).tolist() for l in range(n)]


def few_types_bipartite(
    n_offline: int, r: int, rng: np.random.Generator, overlap: float = 0.25
) -> list[list[int]]:
    """Type graph with only r distinct online types over n_offline offline nodes,
    structured so a near-perfect matching exists.

    Offline nodes are partitioned into r blocks of size ⌊n_offline/r⌋. Type t owns
    block t (guaranteeing it can absorb ~n_offline/r arrivals) plus an `overlap`
    fraction of extra random neighbors (for non-trivial structure). Used with
    `sample_instance(type_adj, m=n_offline)` so an instance draws ~n_offline/r
    arrivals per type — making the realized type counts c* LUMPY, the regime where
    the Choo/BEM prefix test is statistically effective (few high-count types can
    be estimated from a sublinear prefix; ~n distinct unit-count types could not —
    see docs/PHASE3_REPORT.md). Because each type owns a private block, the maximum
    matching size is ≈ n_offline, i.e. n̂/n ≈ 1 — the regime the Choo/BEM
    thresholds are calibrated for.

    Returns type_adj with r rows; n_right = n_offline.
    """
    block = n_offline // r
    n_extra = int(round(overlap * block))
    type_adj: list[list[int]] = []
    for t in range(r):
        own = list(range(t * block, (t + 1) * block))
        extra = rng.choice(n_offline, size=n_extra, replace=False).tolist()
        type_adj.append(sorted(set(own) | set(extra)))
    return type_adj
