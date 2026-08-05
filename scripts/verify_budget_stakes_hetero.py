"""T1 generalization: the budget-stakes law on HETEROGENEOUS cell families.

Cell i has its own contention theta_i in (0,1] and signal eps_i in (0,1/2];
truth direction d_i, advice direction dhat_i; type masses per cell
  flexible: 1/N,  favored spec: theta_i(1/2+eps_i d_i dhat_i)/N,
  disfavored:      theta_i(1/2-eps_i d_i dhat_i)/N,   N = sum_i(1+theta_i)=OPT.

Verified claims (all closed-form-vs-simulation or exact-bound checks):
  1. PAYOFF IDENTITY survives heterogeneity verbatim:
       E[c] = 2 * (follow-advantage / OPT),  c = +1/-1/0 per arrival class,
     including MAGNITUDE-MISMATCHED truth (arbitrary s_i, advice directions
     only) — i.e. the former T2 restriction is not needed.
  2. SLACK IDENTITY: 1 - rho_base = sigma^2 / 2 exactly, where
     sigma^2 = sum_i theta_i / N is the specialist mass (= Var bound on c).
  3. HELLINGER WEIGHTS: for a pair flipping cell set W, the exact per-sample
     squared Hellinger distance lies in [4,8] * sum_W theta_i eps_i^2 / N.
  4. BUDGET SCALING: the directional test's decision error collapses as a
     function of k * g^2 / sigma^2 across heterogeneous families with very
     different (sigma^2, g) — errors small at k = 8 sigma^2/g^2 and large at
     k = sigma^2/(4 g^2), on every family.
"""
from __future__ import annotations
import numpy as np

rng = np.random.default_rng(11)


def make_family(m, theta_lo=0.2, theta_hi=0.9, eps_lo=0.05, eps_hi=0.45):
    theta = rng.uniform(theta_lo, theta_hi, m)
    eps = rng.uniform(eps_lo, eps_hi, m)
    N = float((1.0 + theta).sum())
    return theta, eps, N


def masses(theta, eps_signed, N):
    """Per-cell (favored, disfavored, flexible) masses; eps_signed = eps*d*dhat."""
    fav = theta * (0.5 + eps_signed) / N
    dis = theta * (0.5 - eps_signed) / N
    flx = np.ones_like(theta) / N
    return fav, dis, flx


def sample_c(theta, eps_signed, N, k, trials):
    """Vectorized draws of the per-sample statistic c over `trials` prefixes."""
    fav, dis, _ = masses(theta, eps_signed, N)
    p_fav, p_dis = fav.sum(), dis.sum()
    u = rng.random((trials, k))
    c = np.where(u < p_fav, 1.0, np.where(u < p_fav + p_dis, -1.0, 0.0))
    return c


print("=== 1. payoff identity, heterogeneous + magnitude-mismatched ===")
for tag, mismatch in [("matched magnitudes", False), ("mismatched (arbitrary s_i)", True)]:
    theta, eps, N = make_family(3000)
    dhat = rng.choice([-1.0, 1.0], size=len(theta))
    if mismatch:
        s = rng.uniform(0.0, 1.0, len(theta))          # arbitrary truth biases
        eps_signed = (s - 0.5) * dhat                  # relative to advice dir
    else:
        d = rng.choice([-1.0, 1.0], size=len(theta))
        eps_signed = eps * d * dhat
    adv = float((theta * eps_signed).sum()) / N        # follow-advantage / OPT
    formula = 2.0 * adv
    c = sample_c(theta, eps_signed, N, k=400, trials=4000)
    sim = float(c.mean())
    print(f"  {tag:28s} E[c] sim {sim:+.4f}  formula 2*adv {formula:+.4f}")
    assert abs(sim - formula) < 0.005, (sim, formula)

print("\n=== 2. slack identity: 1 - rho_base = sigma^2/2 (exact) ===")
theta, eps, N = make_family(3000)
sigma2 = float(theta.sum()) / N
rho_base = float((1.0 + theta / 2.0).sum()) / N
print(f"  1-rho_base = {1-rho_base:.6f}   sigma^2/2 = {sigma2/2:.6f}")
assert abs((1 - rho_base) - sigma2 / 2) < 1e-12

print("\n=== 3. Hellinger weights: H^2 in [4,8]*sum_W theta*eps^2/N (exact) ===")
for _ in range(3):
    theta, eps, N = make_family(2000)
    d = np.ones(len(theta))
    W = rng.random(len(theta)) < 0.3
    d2 = np.where(W, -1.0, 1.0)
    f1, g1, x1 = masses(theta, eps * d, N)
    f2, g2, x2 = masses(theta, eps * d2, N)
    p = np.concatenate([f1, g1, x1])
    q = np.concatenate([f2, g2, x2])
    H2 = float(((np.sqrt(p) - np.sqrt(q)) ** 2).sum())
    ref = float((theta[W] * eps[W] ** 2).sum()) / N
    print(f"  H^2 = {H2:.5f}   4*ref = {4*ref:.5f}   8*ref = {8*ref:.5f}")
    assert 4 * ref <= H2 <= 8 * ref + 1e-12

print("\n=== 4. budget scaling: error collapses in k*g^2/sigma^2 ===")
print("  family (m, sigma^2)          x=0.25   x=1   x=4   x=8   [x = k g^2/sigma^2]")
for m, th_rng in [(1000, (0.15, 0.5)), (4000, (0.5, 0.95)), (16000, (0.05, 0.25))]:
    theta, eps, N = make_family(m, *th_rng)
    sigma2 = float(theta.sum()) / N
    d_good = np.ones(m)
    W = rng.random(m) < 0.5
    d_bad = np.where(W, -1.0, 1.0)
    dhat = np.ones(m)
    # center the pair so payoffs are +-g/2 (worst case for a 0-threshold test)
    g = 2.0 * float((theta[W] * eps[W]).sum()) / N     # payoff gap of the pair
    errs = []
    for x in [0.25, 1.0, 4.0, 8.0]:
        k = max(8, int(round(x * sigma2 / (g / 2) ** 2 / 4)))  # k = x*sigma^2/g^2
        thr_trials = 1500
        e = 0.0
        for eps_signed, want_pos in [(eps * d_good * dhat, True),
                                     (eps * d_bad * dhat, False)]:
            # shift both scenarios by -mean so the pair straddles 0 symmetrically
            shift = float((theta * (eps * d_good + eps * d_bad) / 2).sum()) / N
            S = sample_c(theta, eps_signed, N, k, thr_trials).sum(axis=1)
            dec_follow = S / k > 2 * shift
            e += float(np.mean(dec_follow != want_pos)) / 2
        errs.append(e)
    print(f"  m={m:6d} sigma^2={sigma2:.3f}    " +
          "  ".join(f"{e:.3f}" for e in errs))
    assert errs[0] > 0.15, f"error too small at x=0.25: {errs[0]}"
    assert errs[-1] < 0.10, f"error too large at x=8: {errs[-1]}"
    assert all(errs[i] >= errs[i + 1] - 0.03 for i in range(3)), errs

print("\nALL CHECKS PASSED")
