"""Semi-streaming matching in the edge-arrival model (thesis Appendix A.7).

The body of the thesis works in the ONLINE VERTEX-ARRIVAL model: an online node
arrives, reveals its whole neighbourhood, and must be matched immediately and
irrevocably. The original project brief suggested a different relaxation — the
SEMI-STREAMING model, in which the graph arrives as a stream of EDGES in
arbitrary order, working memory is O(n polylog n) (enough to hold a matching but
not the graph), and the algorithm may take p passes over the stream.

The two models relax different constraints, which is the point of comparing them:
streaming forbids storing the graph but, for p > 1, permits REVISION of earlier
decisions; the online model permits unlimited memory but forbids revision.

Both routines below keep a maximal matching and so are >= OPT/2 in the worst case
(Feigenbaum, Kannan, McGregor, Suri, Zhang 2005). `stream_multipass` is the
standard length-3 augmentation pass (McGregor 2005), specialised to bipartite
graphs, where one pass suffices to collect a maximal set of vertex-disjoint
3-augmenting paths in O(n) memory.

One entry does double duty: a single pass in a uniformly random edge order is
exactly offline Greedy on a randomly permuted edge list, so `stream_greedy`
covers both of the brief's suggestions at their weakest common point.
"""
from __future__ import annotations
import numpy as np


def edge_stream(instance_adj: list[list[int]], rng: np.random.Generator) -> np.ndarray:
    """Flatten an instance into a uniformly random stream of (left, right) edges."""
    left = np.concatenate([np.full(len(nb), i, dtype=np.int64)
                           for i, nb in enumerate(instance_adj) if nb]) \
        if any(instance_adj) else np.empty(0, dtype=np.int64)
    right = np.concatenate([np.asarray(nb, dtype=np.int64)
                            for nb in instance_adj if nb]) \
        if any(instance_adj) else np.empty(0, dtype=np.int64)
    order = rng.permutation(left.size)
    return np.stack([left[order], right[order]], axis=1)


def _greedy_pass(stream: np.ndarray, mate_l: np.ndarray, mate_r: np.ndarray) -> int:
    """One pass: add any edge whose both endpoints are still free. Returns growth."""
    grown = 0
    for u, r in stream:
        if mate_l[u] == -1 and mate_r[r] == -1:
            mate_l[u] = r
            mate_r[r] = u
            grown += 1
    return grown


def _augment_pass(stream: np.ndarray, mate_l: np.ndarray, mate_r: np.ndarray) -> int:
    """One pass collecting length-3 augmenting paths, O(n) memory. Returns growth.

    A 3-augmenting path is free-left a -- r -- u -- free-right b, where (u, r) is
    a matched pair. During the pass we remember, per matched right node r, one
    free left neighbour a[r], and per matched left node u, one free right
    neighbour b[u]; both are O(n). Augmentations are committed at the end of the
    pass, greedily, so that the paths taken are vertex-disjoint.
    """
    n_left, n_right = mate_l.size, mate_r.size
    free_left_of = np.full(n_right, -1, dtype=np.int64)   # a[r]
    free_right_of = np.full(n_left, -1, dtype=np.int64)   # b[u]
    for u, r in stream:
        if mate_l[u] == -1:
            if mate_r[r] != -1 and free_left_of[r] == -1:
                free_left_of[r] = u
        elif mate_r[r] == -1 and free_right_of[u] == -1:
            free_right_of[u] = r

    grown = 0
    used_left = np.zeros(n_left, dtype=bool)
    used_right = np.zeros(n_right, dtype=bool)
    for u in range(n_left):
        r = mate_l[u]
        if r == -1:
            continue
        a, b = free_left_of[r], free_right_of[u]
        if a == -1 or b == -1 or used_left[a] or used_right[b]:
            continue
        mate_l[a], mate_r[r] = r, a       # a takes u's partner
        mate_l[u], mate_r[b] = b, u       # u moves to the free right node
        used_left[a] = used_right[b] = True
        grown += 1
    return grown


def stream_greedy(instance_adj: list[list[int]], n_right: int,
                  rng: np.random.Generator) -> int:
    """One-pass semi-streaming greedy: size of the maximal matching it leaves."""
    mate_l = np.full(len(instance_adj), -1, dtype=np.int64)
    mate_r = np.full(n_right, -1, dtype=np.int64)
    return _greedy_pass(edge_stream(instance_adj, rng), mate_l, mate_r)


def stream_multipass(instance_adj: list[list[int]], n_right: int, passes: int,
                     rng: np.random.Generator) -> list[int]:
    """p-pass semi-streaming matching: sizes after pass 1, 2, ..., p.

    Pass 1 is greedy; every later pass is a 3-augmentation pass. The stream is
    re-shuffled per pass (arbitrary order is the model's assumption, and a fixed
    order would make later passes deterministic replays of the first).
    """
    mate_l = np.full(len(instance_adj), -1, dtype=np.int64)
    mate_r = np.full(n_right, -1, dtype=np.int64)
    size = _greedy_pass(edge_stream(instance_adj, rng), mate_l, mate_r)
    sizes = [size]
    for _ in range(passes - 1):
        size += _augment_pass(edge_stream(instance_adj, rng), mate_l, mate_r)
        sizes.append(size)
    return sizes
