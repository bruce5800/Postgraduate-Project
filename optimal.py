"""Offline maximum bipartite matching via Hopcroft-Karp (NetworkX)."""
from __future__ import annotations
import networkx as nx
import numpy as np


def max_matching_size(adj: list[list[int]], n_right: int) -> int:
    """Size of a maximum matching in a bipartite instance graph.

    adj[i] = list of right-node indices that left-node i is connected to.
    Right nodes are 0..n_right-1.
    """
    g = nx.Graph()
    left_offset = n_right
    n_left = len(adj)
    g.add_nodes_from(range(n_right), bipartite=0)
    g.add_nodes_from(range(left_offset, left_offset + n_left), bipartite=1)
    for i, neighbors in enumerate(adj):
        u = left_offset + i
        for r in neighbors:
            g.add_edge(u, r)
    if g.number_of_edges() == 0:
        return 0
    left_nodes = {left_offset + i for i in range(n_left)}
    matching = nx.bipartite.hopcroft_karp_matching(g, top_nodes=left_nodes)
    return len(matching) // 2


def max_b_matching_size(
    types: np.ndarray, type_adj: list[list[int]], n_right: int, capacity: int
) -> int:
    """Maximum b-matching: each resource r may serve up to `capacity` requests.

    The instance is given by `types` (the type label of each arriving request)
    and `type_adj` (which resources serve each type). Computed as a compressed
    max flow: s → type_ℓ (cap = z_ℓ requests of that type) → resource (cap z_ℓ)
    → t (cap `capacity`). The max flow equals the best possible number of served
    requests in hindsight = b-matching OPT.
    """
    n_types = len(type_adj)
    z = np.bincount(types, minlength=n_types)
    g = nx.DiGraph()
    served = 0
    for l in range(n_types):
        if z[l] == 0:
            continue
        g.add_edge("s", ("l", l), capacity=int(z[l]))
        for r in type_adj[l]:
            g.add_edge(("l", l), ("r", r), capacity=int(z[l]))
    for r in range(n_right):
        g.add_edge(("r", r), "t", capacity=capacity)
    if not g.has_node("s") or not g.has_node("t"):
        return 0
    flow_val, _ = nx.maximum_flow(g, "s", "t")
    return int(flow_val)
