"""Hand-verifiable correctness tests for JailletLu."""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from algorithms.jaillet_lu import (
    jaillet_lu_preprocess,
    jaillet_lu_online,
    jaillet_lu_online_greedy,
    _sample_list,
)


def test_single_edge() -> None:
    """L=1, R=1, single edge. Max flow value = min(3, 3, 2) = 2.
    f*_{l0, r0} = 2/3. N'(l0) = [r0], probs = [2/3]."""
    type_adj = [[0]]
    rn, rp = jaillet_lu_preprocess(type_adj, n_right=1)
    assert rn == [[0]], f"rn={rn}"
    assert rp[0] == [2 / 3], f"rp={rp}"
    print("PASS test_single_edge")


def test_K22() -> None:
    """K_{2,2}: 2x2 complete bipartite.

    Max flow: each r sends 3 units total to {l0, l1}, capped by 2 per edge.
    So each r sends 2 to one l and 1 to the other. Symmetric: l0, l1 each
    receive 3 units (filling their cap-3 sink edge).
    Total flow = 6. f*_{l,r} ∈ {1/3, 2/3} with sums ≤ 1 per row and column.
    """
    type_adj = [[0, 1], [0, 1]]
    rn, rp = jaillet_lu_preprocess(type_adj, n_right=2)
    for l in range(2):
        s = sum(rp[l])
        assert abs(s - 1.0) < 1e-9, f"l={l} sum={s}"
        for p in rp[l]:
            assert abs(p - 1 / 3) < 1e-9 or abs(p - 2 / 3) < 1e-9, f"p={p}"
        assert sorted(rn[l]) == [0, 1], f"l={l} rn={rn[l]}"
    print(f"PASS test_K22  (rn={rn}, rp={rp})")


def test_sample_list_distribution() -> None:
    """Empirical check: for k=2 with probs (2/3, 1/3),
    ⟨r1, r2⟩ appears ~2/3 of the time, ⟨r2, r1⟩ ~1/3, dummy never."""
    rng = np.random.default_rng(0)
    counts = {"r0_first": 0, "r1_first": 0, "dummy": 0}
    n_trials = 60000
    for _ in range(n_trials):
        lst = _sample_list([10, 20], [2 / 3, 1 / 3], rng)
        if lst == [10, 20]:
            counts["r0_first"] += 1
        elif lst == [20, 10]:
            counts["r1_first"] += 1
        else:
            counts["dummy"] += 1
    p0 = counts["r0_first"] / n_trials
    p1 = counts["r1_first"] / n_trials
    pd = counts["dummy"] / n_trials
    assert abs(p0 - 2 / 3) < 0.01, f"p(r0_first)={p0}"
    assert abs(p1 - 1 / 3) < 0.01, f"p(r1_first)={p1}"
    assert pd < 0.005, f"dummy should be 0; got {pd}"
    print(f"PASS test_sample_list_distribution  (p0={p0:.3f}, p1={p1:.3f}, pd={pd:.3f})")


def test_sample_list_dummy_present() -> None:
    """k=2 with probs (1/3, 1/3) → dummy mass = 1/3."""
    rng = np.random.default_rng(0)
    n_trials = 60000
    dummy_count = 0
    for _ in range(n_trials):
        lst = _sample_list([10, 20], [1 / 3, 1 / 3], rng)
        if not lst:
            dummy_count += 1
    pd = dummy_count / n_trials
    assert abs(pd - 1 / 3) < 0.01, f"dummy prob {pd}, expected 1/3"
    print(f"PASS test_sample_list_dummy_present  (pd={pd:.3f})")


def test_k3_uniform_permutation() -> None:
    """k=3 → uniform over 6 permutations, each ≈ 1/6."""
    rng = np.random.default_rng(0)
    counts: dict[tuple[int, ...], int] = {}
    n_trials = 60000
    for _ in range(n_trials):
        lst = tuple(_sample_list([10, 20, 30], [1 / 3, 1 / 3, 1 / 3], rng))
        counts[lst] = counts.get(lst, 0) + 1
    assert len(counts) == 6, f"expected 6 distinct perms, got {len(counts)}"
    for perm, ct in counts.items():
        p = ct / n_trials
        assert abs(p - 1 / 6) < 0.01, f"perm {perm}: prob {p}"
    print(f"PASS test_k3_uniform_permutation  ({len(counts)} perms, each ~{1/6:.3f})")


def test_online_does_not_exceed_OPT() -> None:
    """K_{2,2}, m=2 arrivals. OPT ≤ 2; both algorithm variants ≤ 2."""
    type_adj = [[0, 1], [0, 1]]
    rn, rp = jaillet_lu_preprocess(type_adj, n_right=2)
    rng = np.random.default_rng(0)
    types = rng.integers(0, 2, size=2)
    instance_adj = [type_adj[t] for t in types]
    s1 = jaillet_lu_online(instance_adj, types, 2, rn, rp, rng)
    s2 = jaillet_lu_online_greedy(instance_adj, types, 2, rn, rp, rng)
    assert 0 <= s1 <= 2 and 0 <= s2 <= 2
    print(f"PASS test_online_does_not_exceed_OPT  (non-greedy={s1}, greedy={s2})")


if __name__ == "__main__":
    test_single_edge()
    test_K22()
    test_sample_list_distribution()
    test_sample_list_dummy_present()
    test_k3_uniform_permutation()
    test_online_does_not_exceed_OPT()
    print("\nAll JailletLu small-graph tests passed.")
