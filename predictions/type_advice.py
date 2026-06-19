"""Type-histogram advice (prediction object B) for Choo/BEM (Phase 3c).

A 'type' of an online vertex = its neighborhood = a row `type_adj[l]`. The advice
is a count vector ĉ over types (how many vertices of each type are predicted to
arrive), summing to the number of arrivals. From ĉ we build an 'advice graph' Ĝ
(ĉ[l] copies of type l), compute a maximum matching M̂ on it, and record, per
type, the offline partners M̂ used — which the online algorithm then mimics.

See docs/PHASE3_SPEC.md §3.2/§3.3 and the Choo/BEM Algorithm boxes.
"""
from __future__ import annotations
import networkx as nx
import numpy as np


def true_type_counts(types: np.ndarray, n_types: int) -> np.ndarray:
    """Realized counts c*(l) = number of arrivals of type l in the instance."""
    return np.bincount(types, minlength=n_types).astype(np.float64)


def build_advice_matching(
    type_adj: list[list[int]], chat: np.ndarray, n_right: int
) -> tuple[int, list[list[int]]]:
    """Compute a maximum matching M̂ on the advice graph Ĝ (ĉ[l] copies of type l).

    Returns (n_hat, partners) where partners[l] is the list of offline nodes that
    M̂ matched to type-l advice vertices. Because M̂ is a matching, every offline
    node appears in at most one partners[l], so mimicking it never conflicts.
    """
    n_types = len(type_adj)
    adv_types: list[int] = []
    for l in range(n_types):
        adv_types.extend([l] * int(round(float(chat[l]))))
    n_adv = len(adv_types)
    partners: list[list[int]] = [[] for _ in range(n_types)]
    if n_adv == 0:
        return 0, partners

    g = nx.Graph()
    off = n_right
    g.add_nodes_from(range(n_right), bipartite=0)
    g.add_nodes_from(range(off, off + n_adv), bipartite=1)
    for i, l in enumerate(adv_types):
        u = off + i
        for r in type_adj[l]:
            g.add_edge(u, r)
    if g.number_of_edges() == 0:
        return 0, partners

    left_nodes = {off + i for i in range(n_adv)}
    matching = nx.bipartite.hopcroft_karp_matching(g, top_nodes=left_nodes)
    n_hat = 0
    for i, l in enumerate(adv_types):
        u = off + i
        if u in matching:
            partners[l].append(int(matching[u]))
            n_hat += 1
    return n_hat, partners


def perturb_counts(
    c_star: np.ndarray, eta: float, rng: np.random.Generator,
    concentration: float = 0.3,
) -> tuple[np.ndarray, float]:
    """Blend the true type distribution toward a SPIKY random target.

    ĉ ≈ n · [(1−η)·p* + η·q_target], where q_target ~ Dirichlet(concentration)
    is a concentrated (non-uniform) distribution. Using a spiky target (rather
    than a uniform-random one) is what lets L1(p,q) actually span the full range:
    when the true type distribution is near-uniform, a uniform perturbation stays
    near-uniform and barely moves L1.

    η = 0 → perfect advice (ĉ = c*, L1 = 0). η = 1 → counts follow the spiky
    target. Returns (chat as integer counts summing to n, normalized L1 = L1(p,q)).
    """
    n = int(round(float(c_star.sum())))
    n_types = len(c_star)
    p_star = c_star / n
    q_target = rng.dirichlet(np.full(n_types, concentration))
    blended_p = (1.0 - eta) * p_star + eta * q_target
    chat = np.round(n * blended_p).astype(np.int64)

    # Repair rounding so the counts sum exactly to n.
    diff = n - int(chat.sum())
    if diff != 0:
        idx = rng.choice(n_types, size=abs(diff), replace=True)
        for j in idx:
            chat[j] += 1 if diff > 0 else -1
        chat = np.clip(chat, 0, None)
        # final tiny correction
        d2 = n - int(chat.sum())
        if d2 != 0:
            chat[int(np.argmax(chat))] += d2

    l1 = float(np.abs(chat.astype(np.float64) - c_star).sum() / n)
    return chat.astype(np.float64), l1
