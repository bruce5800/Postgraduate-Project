"""Four structured prediction-error models for the degree predictor μ (object A).

Each model takes the ground-truth degree vector μ* and a strength η ∈ [0,1],
and returns (μ_perturbed, error_dict). error_dict reports two x-axes for RQ2:
  - 'l1'          : normalized L1 magnitude  ‖μ'−μ*‖₁ / ‖μ*‖₁
  - 'order_error' : normalized Kendall-τ distance ∈ [0,1] between the orders
                    μ* and μ' induce on the offline nodes (0 = same order).

The key design point (docs/PHASE3_SPEC.md §3.1, §4.4): MPD depends on μ only
through the induced ORDER. So 'systematic_bias' is order-preserving and must
leave MPD unchanged (order_error ≡ 0) while its L1 magnitude grows — the sharp
demonstration that error structure, not magnitude, drives impact.
"""
from __future__ import annotations
import numpy as np
from scipy.stats import kendalltau


def _order_error(mu_true: np.ndarray, mu_pred: np.ndarray) -> float:
    """Normalized Kendall-τ distance in [0,1]; 0 = identical order, 1 = reversed."""
    if np.all(mu_true == mu_true[0]) or np.all(mu_pred == mu_pred[0]):
        return 0.0
    tau, _ = kendalltau(mu_true, mu_pred)
    if np.isnan(tau):
        return 0.0
    dist = (1.0 - tau) / 2.0
    # Clamp float noise: τ=1 (identical order) can return 1-1e-16 with ties.
    if abs(dist) < 1e-12:
        return 0.0
    return float(dist)


def _l1(mu_true: np.ndarray, mu_pred: np.ndarray) -> float:
    denom = np.abs(mu_true).sum()
    if denom == 0:
        return 0.0
    return float(np.abs(mu_pred - mu_true).sum() / denom)


def _errors(mu_true: np.ndarray, mu_pred: np.ndarray) -> dict[str, float]:
    return {"l1": _l1(mu_true, mu_pred), "order_error": _order_error(mu_true, mu_pred)}


def random_flip(
    mu: np.ndarray, eta: float, rng: np.random.Generator
) -> tuple[np.ndarray, dict[str, float]]:
    """Independently, w.p. η, replace μ(r) with a uniform random value in [min,max].

    η=0 → μ unchanged (MinDegree/MPD order); η=1 → fully random (≡ Ranking).
    """
    lo, hi = float(mu.min()), float(mu.max())
    out = mu.copy()
    flip = rng.random(mu.shape[0]) < eta
    out[flip] = rng.uniform(lo, hi, size=int(flip.sum()))
    return out, _errors(mu, out)


def systematic_bias(
    mu: np.ndarray, eta: float, rng: np.random.Generator
) -> tuple[np.ndarray, dict[str, float]]:
    """Monotone (order-preserving) rescale μ ← μ·(1+η).

    Order-invariant ⇒ MPD is provably unaffected (order_error ≡ 0), even though
    L1 magnitude grows linearly in η. The methodological headline.
    """
    out = mu * (1.0 + eta)
    return out, _errors(mu, out)


def adversarial(
    mu: np.ndarray, eta: float, rng: np.random.Generator
) -> tuple[np.ndarray, dict[str, float]]:
    """Reflect μ on an η-fraction of nodes: μ'(r) = (min+max) − μ(r).

    Reflecting inverts the degree signal (low↔high) for the chosen nodes — the
    most order-damaging perturbation at a given fraction. η=1 reverses the whole
    order, so MPD then prioritizes the HIGHEST-degree nodes (worst case).
    """
    lo, hi = float(mu.min()), float(mu.max())
    out = mu.copy()
    k = int(round(eta * mu.shape[0]))
    if k > 0:
        idx = rng.choice(mu.shape[0], size=k, replace=False)
        out[idx] = (lo + hi) - mu[idx]
    return out, _errors(mu, out)


def distribution_drift(
    mu: np.ndarray, mu_alt: np.ndarray, eta: float, rng: np.random.Generator
) -> tuple[np.ndarray, dict[str, float]]:
    """Blend toward μ_alt (degrees from an independently sampled graph of the
    same family): μ' = (1−η)·μ + η·μ_alt.

    Models a predictor trained on a drifted/old distribution. Structured and
    realistic — the order error grows with η but in a correlated way, unlike
    random_flip.
    """
    out = (1.0 - eta) * mu + eta * mu_alt
    return out, _errors(mu, out)
