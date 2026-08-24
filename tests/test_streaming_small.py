"""Correctness tests for the semi-streaming edge-arrival algorithms (Appendix A.7)."""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.synthetic import clvb_zipf_bipartite, left_regular_bipartite
from iid_sampler import sample_instance
from optimal import max_matching_size
from algorithms.streaming import stream_greedy, stream_multipass, edge_stream


def test_stream_greedy_is_maximal_and_half_optimal() -> None:
    """A one-pass greedy leaves a MAXIMAL matching, hence >= OPT/2 always."""
    rng = np.random.default_rng(0)
    for trial in range(20):
        type_adj = clvb_zipf_bipartite(120, 1.0, rng)
        adj, _ = sample_instance(type_adj, m=120, rng=rng)
        opt = max_matching_size(adj, n_right=120)
        if opt == 0:
            continue
        size = stream_greedy(adj, 120, np.random.default_rng(trial))
        assert 2 * size >= opt, f"maximal matching {size} < OPT/2 = {opt / 2}"
        assert size <= opt, f"streaming {size} exceeds OPT {opt}"
    print("PASS test_stream_greedy_is_maximal_and_half_optimal")


def test_passes_are_monotone_and_bounded_by_opt() -> None:
    """Every augmentation pass can only grow the matching, and never past OPT."""
    rng = np.random.default_rng(1)
    for trial in range(20):
        type_adj = left_regular_bipartite(200, 5, rng)
        adj, _ = sample_instance(type_adj, m=200, rng=rng)
        opt = max_matching_size(adj, n_right=200)
        sizes = stream_multipass(adj, 200, passes=4, rng=np.random.default_rng(trial))
        assert sizes == sorted(sizes), f"non-monotone pass sizes {sizes}"
        assert sizes[-1] <= opt, f"{sizes[-1]} exceeds OPT {opt}"
    print("PASS test_passes_are_monotone_and_bounded_by_opt")


def test_augmentation_leaves_a_valid_matching() -> None:
    """Brute-force check on tiny graphs: the reported size is a real matching size,
    and on a 3-augmentable path instance the second pass actually finds it."""
    # left0-r0 ; left1-{r0,r1}: greedy can take (left1,r0) and strand left0.
    adj = [[0], [0, 1]]
    assert max_matching_size(adj, 2) == 2
    stranded = [s for s in range(50)
                if stream_greedy(adj, 2, np.random.default_rng(s)) == 1]
    assert stranded, "expected some seed where one-pass greedy is suboptimal"
    for s in stranded:
        sizes = stream_multipass(adj, 2, passes=2, rng=np.random.default_rng(s))
        assert sizes == [1, 2], f"3-augmentation failed on seed {s}: {sizes}"
    print(f"PASS test_augmentation_leaves_a_valid_matching ({len(stranded)}/50 seeds)")


def test_edge_stream_is_a_permutation_of_the_edges() -> None:
    """The stream must contain every edge exactly once (no loss, no duplication)."""
    rng = np.random.default_rng(2)
    type_adj = left_regular_bipartite(60, 4, rng)
    adj, _ = sample_instance(type_adj, m=60, rng=rng)
    st = edge_stream(adj, np.random.default_rng(3))
    assert st.shape[0] == sum(len(nb) for nb in adj)
    got = sorted(map(tuple, st.tolist()))
    want = sorted((i, r) for i, nb in enumerate(adj) for r in nb)
    assert got == want, "edge stream is not a permutation of the edge set"
    print("PASS test_edge_stream_is_a_permutation_of_the_edges")


if __name__ == "__main__":
    test_stream_greedy_is_maximal_and_half_optimal()
    test_passes_are_monotone_and_bounded_by_opt()
    test_augmentation_leaves_a_valid_matching()
    test_edge_stream_is_a_permutation_of_the_edges()
    print("all streaming tests pass")
