"""Offline maximum bipartite matching via Hopcroft-Karp (NetworkX)."""
from __future__ import annotations
import networkx as nx


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
