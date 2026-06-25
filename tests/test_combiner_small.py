"""Hand-verifiable tests for the Chłędowski-style switching combiner (benchmark).

We assert the two defining properties of the combiner as a robustness mechanism:
  1. With GARBAGE advice it never crashes — it stays at the Ranking baseline
     (the follower never leads, so it never switches away from `base`).
  2. The irrevocable-switch HYBRID PENALTY is real and reproducible: with PERFECT
     advice and an eager (tiny-γ) combiner, switching mid-stream lands in an
     incompatible hybrid that scores BELOW both the pure follower AND the pure
     baseline — the structural reason matching needs test-and-fallback, not the
     caching-style dynamic switch.
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.synthetic import few_types_bipartite
from iid_sampler import sample_instance
from optimal import max_matching_size
from algorithms.ranking import ranking
from algorithms.test_and_match import follow_prediction
from algorithms.combiner import combiner
from predictions.type_advice import (
    true_type_counts, build_advice_matching, perturb_counts,
)


def _setup(n=600, r=6, seed=7):
    rg, ri, rs, rp = np.random.default_rng(seed).spawn(4)
    type_adj = few_types_bipartite(n, r, rg)
    instance_adj, types = sample_instance(type_adj, m=n, rng=ri)
    opt = max_matching_size(instance_adj, n_right=n)
    c_star = true_type_counts(types, n_types=r)
    return type_adj, instance_adj, types, opt, c_star, rs, rp, n, r


def test_garbage_advice_never_below_baseline():
    """Property 1: with garbage advice the combiner ≈ the Ranking floor."""
    type_adj, ia, ty, opt, c_star, rs, rp, n, r = _setup()
    ts = int(rs.integers(0, 2**31 - 1))
    chat, _ = perturb_counts(c_star, 1.0, rp)            # garbage
    n_hat, partners = build_advice_matching(type_adj, chat, n_right=n)

    follow = follow_prediction(ia, ty, n, partners, chat) / opt
    rk = ranking(ia, n, np.random.default_rng(ts)) / opt
    cm_size, info = combiner(ia, ty, n, partners, chat,
                        rng=np.random.default_rng(ts), gamma=max(20, n // 40))
    cm = cm_size / opt

    assert follow < rk - 0.05, f"garbage advice should hurt the blind follower ({follow} vs {rk})"
    assert cm >= rk - 1e-9, f"combiner {cm} dropped below the baseline {rk} on garbage advice"
    print(f"OK garbage: follow={follow:.3f}  ranking={rk:.3f}  combiner={cm:.3f} "
          f"(switches={info['n_switches']})")


def test_perfect_advice_eager_switch_hybrid_penalty():
    """Property 2: eager (γ=0) switching on PERFECT advice underperforms BOTH
    experts — the irrevocable hybrid-state penalty that motivates test-and-fallback."""
    type_adj, ia, ty, opt, c_star, rs, rp, n, r = _setup()
    ts = int(rs.integers(0, 2**31 - 1))
    chat, _ = perturb_counts(c_star, 0.0, rp)            # perfect (ĉ = c*)
    n_hat, partners = build_advice_matching(type_adj, chat, n_right=n)

    follow = follow_prediction(ia, ty, n, partners, chat) / opt
    rk = ranking(ia, n, np.random.default_rng(ts)) / opt
    cm_size, info = combiner(ia, ty, n, partners, chat,
                              rng=np.random.default_rng(ts), gamma=0)
    cm_eager = cm_size / opt

    assert follow >= rk, f"perfect advice should make the follower ≥ baseline ({follow} vs {rk})"
    assert info["n_switches"] >= 1, "eager combiner should switch on perfect advice"
    assert cm_eager < rk, (f"hybrid penalty expected: eager combiner {cm_eager} should fall "
                           f"below baseline {rk} despite perfect advice (follow={follow})")
    print(f"OK hybrid: follow={follow:.3f}  ranking={rk:.3f}  combiner(γ=0)={cm_eager:.3f} "
          f"(switches={info['n_switches']})")


def test_robust_tuning_captures_floor():
    """The intended tuning (γ scaled with n) sits at the floor across advice
    quality: robust, but capturing none of the (tiny) consistency upside."""
    type_adj, ia, ty, opt, c_star, rs, rp, n, r = _setup()
    ts = int(rs.integers(0, 2**31 - 1))
    g = max(20, n // 40)
    rk = ranking(ia, n, np.random.default_rng(ts)) / opt
    for eta in (0.0, 0.5, 1.0):
        chat, _ = perturb_counts(c_star, eta, rp)
        n_hat, partners = build_advice_matching(type_adj, chat, n_right=n)
        cm_size, _ = combiner(ia, ty, n, partners, chat,
                         rng=np.random.default_rng(ts), gamma=g)
        cm = cm_size / opt
        assert abs(cm - rk) < 0.02, f"η={eta}: robust combiner {cm} should track floor {rk}"
    print(f"OK robust tuning tracks the Ranking floor {rk:.3f} across η")


if __name__ == "__main__":
    test_garbage_advice_never_below_baseline()
    test_perfect_advice_eager_switch_hybrid_penalty()
    test_robust_tuning_captures_floor()
    print("\nall combiner tests passed")
