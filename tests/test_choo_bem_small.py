"""Correctness tests for FollowPrediction and TestAndMatch (Choo/BEM)."""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.synthetic import few_types_bipartite
from iid_sampler import sample_instance
from optimal import max_matching_size
from algorithms.ranking import ranking
from algorithms.test_and_match import follow_prediction, test_and_match
from predictions.type_advice import (
    true_type_counts, build_advice_matching, perturb_counts,
)


def test_mimic_perfect_advice_is_optimal() -> None:
    """With perfect advice (ĉ = c*), the advice matching M̂ IS an optimal matching
    of the realized instance, so blindly following it must achieve OPT."""
    rng = np.random.default_rng(0)
    type_adj = few_types_bipartite(n_offline=400, r=8, rng=rng)
    instance_adj, types = sample_instance(type_adj, m=400, rng=rng)
    opt = max_matching_size(instance_adj, n_right=400)
    c_star = true_type_counts(types, n_types=8)
    n_hat, partners = build_advice_matching(type_adj, c_star, n_right=400)
    size = follow_prediction(instance_adj, types, 400, partners, c_star)
    assert size == opt, f"perfect-advice follow={size} should equal OPT={opt}"
    assert n_hat == opt, f"n_hat={n_hat} should equal OPT={opt} for perfect advice"
    print(f"PASS test_mimic_perfect_advice_is_optimal (follow={size}=OPT={opt})")


def test_follow_never_exceeds_opt() -> None:
    rng = np.random.default_rng(1)
    type_adj = few_types_bipartite(400, 8, rng)
    instance_adj, types = sample_instance(type_adj, m=400, rng=rng)
    opt = max_matching_size(instance_adj, 400)
    c_star = true_type_counts(types, 8)
    chat, l1 = perturb_counts(c_star, 0.5, rng)
    n_hat, partners = build_advice_matching(type_adj, chat, 400)
    size = follow_prediction(instance_adj, types, 400, partners, chat)
    assert 0 <= size <= opt
    print(f"PASS test_follow_never_exceeds_opt (size={size} <= OPT={opt}, L1={l1:.3f})")


def test_perturb_anchors() -> None:
    rng = np.random.default_rng(2)
    c_star = np.array([100.0, 50.0, 30.0, 20.0])
    chat0, l10 = perturb_counts(c_star, 0.0, rng)
    assert np.array_equal(chat0, c_star), "η=0 must give exact c*"
    assert l10 == 0.0
    assert int(chat0.sum()) == int(c_star.sum())
    chat1, l11 = perturb_counts(c_star, 1.0, rng)
    assert int(chat1.sum()) == int(c_star.sum()), "counts must still sum to n"
    assert l11 > 0.0
    print(f"PASS test_perturb_anchors (η=0 L1=0; η=1 L1={l11:.3f}, sum preserved)")


def test_consistency_perfect_advice() -> None:
    """TestAndMatch with perfect advice should pass the test and reach ~OPT."""
    rng = np.random.default_rng(3)
    type_adj = few_types_bipartite(1000, 8, rng)
    instance_adj, types = sample_instance(type_adj, m=1000, rng=rng)
    opt = max_matching_size(instance_adj, 1000)
    c_star = true_type_counts(types, 8)
    n_hat, partners = build_advice_matching(type_adj, c_star, 1000)
    size, info = test_and_match(
        instance_adj, types, 1000, partners, c_star, n_hat,
        rng=np.random.default_rng(99), variant="bem", prefix_k=300,
    )
    ratio = size / opt
    assert info["followed"], f"perfect advice should pass the test; info={info}"
    assert ratio > 0.95, f"consistency ratio {ratio:.3f} should be ~1"
    print(f"PASS test_consistency_perfect_advice (ratio={ratio:.3f}, followed={info['followed']})")


def test_robustness_garbage_advice() -> None:
    """With garbage advice, TestAndMatch must (a) stay robust — well above the 1/2
    floor and near the β≈0.696 guarantee — and (b) be no worse than blindly
    following the advice, since it can bail out to the baseline. (It need NOT match
    empirical Ranking exactly: the prefix it spends probing bad advice costs some
    matches, exactly the β·(1−k/n) robustness the theory predicts.)"""
    rng = np.random.default_rng(4)
    type_adj = few_types_bipartite(2000, 8, rng)
    instance_adj, types = sample_instance(type_adj, m=2000, rng=rng)
    opt = max_matching_size(instance_adj, 2000)
    c_star = true_type_counts(types, 8)
    chat, l1 = perturb_counts(c_star, 1.0, rng, concentration=0.15)  # strongly bad
    n_hat, partners = build_advice_matching(type_adj, chat, 2000)
    tm_size, info = test_and_match(
        instance_adj, types, 2000, partners, chat, n_hat,
        rng=np.random.default_rng(7), variant="bem", prefix_k=200,
    )
    follow = follow_prediction(instance_adj, types, 2000, partners, chat) / opt
    rk = ranking(instance_adj, 2000, np.random.default_rng(7)) / opt
    tm = tm_size / opt
    assert tm >= 0.65, f"TestAndMatch {tm:.3f} not robust (should stay near β≈0.70)"
    assert tm >= follow - 0.03, f"adaptive {tm:.3f} worse than blind follow {follow:.3f}"
    print(f"PASS test_robustness_garbage_advice (TestAndMatch={tm:.3f}, "
          f"blind-follow={follow:.3f}, Ranking={rk:.3f}, followed={info['followed']}, L1={l1:.3f})")


def test_choo_vs_bem_thresholds() -> None:
    """The two variants must compute the documented thresholds."""
    rng = np.random.default_rng(5)
    type_adj = few_types_bipartite(500, 6, rng)
    instance_adj, types = sample_instance(type_adj, m=500, rng=rng)
    c_star = true_type_counts(types, 6)
    n_hat, partners = build_advice_matching(type_adj, c_star, 500)
    _, ic = test_and_match(instance_adj, types, 500, partners, c_star, n_hat,
                           rng=np.random.default_rng(1), variant="choo", prefix_k=150)
    _, ib = test_and_match(instance_adj, types, 500, partners, c_star, n_hat,
                           rng=np.random.default_rng(1), variant="bem", prefix_k=150)
    beta = 0.696
    exp_choo = 2 * (ic["n_hat_ratio"] - beta)
    exp_bem = 2 * ib["n_hat_ratio"] * (1 - beta) / (1 + beta)
    assert abs(ic["tau"] - exp_choo) < 1e-9
    assert abs(ib["tau"] - exp_bem) < 1e-9
    print(f"PASS test_choo_vs_bem_thresholds (choo τ={ic['tau']:.3f}, bem τ={ib['tau']:.3f})")


if __name__ == "__main__":
    test_mimic_perfect_advice_is_optimal()
    test_follow_never_exceeds_opt()
    test_perturb_anchors()
    test_consistency_perfect_advice()
    test_robustness_garbage_advice()
    test_choo_vs_bem_thresholds()
    print("\nAll Choo/BEM tests passed.")
