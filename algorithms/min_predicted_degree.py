"""MinPredictedDegree (Aamand–Chen–Indyk, NeurIPS 2022).

MPD matches each arriving online (L) node to its unmatched offline (R) neighbor
of minimum predicted degree μ. We implement it as the Phase 2 primitive
`greedy_with_permutation` with a rank derived from μ:

    rank = lexsort by (μ, random tiebreak)

so that:
  - μ constant         → pure random order  ≡ Ranking         (robustness floor)
  - μ = true degree    → MinDegree                            (consistency ceiling)
  - μ = type-graph deg → MPD                                  (the natural predictor)

Random tie-breaking among equal predicted degrees is what makes
MPD(constant μ) ≡ Ranking exactly (rather than ≡ SimpleGreedy). This matches
ACI's statement that a random predictor reduces MPD to Ranking.
"""
from __future__ import annotations
import numpy as np

from algorithms._common import greedy_with_permutation


def mpd_rank(mu: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Rank offline nodes by ascending μ, breaking ties uniformly at random.

    Returns rank[r] = position of r (0 = matched first / lowest predicted degree).
    """
    n = mu.shape[0]
    tiebreak = rng.permutation(n)
    # lexsort: last key is primary → sort by μ first, then random tiebreak.
    order = np.lexsort((tiebreak, mu))
    rank = np.empty(n, dtype=np.int64)
    rank[order] = np.arange(n)
    return rank


def mpd(
    instance_adj: list[list[int]],
    n_right: int,
    mu: np.ndarray,
    rng: np.random.Generator,
) -> int:
    """Run MinPredictedDegree with predictor μ. Returns matching size.

    MinDegree = mpd(..., mu=instance_degree(...)).
    MPD       = mpd(..., mu=type_graph_degree(...)).
    """
    rank = mpd_rank(mu, rng)
    return greedy_with_permutation(instance_adj, rank)
