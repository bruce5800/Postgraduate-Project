"""FeldmanEtAl (Feldman et al., FOCS 2009) for online bipartite matching under known i.i.d.

Pipeline:
  1. Build the flow network G̃: s --2--> R --1--> L --2--> t.
     (Edges from R to L are the type graph edges, oriented R→L.)
  2. Solve max integral flow f.
  3. Let G' = subgraph induced by edges {r, ℓ} with f(r→ℓ) = 1.
     G' has max degree 2 (each r ≤ 2 outgoing, each ℓ ≤ 2 incoming).
  4. Apply blue-red decomposition (Algorithm 3) to G' → (M_b, M_r).
  5. Online stage: at the k-th arrival of type ℓ,
       k=1 → try M_b[ℓ];  k=2 → try M_r[ℓ];  k≥3 → unmatched (non-greedy).
     The greedy version falls back to any unmatched neighbor.
"""
from __future__ import annotations
import networkx as nx
import numpy as np


# ----------------------------- preprocessing ------------------------------

def _build_flow_network(type_adj: list[list[int]], n_right: int) -> nx.DiGraph:
    """s → r (cap 2), r → ℓ (cap 1) for each edge, ℓ → t (cap 2)."""
    g = nx.DiGraph()
    n_left = len(type_adj)
    for r in range(n_right):
        g.add_edge("s", ("r", r), capacity=2)
    for l in range(n_left):
        g.add_edge(("l", l), "t", capacity=2)
    for l, neighbors in enumerate(type_adj):
        for r in neighbors:
            g.add_edge(("r", r), ("l", l), capacity=1)
    return g


def _max_flow_unit_edges(type_adj: list[list[int]], n_right: int) -> list[tuple[int, int]]:
    """Return list of (r, ℓ) such that f(r → ℓ) = 1 in the max flow."""
    g = _build_flow_network(type_adj, n_right)
    _, flow = nx.maximum_flow(g, "s", "t")
    edges: list[tuple[int, int]] = []
    for l, neighbors in enumerate(type_adj):
        for r in neighbors:
            if flow.get(("r", r), {}).get(("l", l), 0) == 1:
                edges.append((r, l))
    return edges


# ------------------------ blue-red decomposition --------------------------

def _trace_component(
    adj: dict[tuple[str, int], list[tuple[str, int]]],
    start: tuple[str, int],
    is_cycle: bool,
) -> list[tuple[str, int]]:
    """Trace a path or cycle starting at `start`. Returns the node sequence.
    For a cycle, the last element equals the first (closed loop).
    """
    path = [start]
    visited = {start}
    cur = start
    prev: tuple[str, int] | None = None
    while True:
        next_node = None
        for nbr in adj[cur]:
            if nbr == prev:
                continue
            if nbr in visited:
                if is_cycle and nbr == start and len(path) >= 3:
                    path.append(start)
                    return path
                continue
            next_node = nbr
            break
        if next_node is None:
            return path
        path.append(next_node)
        visited.add(next_node)
        prev = cur
        cur = next_node


def _color_edges(path: list[tuple[str, int]], is_cycle: bool) -> list[str]:
    """Apply the Feldman et al. coloring rules.

    Path is a list of nodes; edges are pairs (path[i], path[i+1]).
    Returns a list of "blue"/"red" of length (len(path) - 1).
    """
    n_edges = len(path) - 1
    if is_cycle:
        # Even-length cycle (bipartite). Alternate.
        return ["blue" if i % 2 == 0 else "red" for i in range(n_edges)]
    if n_edges % 2 == 1:
        # Odd-length path: blue, red, blue, ... (more blue than red).
        return ["blue" if i % 2 == 0 else "red" for i in range(n_edges)]
    # Even-length path.
    start_side, end_side = path[0][0], path[-1][0]
    if start_side == "R" and end_side == "R":
        # R-R even: alternate, starting blue.
        return ["blue" if i % 2 == 0 else "red" for i in range(n_edges)]
    if start_side == "L" and end_side == "L":
        # L-L even: first two blue, then red, blue, red, blue, ...
        colors = ["blue", "blue"]
        # From index 2 onward: red at even index, blue at odd index.
        for i in range(2, n_edges):
            colors.append("red" if i % 2 == 0 else "blue")
        return colors
    raise ValueError(f"Bipartite path with mixed-side endpoints: {start_side}..{end_side}")


def blue_red_decomposition(
    edges: list[tuple[int, int]], n_left: int
) -> tuple[np.ndarray, np.ndarray]:
    """Decompose the max-flow unit-edge subgraph into a blue semi-matching
    (matched on L) and a red matching.

    Returns (Mb, Mr) with shape (n_left,). Entry = -1 means absent.
    """
    # Build undirected adjacency, distinguishing R and L by a tag.
    adj: dict[tuple[str, int], list[tuple[str, int]]] = {}
    for r, l in edges:
        ru, lv = ("R", r), ("L", l)
        adj.setdefault(ru, []).append(lv)
        adj.setdefault(lv, []).append(ru)

    Mb = -np.ones(n_left, dtype=np.int64)
    Mr = -np.ones(n_left, dtype=np.int64)

    visited: set[tuple[str, int]] = set()
    for node in list(adj.keys()):
        if node in visited:
            continue
        # Find an endpoint (degree 1) in this component; else it is a cycle.
        component_nodes: list[tuple[str, int]] = []
        stack = [node]
        seen_local: set[tuple[str, int]] = set()
        while stack:
            u = stack.pop()
            if u in seen_local:
                continue
            seen_local.add(u)
            component_nodes.append(u)
            for v in adj[u]:
                if v not in seen_local:
                    stack.append(v)

        endpoints = [u for u in component_nodes if len(adj[u]) == 1]
        is_cycle = len(endpoints) == 0
        start = endpoints[0] if not is_cycle else component_nodes[0]
        path = _trace_component(adj, start, is_cycle)
        visited.update(component_nodes)

        colors = _color_edges(path, is_cycle)
        for i, c in enumerate(colors):
            u, v = path[i], path[i + 1]
            if u[0] == "L":
                l_idx, r_idx = u[1], v[1]
            else:
                r_idx, l_idx = u[1], v[1]
            if c == "blue":
                Mb[l_idx] = r_idx
            else:
                Mr[l_idx] = r_idx

    return Mb, Mr


def feldman_preprocess(
    type_adj: list[list[int]], n_right: int
) -> tuple[np.ndarray, np.ndarray]:
    """Returns (Mb, Mr) advice arrays of length |L|."""
    n_left = len(type_adj)
    edges = _max_flow_unit_edges(type_adj, n_right)
    return blue_red_decomposition(edges, n_left)


# ------------------------------ online stage ------------------------------

def feldman_online(
    instance_adj: list[list[int]],
    types: np.ndarray,
    n_right: int,
    Mb: np.ndarray,
    Mr: np.ndarray,
) -> int:
    """Non-greedy: only follow Mb on 1st arrival, Mr on 2nd; otherwise skip."""
    matched = np.zeros(n_right, dtype=bool)
    arrivals = np.zeros(len(Mb), dtype=np.int64)
    size = 0
    for i in range(len(instance_adj)):
        l = int(types[i])
        z = arrivals[l]
        arrivals[l] += 1
        target = -1
        if z == 0 and Mb[l] != -1:
            target = int(Mb[l])
        elif z == 1 and Mr[l] != -1:
            target = int(Mr[l])
        if target != -1 and not matched[target]:
            matched[target] = True
            size += 1
    return size


def feldman_online_greedy(
    instance_adj: list[list[int]],
    types: np.ndarray,
    n_right: int,
    Mb: np.ndarray,
    Mr: np.ndarray,
) -> int:
    """Greedy: if advice slot is unavailable, fall back to any unmatched neighbor."""
    matched = np.zeros(n_right, dtype=bool)
    arrivals = np.zeros(len(Mb), dtype=np.int64)
    size = 0
    for i, neighbors in enumerate(instance_adj):
        l = int(types[i])
        z = arrivals[l]
        arrivals[l] += 1
        target = -1
        if z == 0 and Mb[l] != -1 and not matched[Mb[l]]:
            target = int(Mb[l])
        elif z == 1 and Mr[l] != -1 and not matched[Mr[l]]:
            target = int(Mr[l])
        if target == -1:
            for r in neighbors:
                if not matched[r]:
                    target = r
                    break
        if target != -1:
            matched[target] = True
            size += 1
    return size
