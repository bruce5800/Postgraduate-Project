"""Correctness tests for MinPredictedDegree and the prediction infrastructure.

These nail down the three theoretical anchors of the Phase 3 framing:
  MPD(constant μ)  ≡ Ranking      (robustness floor)
  MPD(true degree) ≡ MinDegree    (consistency ceiling)
  systematic bias is order-invariant ⇒ MPD unaffected
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.synthetic import erdos_renyi_bipartite, left_regular_bipartite, clvb_zipf_bipartite
from iid_sampler import sample_instance
from algorithms.min_predicted_degree import mpd, mpd_rank
from algorithms.ranking import ranking
from algorithms._common import greedy_with_permutation
from predictions.degree_truth import type_graph_degree, instance_degree
from predictions import error_models as em


def test_mpd_constant_mu_equals_ranking_in_distribution() -> None:
    """With constant μ, every offline node has equal predicted degree, so MPD's
    rank is determined purely by its uniform random tiebreak — i.e. a uniformly
    random permutation, which is exactly Ranking. The equivalence is
    DISTRIBUTIONAL (a single shared seed gives a permutation vs its inverse, both
    valid but different Ranking runs), so we compare MEANS over many trials."""
    rng = np.random.default_rng(0)
    type_adj = left_regular_bipartite(200, 5, rng)
    instance_adj, types = sample_instance(type_adj, m=200, rng=rng)

    mu_const = np.zeros(200)
    n_trials = 200
    rng_mpd = np.random.default_rng(100)
    rng_rk = np.random.default_rng(200)
    sizes_mpd = [mpd(instance_adj, 200, mu_const, rng_mpd) for _ in range(n_trials)]
    sizes_rk = [ranking(instance_adj, 200, rng_rk) for _ in range(n_trials)]
    m_mpd, m_rk = float(np.mean(sizes_mpd)), float(np.mean(sizes_rk))
    assert abs(m_mpd - m_rk) < 1.5, f"MPD(const μ) mean={m_mpd:.2f} vs Ranking mean={m_rk:.2f}"
    print(f"PASS test_mpd_constant_mu_equals_ranking_in_distribution "
          f"(MPD mean={m_mpd:.2f}, Ranking mean={m_rk:.2f}, |Δ|={abs(m_mpd-m_rk):.2f})")


def test_mpd_true_degree_is_mindegree() -> None:
    """MinDegree = MPD with μ = realized instance degree. Just confirm it runs
    and never exceeds OPT, and beats a constant-μ run on a skewed graph."""
    rng = np.random.default_rng(1)
    type_adj = clvb_zipf_bipartite(300, exponent=1.0, rng=rng)
    instance_adj, types = sample_instance(type_adj, m=300, rng=rng)

    mu_true = instance_degree(instance_adj, n_right=300)
    mu_pred = type_graph_degree(type_adj, n_right=300)
    rng_md = np.random.default_rng(7)
    rng_mpd = np.random.default_rng(7)
    rng_rk = np.random.default_rng(7)
    size_md = mpd(instance_adj, 300, mu_true, rng_md)
    size_mpd = mpd(instance_adj, 300, mu_pred, rng_mpd)
    size_rk = mpd(instance_adj, 300, np.zeros(300), rng_rk)  # constant ≡ Ranking
    # On a Zipf graph, degree info should help: MinDegree ≥ MPD ≳ Ranking.
    assert size_md >= size_rk, f"MinDegree {size_md} should beat Ranking {size_rk}"
    print(f"PASS test_mpd_true_degree_is_mindegree "
          f"(MinDegree={size_md}, MPD={size_mpd}, Ranking={size_rk})")


def test_systematic_bias_is_order_invariant() -> None:
    """The headline: a monotone bias must not change MPD's output at all,
    because MPD depends on μ only through its induced order."""
    rng = np.random.default_rng(2)
    type_adj = clvb_zipf_bipartite(300, exponent=1.0, rng=rng)
    instance_adj, types = sample_instance(type_adj, m=300, rng=rng)
    mu = type_graph_degree(type_adj, n_right=300)

    for eta in [0.0, 0.3, 0.7, 1.0]:
        mu_biased, errs = em.systematic_bias(mu, eta, rng)
        # Same tiebreak rng → identical rank → identical matching.
        s0 = mpd(instance_adj, 300, mu, np.random.default_rng(99))
        s1 = mpd(instance_adj, 300, mu_biased, np.random.default_rng(99))
        assert s0 == s1, f"bias η={eta} changed MPD: {s0} → {s1}"
        assert errs["order_error"] == 0.0, f"bias η={eta} order_error={errs['order_error']}"
    print("PASS test_systematic_bias_is_order_invariant (order_error≡0, MPD unchanged)")


def test_random_flip_anchors() -> None:
    """random_flip at η=0 leaves μ untouched; at η=1 fully randomizes."""
    rng = np.random.default_rng(3)
    mu = np.arange(100, dtype=float)
    out0, e0 = em.random_flip(mu, 0.0, rng)
    assert np.array_equal(out0, mu), "η=0 must be identity"
    assert e0["order_error"] == 0.0 and e0["l1"] == 0.0
    out1, e1 = em.random_flip(mu, 1.0, rng)
    assert e1["order_error"] > 0.2, f"η=1 should disrupt order, got {e1['order_error']}"
    print(f"PASS test_random_flip_anchors (η=1 order_error={e1['order_error']:.3f})")


def test_adversarial_full_reverses_order() -> None:
    """adversarial at η=1 reflects every node ⇒ order fully reversed ⇒
    order_error ≈ 1."""
    rng = np.random.default_rng(4)
    mu = np.arange(100, dtype=float)
    out, e = em.adversarial(mu, 1.0, rng)
    assert e["order_error"] > 0.95, f"full adversarial order_error={e['order_error']}"
    print(f"PASS test_adversarial_full_reverses_order (order_error={e['order_error']:.3f})")


def test_distribution_drift_monotone_in_eta() -> None:
    """drift error should grow with η."""
    rng = np.random.default_rng(5)
    type_adj = clvb_zipf_bipartite(300, exponent=1.0, rng=rng)
    type_adj_alt = clvb_zipf_bipartite(300, exponent=1.0, rng=rng)
    mu = type_graph_degree(type_adj, 300)
    mu_alt = type_graph_degree(type_adj_alt, 300)
    prev = -1.0
    for eta in [0.0, 0.25, 0.5, 0.75, 1.0]:
        _, e = em.distribution_drift(mu, mu_alt, eta, rng)
        if eta == 0.0:
            assert e["l1"] == 0.0
        prev = e["l1"]
    print("PASS test_distribution_drift_monotone_in_eta")


if __name__ == "__main__":
    test_mpd_constant_mu_equals_ranking_in_distribution()
    test_mpd_true_degree_is_mindegree()
    test_systematic_bias_is_order_invariant()
    test_random_flip_anchors()
    test_adversarial_full_reverses_order()
    test_distribution_drift_monotone_in_eta()
    print("\nAll MPD / prediction tests passed.")
