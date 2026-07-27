"""
Verification for the T1 witness-step check (2026-07-27).

Claim under test: on the SS B.4 matched-magnitude cell family, the "directional"
statistic  c(X) = +1 if X is the advice-favored specialist of its cell,
-1 if disfavored, 0 if flexible  satisfies the exact identity

    E[c]  =  2 * (follow-advantage / OPT)  =  (2*theta*eps/(1+theta)) * (1 - 2*phi)

(phi = wrong-direction fraction), so a trivial test-and-fallback rule
"follow iff sum(c) > 0" separates the good side (phi = 1/4, l1 = a) from the
bad side (phi = 3/4, l1 = b) with error exp(-Theta(k)) — at a prefix size k
INDEPENDENT of n. If true, Theorem B.6 (impossibility for every k = o(n/log n))
is FALSE on this family, and no witness pair (gamma_k = o(1) with Theta(1)
stakes) can exist.

Checks:
  1. E[c] matches the closed form at phi in {0, 1/4, 1/2, 3/4, 1}.
  2. Decision accuracy vs k at m=2000: should approach 1 rapidly.
  3. Decision accuracy at fixed k=200 as m grows 2000 -> 200000 (n = 1.6m
     grows 100x): should stay FLAT (n-independence — the kill shot).
  4. eta_c + eta_r implied by the decisions (Lemma B.1 says >= 1 - gamma_k;
     if the test works, gamma_k -> 1, not o(1)).
  5. Plug-in empirical l1(p_hat, q) at k << r: near 2 and nearly identical
     across phi — confirming the *l1-threshold* class really is blind here
     (the part of the old story that survives).
"""
import numpy as np

rng = np.random.default_rng(7)
THETA, EPS = 0.6, 0.3

RHO_BASE = (1 + THETA / 2) / (1 + THETA)          # 0.8125
RHO_PERF = (1 + THETA * (0.5 + EPS)) / (1 + THETA)  # 0.925
L1_STAR = 2 * (RHO_PERF - RHO_BASE)                # 0.225
DELTA = L1_STAR / 4                                 # stakes at phi = 1/4 vs 3/4


def trial_stat(m, k, phi, want_l1=False):
    """One trial: sample k arrivals, return (sum of c, plug-in l1 if asked).

    Advice WLOG predicts alpha-majority in every cell (dhat_i = +1). Truth
    directions are i.i.d. wrong with prob phi, drawn lazily only for the cells
    the prefix actually touches (consistent within the trial).
    """
    cells = rng.integers(0, m, size=k)
    uniq, inv = np.unique(cells, return_inverse=True)
    d_uniq = np.where(rng.random(uniq.size) < phi, -1.0, 1.0)
    d = d_uniq[inv]
    u = rng.random(k)
    p_spec = THETA / (1 + THETA)
    is_spec = u < p_spec
    v = rng.random(k)
    s = 0.5 + EPS * d
    is_alpha = is_spec & (v < s)          # advice-favored specialist
    is_beta = is_spec & ~(v < s)          # disfavored
    stat = int(is_alpha.sum()) - int(is_beta.sum())
    if not want_l1:
        return stat, None
    # plug-in l1(p_hat, q): p_hat has k atoms of 1/k on the drawn type ids;
    # q masses: F=1/N, alpha=theta*(.5+EPS)/N, beta=theta*(.5-EPS)/N, N=m(1+theta)
    N = m * (1 + THETA)
    type_id = cells * 3 + np.where(is_alpha, 1, np.where(is_beta, 2, 0))
    tid_u, counts = np.unique(type_id, return_counts=True)
    kind = tid_u % 3
    q_seen = np.where(kind == 0, 1.0,
                      np.where(kind == 1, THETA * (0.5 + EPS),
                               THETA * (0.5 - EPS))) / N
    l1 = float(np.abs(counts / k - q_seen).sum() + (1.0 - q_seen.sum()))
    return stat, l1


def batch(m, k, phi, trials, want_l1=False):
    stats, l1s = np.empty(trials), np.empty(trials)
    for t in range(trials):
        s, l1 = trial_stat(m, k, phi, want_l1)
        stats[t] = s
        l1s[t] = l1 if l1 is not None else np.nan
    return stats, l1s


print(f"rho_base={RHO_BASE:.4f}  rho_perfect={RHO_PERF:.4f}  "
      f"l1*={L1_STAR:.4f}  stakes delta=Delta={DELTA:.4f}\n")

# --- Check 1: E[c]/k matches 0.225*(1-2phi) --------------------------------
print("Check 1 — per-sample mean of c vs closed form 2*theta*eps*(1-2phi)/(1+theta):")
for phi in (0.0, 0.25, 0.5, 0.75, 1.0):
    stats, _ = batch(2000, 400, phi, 800)
    pred = 2 * THETA * EPS * (1 - 2 * phi) / (1 + THETA)
    print(f"  phi={phi:4.2f}   sim {np.mean(stats)/400:+.4f}   formula {pred:+.4f}")

# --- Check 2: accuracy vs k (m fixed) --------------------------------------
print("\nCheck 2 — decision rule 'follow iff sum(c)>0', m=2000, 2000 trials:")
print("  k     P(follow|good phi=1/4)   P(fallback|bad phi=3/4)   eta_c+eta_r")
for k in (25, 50, 100, 200, 400, 800):
    sg, _ = batch(2000, k, 0.25, 2000)
    sb, _ = batch(2000, k, 0.75, 2000)
    acc_g = float(np.mean(sg > 0))
    acc_b = float(np.mean(sb <= 0))
    print(f"  {k:<5d} {acc_g:^24.3f} {acc_b:^25.3f} {2 - acc_g - acc_b:^12.3f}")

# --- Check 3: fixed k, growing m (n-independence) --------------------------
print("\nCheck 3 — fixed k=200, growing m (n=1.6m; theorem needs failure at k=o(n/log n)):")
for m in (2000, 20000, 200000):
    sg, _ = batch(m, 200, 0.25, 2000)
    sb, _ = batch(m, 200, 0.75, 2000)
    acc_g, acc_b = float(np.mean(sg > 0)), float(np.mean(sb <= 0))
    n = int(1.6 * m)
    print(f"  m={m:<7d} n={n:<7d} n/log n~{n/np.log(n):>8.0f}   "
          f"acc_good={acc_g:.3f}  acc_bad={acc_b:.3f}  eta_c+eta_r={2-acc_g-acc_b:.3f}")

# --- Check 5: plug-in l1 is blind (the surviving half of the old story) ----
print("\nCheck 5 — plug-in l1(p_hat,q) at k=200, m=2000 (r=6000 types), 400 trials:")
for phi in (0.25, 0.75):
    _, l1s = batch(2000, 200, phi, 400, want_l1=True)
    print(f"  phi={phi:4.2f}   mean plug-in l1 = {np.nanmean(l1s):.4f} "
          f"(sd {np.nanstd(l1s):.4f})   [true l1 = {4*THETA*EPS*phi/(1+THETA):.4f}]")
print("\n(The two phi's true l1 differ by 0.225, but the plug-in estimate is ~2 and")
print(" nearly identical across phi -> the l1-THRESHOLD class really is blind at")
print(" k << r. The directional statistic is not. That asymmetry is the finding.)")
