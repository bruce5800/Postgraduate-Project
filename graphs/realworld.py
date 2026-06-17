"""Load real-world graphs and convert them to bipartite type graphs.

Supports the Network Repository formats we use:
  - MatrixMarket .mtx  (pattern/real, symmetric/general; 1-indexed)
  - whitespace .edges  (optionally weighted; any indexing)

All graphs are reduced to a SIMPLE UNDIRECTED graph: weights dropped, direction
dropped (symmetrized), self-loops removed, parallel edges deduped, vertex ids
remapped to a dense range 0..n-1.

Two bipartite conversions follow Borodin et al. (2018) §3.3:
  - duplicating (bipartite double cover): U,V are copies of the vertex set;
    {u_i, v_j} ∈ E' iff {v_i, v_j} ∈ E.  |L| = |R| = n.
  - random balanced partition: split V into two blocks, keep only cross edges.

Orientation (docs/PHASE3_SPEC.md §1): we return `type_adj` where index = online
(L) type and entries = offline (R) neighbor indices, plus n_right.
"""
from __future__ import annotations
from pathlib import Path

import numpy as np


def load_simple_graph(path: str | Path) -> tuple[int, list[tuple[int, int]]]:
    """Parse a .mtx or .edges file into (n_vertices, edges).

    edges are (i, j) with i < j, deduped, self-loops removed, ids dense 0..n-1.
    """
    path = Path(path)
    is_mtx = path.suffix == ".mtx"
    raw: list[tuple[int, int]] = []
    seen_dim_line = False
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("%"):
                continue
            if is_mtx and not seen_dim_line:
                # First non-comment line of an .mtx is "rows cols nnz" — skip it.
                seen_dim_line = True
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            i, j = int(float(parts[0])), int(float(parts[1]))
            raw.append((i, j))

    # Remap ids to dense 0..n-1.
    ids = sorted({v for e in raw for v in e})
    remap = {v: k for k, v in enumerate(ids)}
    edge_set: set[tuple[int, int]] = set()
    for i, j in raw:
        a, b = remap[i], remap[j]
        if a == b:
            continue  # drop self-loop
        edge_set.add((a, b) if a < b else (b, a))
    return len(ids), sorted(edge_set)


def _adjacency(n: int, edges: list[tuple[int, int]]) -> list[list[int]]:
    adj: list[list[int]] = [[] for _ in range(n)]
    for i, j in edges:
        adj[i].append(j)
        adj[j].append(i)
    return adj


def to_bipartite_duplicating(
    n: int, edges: list[tuple[int, int]]
) -> tuple[list[list[int]], int]:
    """Bipartite double cover. type_adj[l] = neighbors of l in G. |L| = |R| = n."""
    adj = _adjacency(n, edges)
    type_adj = [sorted(neigh) for neigh in adj]
    return type_adj, n


def to_bipartite_random_partition(
    n: int, edges: list[tuple[int, int]], rng: np.random.Generator
) -> tuple[list[list[int]], int]:
    """Random balanced partition. Split V into L (⌊n/2⌋) and R (⌈n/2⌉); keep only
    edges crossing the partition. Returns (type_adj over L, |R|)."""
    perm = rng.permutation(n)
    half = n // 2
    l_nodes = perm[:half]
    r_nodes = perm[half:]
    l_remap = {int(v): k for k, v in enumerate(l_nodes)}
    r_remap = {int(v): k for k, v in enumerate(r_nodes)}

    type_adj: list[list[int]] = [[] for _ in range(len(l_nodes))]
    for i, j in edges:
        # keep only cross edges; orient L-side → R-side
        if i in l_remap and j in r_remap:
            type_adj[l_remap[i]].append(r_remap[j])
        elif j in l_remap and i in r_remap:
            type_adj[l_remap[j]].append(r_remap[i])
    type_adj = [sorted(a) for a in type_adj]
    return type_adj, len(r_nodes)
