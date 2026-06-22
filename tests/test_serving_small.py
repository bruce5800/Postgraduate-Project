"""Correctness tests for the serving (b-matching) instantiation."""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.serving import serving_topology
from iid_sampler import sample_instance
from optimal import max_b_matching_size, max_matching_size
from algorithms.capacity import (
    greedy_with_capacity, build_advice_b_matching,
    follow_prediction_capacity, test_and_match_capacity,
)
from algorithms.min_predicted_degree import mpd_rank
from predictions.degree_truth import type_graph_degree
from predictions.type_advice import true_type_counts, perturb_counts


def test_b_matching_capacity1_equals_matching() -> None:
    """With capacity 1, b-matching OPT must equal the ordinary matching OPT."""
    rng = np.random.default_rng(0)
    type_adj, p = serving_topology(n_resources=80, n_types=20, deg=5, rng=rng)
    inst, types = sample_instance(type_adj, m=200, rng=rng, p=p)
    opt_b = max_b_matching_size(types, type_adj, n_right=80, capacity=1)
    opt_1 = max_matching_size(inst, n_right=80)
    assert opt_b == opt_1, f"b-matching(c=1)={opt_b} vs matching={opt_1}"
    print(f"PASS test_b_matching_capacity1_equals_matching ({opt_b})")


def test_b_matching_grows_with_capacity() -> None:
    """More capacity serves at least as many requests; saturates at n_requests."""
    rng = np.random.default_rng(1)
    type_adj, p = serving_topology(60, 15, 6, rng)
    inst, types = sample_instance(type_adj, m=300, rng=rng, p=p)
    prev = -1
    for c in [1, 2, 4, 8, 20]:
        o = max_b_matching_size(types, type_adj, 60, c)
        assert o >= prev, f"capacity {c}: OPT {o} < prev {prev}"
        assert o <= 300
        prev = o
    print(f"PASS test_b_matching_grows_with_capacity (c=1→{max_b_matching_size(types,type_adj,60,1)}, c=20→{prev})")


def test_greedy_capacity_never_exceeds_opt() -> None:
    rng = np.random.default_rng(2)
    type_adj, p = serving_topology(100, 25, 6, rng)
    inst, types = sample_instance(type_adj, m=400, rng=rng, p=p)
    for c in [1, 3, 6]:
        opt = max_b_matching_size(types, type_adj, 100, c)
        mu = type_graph_degree(type_adj, 100)
        rank = mpd_rank(mu, np.random.default_rng(9))
        g = greedy_with_capacity(inst, rank, 100, c)
        assert 0 <= g <= opt, f"c={c}: greedy {g} vs OPT {opt}"
    print("PASS test_greedy_capacity_never_exceeds_opt")


def test_perfect_advice_b_matching_is_optimal() -> None:
    """Perfect forecast (ĉ = c*) ⇒ the advice b-matching IS optimal, so blindly
    following it serves OPT_b requests."""
    rng = np.random.default_rng(3)
    type_adj, p = serving_topology(120, 20, 6, rng)
    inst, types = sample_instance(type_adj, m=500, rng=rng, p=p)
    for cap in [1, 3, 5]:
        opt = max_b_matching_size(types, type_adj, 120, cap)
        c_star = true_type_counts(types, n_types=20)
        n_hat, partners = build_advice_b_matching(type_adj, c_star, 120, cap)
        served = follow_prediction_capacity(inst, types, 120, partners, c_star, cap)
        assert n_hat == opt, f"cap={cap}: n_hat {n_hat} != OPT {opt}"
        assert served == opt, f"cap={cap}: follow {served} != OPT {opt}"
    print("PASS test_perfect_advice_b_matching_is_optimal")


def test_robustness_under_capacity() -> None:
    """Garbage forecast: TestAndMatch detects it and stays robust under capacity."""
    rng = np.random.default_rng(4)
    type_adj, p = serving_topology(120, 12, 6, rng)
    inst, types = sample_instance(type_adj, m=600, rng=rng, p=p)
    cap = 4
    opt = max_b_matching_size(types, type_adj, 120, cap)
    c_star = true_type_counts(types, 12)
    chat, l1 = perturb_counts(c_star, 1.0, rng, concentration=0.15)
    n_hat, partners = build_advice_b_matching(type_adj, chat, 120, cap)
    tm, info = test_and_match_capacity(inst, types, 120, partners, chat, n_hat, cap,
                                       rng=np.random.default_rng(7), variant="bem", prefix_k=120)
    follow = follow_prediction_capacity(inst, types, 120, partners, chat, cap) / opt
    tmr = tm / opt
    assert tmr >= follow - 0.03, f"adaptive {tmr:.3f} worse than blind {follow:.3f}"
    print(f"PASS test_robustness_under_capacity (adaptive={tmr:.3f}, blind={follow:.3f}, L1={l1:.2f})")


def test_dynamic_releases_capacity() -> None:
    """A resource of capacity 1 can serve back-to-back requests if they don't
    overlap in time, but only one of two simultaneous requests."""
    from algorithms.dynamic import simulate

    def choose(l, load):
        return 0 if load[0] < 1 else None  # single resource, capacity enforced by caller

    type_adj = [[0]]
    # Two non-overlapping requests (arrive at 0 and 10, each lasts 5) → both served.
    served = simulate([0.0, 10.0], [0, 0], [5.0, 5.0], type_adj, 1, 1, choose)
    assert served == 2, f"non-overlapping should both serve; got {served}"
    # Two overlapping requests (arrive at 0 and 1, each lasts 5) → only one served.
    served = simulate([0.0, 1.0], [0, 0], [5.0, 5.0], type_adj, 1, 1, choose)
    assert served == 1, f"overlapping should serve one; got {served}"
    print("PASS test_dynamic_releases_capacity")


def test_prefix_cache_hit_semantics() -> None:
    """Leading-prefix-match: a repeated request is a full hit the second time;
    a divergent prefix hits only the shared leading blocks."""
    from algorithms.prefix_cache import run_router

    def single(hids, caches, load):
        return 0  # one replica

    # Same request twice: first miss (cache empty), second full hit.
    frac = run_router([[1, 2, 3], [1, 2, 3]], single, 1, 100)
    assert abs(frac - 0.5) < 1e-9, f"repeat should give hit 3/6=0.5; got {frac}"
    # Shared 2-block prefix then divergence: second request hits 2 of its 3.
    frac = run_router([[1, 2, 9], [1, 2, 8]], single, 1, 100)
    assert abs(frac - (2 / 6)) < 1e-9, f"shared-2 prefix should give 2/6; got {frac}"
    print("PASS test_prefix_cache_hit_semantics")


if __name__ == "__main__":
    test_prefix_cache_hit_semantics()
    test_dynamic_releases_capacity()
    test_b_matching_capacity1_equals_matching()
    test_b_matching_grows_with_capacity()
    test_greedy_capacity_never_exceeds_opt()
    test_perfect_advice_b_matching_is_optimal()
    test_robustness_under_capacity()
    print("\nAll serving (b-matching) tests passed.")
