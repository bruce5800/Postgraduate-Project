"""Correctness tests for the arrival-order probe (thesis §10.3 / Appendix)."""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from optimal import max_matching_size
from algorithms.greedy import simple_greedy
from algorithms.min_predicted_degree import mpd
from predictions.degree_truth import instance_degree
from scripts.run_arrival_order import hard_greedy_instance, reorder, order_index


def test_construction_admits_a_perfect_matching() -> None:
    """OPT must be 2m — otherwise the 0.5 ratio would be an artefact."""
    for m in (1, 2, 5, 40):
        inst, n_right = hard_greedy_instance(m)
        assert n_right == 2 * m
        assert max_matching_size(inst, n_right) == 2 * m, f"m={m}"
    print("PASS test_construction_admits_a_perfect_matching")


def test_order_alone_moves_greedy_between_1_and_one_half() -> None:
    """Same graph, two orders: exactly OPT and exactly OPT/2."""
    m = 60
    inst, n_right = hard_greedy_instance(m)
    opt = max_matching_size(inst, n_right)
    hostile = list(range(2 * m))
    friendly = list(range(m, 2 * m)) + list(range(m))
    zeros = np.zeros(2 * m, dtype=int)
    h, _ = reorder(inst, zeros, hostile)
    f, _ = reorder(inst, zeros, friendly)
    assert simple_greedy(h, n_right) == opt // 2, "hostile order should force OPT/2"
    assert simple_greedy(f, n_right) == opt, "friendly order should be optimal"
    print("PASS test_order_alone_moves_greedy_between_1_and_one_half")


def test_degree_prediction_rescues_the_hostile_order() -> None:
    """MPD's 'match your rarest option' rule is exactly the right call here."""
    m = 60
    inst, n_right = hard_greedy_instance(m)
    opt = max_matching_size(inst, n_right)
    mu = instance_degree(inst, n_right)
    for s in range(5):
        got = mpd(inst, n_right, mu, np.random.default_rng(s))
        assert got == opt, f"MPD got {got}, expected OPT={opt} (seed {s})"
    print("PASS test_degree_prediction_rescues_the_hostile_order")


def test_reorder_preserves_the_instance() -> None:
    """Permuting arrivals must not change the graph, hence not change OPT."""
    rng = np.random.default_rng(0)
    inst = [sorted(rng.choice(50, size=int(rng.integers(1, 8)), replace=False).tolist())
            for _ in range(50)]
    types = np.arange(50)
    opt = max_matching_size(inst, 50)
    for kind in ("random", "flexible_first", "inflexible_first"):
        idx = order_index(inst, kind, np.random.default_rng(1))
        adj, ty = reorder(inst, types, idx)
        assert sorted(map(tuple, adj)) == sorted(map(tuple, inst)), kind
        assert max_matching_size(adj, 50) == opt, kind
        assert sorted(ty.tolist()) == list(range(50)), kind
    # the hostile order really is degree-descending
    idx = order_index(inst, "flexible_first", np.random.default_rng(1))
    degs = [len(inst[i]) for i in idx]
    assert degs == sorted(degs, reverse=True)
    print("PASS test_reorder_preserves_the_instance")


if __name__ == "__main__":
    test_construction_admits_a_perfect_matching()
    test_order_alone_moves_greedy_between_1_and_one_half()
    test_degree_prediction_rescues_the_hostile_order()
    test_reorder_preserves_the_instance()
    print("all arrival-order tests pass")
