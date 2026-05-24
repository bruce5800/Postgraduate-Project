"""Hand-verifiable correctness tests for FeldmanEtAl building blocks."""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from algorithms.feldman import (
    _max_flow_unit_edges,
    blue_red_decomposition,
    feldman_preprocess,
    feldman_online,
    feldman_online_greedy,
)


def _check_blue_red_invariants(Mb: np.ndarray, Mr: np.ndarray, name: str) -> None:
    # Red must be a proper matching on R: no R-node is the red partner of >1 L.
    rs = [int(r) for r in Mr if r != -1]
    assert len(rs) == len(set(rs)), f"[{name}] red is NOT a matching on R: {rs}"
    # Each L has at most one Mb and one Mr (by array construction).
    # Mb need NOT be a matching on R (semi-matching).


def test_single_edge() -> None:
    """L=1, R=1, single edge. Path length 1 (odd) → 1 blue, 0 red."""
    type_adj = [[0]]
    Mb, Mr = feldman_preprocess(type_adj, n_right=1)
    assert Mb.tolist() == [0], f"Mb={Mb.tolist()}"
    assert Mr.tolist() == [-1], f"Mr={Mr.tolist()}"
    _check_blue_red_invariants(Mb, Mr, "single_edge")
    print("PASS test_single_edge")


def test_K42_paper_example() -> None:
    """Paper §2.3.2 example.

    L = {l0, l1, l2, l3}, R = {r0, r1}, complete K_{4,2}.
    Per paper: 'one possible max flow sends 2 units through r1 into l1, l2 and
    2 units through r2 into l1, l2.' Vanilla FeldmanEtAl covers only 2 of 4
    L-nodes — BahmaniKapralov's balancing is what extends coverage to all 4.

    Verified here:
      - flow value = 4 (4 unit edges)
      - exactly 2 L-nodes are covered (each with both blue and red)
      - red is a proper matching on R
    """
    type_adj = [[0, 1]] * 4
    edges = _max_flow_unit_edges(type_adj, n_right=2)
    assert len(edges) == 4, f"expected 4 unit edges, got {len(edges)}"

    Mb, Mr = blue_red_decomposition(edges, n_left=4)
    covered = sum(1 for l in range(4) if Mb[l] != -1 or Mr[l] != -1)
    assert covered == 2, f"vanilla Feldman covers exactly 2 of 4 L; got {covered}"
    # The 2 covered L's should each have BOTH a blue and red partner.
    full_cover = sum(1 for l in range(4) if Mb[l] != -1 and Mr[l] != -1)
    assert full_cover == 2, f"the 2 covered L's should have both colors; got {full_cover}"
    _check_blue_red_invariants(Mb, Mr, "K42")
    print(f"PASS test_K42_paper_example  (Mb={Mb.tolist()}, Mr={Mr.tolist()})")


def test_path_length_3() -> None:
    """L-R-L-R path of 3 edges. Odd → blue, red, blue."""
    # Edges: (r0, l0), (r0, l1), (r1, l1)? No — that's not a path.
    # A path of 3 edges: r0-l0-r1-l1. So edges (r0,l0), (r1,l0), (r1,l1).
    # But that requires l0 to have degree 2 (r0 and r1) and l1 only r1.
    # Then flow: each l has cap 2 to t, each r has cap 2 from s. With 2 L and
    # 2 R and 3 edges, max flow = 3.
    type_adj = [[0, 1], [1]]  # l0 → {r0, r1};  l1 → {r1}
    edges = _max_flow_unit_edges(type_adj, n_right=2)
    # All 3 edges saturated.
    assert len(edges) == 3, f"expected 3 unit edges, got {len(edges)}"
    Mb, Mr = blue_red_decomposition(edges, n_left=2)
    _check_blue_red_invariants(Mb, Mr, "path_length_3")
    # Both L should be covered (path of length 3 yields 2 blue edges covering both L).
    for l in range(2):
        assert Mb[l] != -1 or Mr[l] != -1, f"L{l} uncovered"
    print(f"PASS test_path_length_3  (Mb={Mb.tolist()}, Mr={Mr.tolist()})")


def test_LL_even_path() -> None:
    """L-R-L-R-L path of 4 edges (L-L even). Rule: blue, blue, red, blue.
    Should cover all 3 L-nodes with blue.
    """
    # Path: l0 - r0 - l1 - r1 - l2
    # Edges: (r0,l0), (r0,l1), (r1,l1), (r1,l2). 4 edges.
    type_adj = [[0], [0, 1], [1]]
    edges = _max_flow_unit_edges(type_adj, n_right=2)
    assert len(edges) == 4, f"expected 4, got {len(edges)}"
    Mb, Mr = blue_red_decomposition(edges, n_left=3)
    _check_blue_red_invariants(Mb, Mr, "LL_even")
    # All 3 L should have a blue partner (per the rule "first two edges blue, ...").
    blue_count = sum(1 for x in Mb if x != -1)
    assert blue_count == 3, f"expected 3 L with blue, got {blue_count}; Mb={Mb.tolist()}"
    print(f"PASS test_LL_even_path  (Mb={Mb.tolist()}, Mr={Mr.tolist()})")


def test_cycle_4() -> None:
    """4-cycle: l0-r0-l1-r1-l0. Alternate blue/red."""
    type_adj = [[0, 1], [0, 1]]
    edges = _max_flow_unit_edges(type_adj, n_right=2)
    # Max flow = 4 (both r send 2, both l receive 2). All 4 edges saturated.
    assert len(edges) == 4, f"expected 4, got {len(edges)}"
    Mb, Mr = blue_red_decomposition(edges, n_left=2)
    _check_blue_red_invariants(Mb, Mr, "cycle_4")
    # Every L gets 1 blue + 1 red.
    for l in range(2):
        assert Mb[l] != -1 and Mr[l] != -1, f"L{l} not fully covered"
    print(f"PASS test_cycle_4  (Mb={Mb.tolist()}, Mr={Mr.tolist()})")


def test_online_does_not_exceed_OPT() -> None:
    """Sanity: on K_{4,2}, both online variants give matchings ≤ OPT=2."""
    type_adj = [[0, 1]] * 4
    Mb, Mr = feldman_preprocess(type_adj, n_right=2)
    rng = np.random.default_rng(0)
    types = rng.integers(0, 4, size=4)
    instance_adj = [type_adj[t] for t in types]
    s1 = feldman_online(instance_adj, types, 2, Mb, Mr)
    s2 = feldman_online_greedy(instance_adj, types, 2, Mb, Mr)
    assert 0 <= s1 <= 2, f"non-greedy matched {s1}"
    assert 0 <= s2 <= 2, f"greedy matched {s2}"
    assert s2 >= s1, f"greedy({s2}) should be >= non-greedy({s1})"
    print(f"PASS test_online_does_not_exceed_OPT  (non-greedy={s1}, greedy={s2})")


if __name__ == "__main__":
    test_single_edge()
    test_K42_paper_example()
    test_path_length_3()
    test_LL_even_path()
    test_cycle_4()
    test_online_does_not_exceed_OPT()
    print("\nAll FeldmanEtAl small-graph tests passed.")
