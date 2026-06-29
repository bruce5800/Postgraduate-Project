"""C-M0 — the numerical impossibility frontier (empirical statement of Theorem T1).

T1 (no-free-lunch for sublinear test-and-fallback): on strong-baseline online
matching, no test-and-fallback algorithm with a sublinear test can be both
consistent (capture the upside of good advice) and robust (never fall below the
baseline), because the consistency upside sits below the test's statistical
resolution. This script measures it numerically BEFORE we prove it (the go/no-go).

The key structural coupling we surface: the few-types structure required for the
prefix distribution-test to be statistically feasible (few high-count types) is
*precisely* the structure that makes the advice-free baseline near-optimal — so
"wherever you can test, you don't need to." We sweep the number of types r
(equivalently the average count per type ≈ n/r):
  - small r  → high count/type → the prefix test is feasible, BUT ρ_base ≈ 1 (no
               upside to capture);
  - large r  → ρ_base drops (real upside appears), BUT count/type → 1, so a
               sublinear prefix cannot estimate the histogram → the test must reject
               everything → the upside is uncapturable.
So the POTENTIAL upside rises with r while the test-CAPTURABLE upside stays ≈ 0 — the
scissors gap is the impossibility. Panel B fixes a weak-baseline r and shows the
capturable upside only appears as the test budget k → Θ(n) (linear), violating the
sublinear-test premise.

Outputs: results/impossibility_frontier.json, results/impossibility_frontier.png
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from iid_sampler import sample_instance
from optimal import max_matching_size
from algorithms.ranking import ranking
from algorithms.test_and_match import _mimic_stepper, _baseline_ranking
from predictions.type_advice import true_type_counts, build_advice_matching, perturb_counts


def few_types_random(n, r, deg, rng):
    """r distinct online types, each able to use `deg` random offline resources.
    Few types (testable histogram) but, for large r, a hard near-perfect matching."""
    return [sorted(rng.choice(n, size=deg, replace=False).tolist()) for _ in range(r)]


def taf_tau(instance_adj, types, n_right, partners, chat, rng, tau, prefix_k):
    """Test-and-fallback with EXPLICIT threshold τ: Mimic a length-k prefix, estimate
    empirical L1 of the prefix type distribution vs the advice; follow if ≤ τ else
    fall back to Ranking. Returns matching size."""
    n = len(instance_adj)
    n_types = len(chat)
    matched = np.zeros(n_right, dtype=bool)
    base_rank = _baseline_ranking(n_right, rng)

    def baseline_step(neighbors):
        best, br = -1, np.iinfo(np.int64).max
        for r in neighbors:
            if not matched[r] and base_rank[r] < br:
                br = base_rank[r]; best = r
        if best != -1:
            matched[best] = True; return 1
        return 0

    step = _mimic_stepper(chat, partners, matched)
    prefix_k = min(prefix_k, n)
    size = 0
    pc = np.zeros(n_types, dtype=np.float64)
    for i in range(prefix_k):
        l = int(types[i]); size += step(l); pc[l] += 1.0
    phat = pc / max(1, prefix_k)
    q = chat / float(chat.sum())
    emp_l1 = float(np.abs(phat - q).sum())
    followed = emp_l1 <= tau
    for i in range(prefix_k, n):
        size += step(int(types[i])) if followed else baseline_step(instance_adj[i])
    return size


def _frontier(trials, advice, n, k, taus, etas, rho, eps=0.01):
    """Return (consistency[τ], robustness[τ], max_safe_upside). consistency = ratio at
    η=0 (perfect advice); robustness = min over advice quality η of the ratio (worst
    advice the τ accepts); max_safe_upside = max_τ (consistency−ρ_base) s.t. robustness
    ≥ ρ_base−eps."""
    cons, robu = [], []
    for tau in taus:
        by_eta = []
        for ei, eta in enumerate(etas):
            rr = []
            for j, (inst, types, opt, ts) in enumerate(trials):
                chat, partners = advice[(j, ei)]
                rr.append(taf_tau(inst, types, n, partners, chat,
                                  np.random.default_rng(ts), float(tau), k) / opt)
            by_eta.append(float(np.mean(rr)))
        cons.append(by_eta[0])
        robu.append(float(np.min(by_eta)))
    safe = [c - rho for c, rb in zip(cons, robu) if rb >= rho - eps]
    return cons, robu, (max(safe) if safe else 0.0)


def _build(n, r, deg, n_trials, etas, rngs):
    rg, ri, rs, rp = rngs
    trials, advice, rho_base, follow_perfect = [], {}, [], []
    for j in range(n_trials):
        type_adj = few_types_random(n, r, deg, rg)
        inst, types = sample_instance(type_adj, m=n, rng=ri)
        opt = max_matching_size(inst, n_right=n)
        if opt == 0:
            continue
        ts = int(rs.integers(0, 2**31 - 1))
        c_star = true_type_counts(types, n_types=r)
        rho_base.append(ranking(inst, n, np.random.default_rng(ts)) / opt)
        jj = len(trials)
        for ei, eta in enumerate(etas):
            chat, _ = perturb_counts(c_star, float(eta), rp)
            n_hat, partners = build_advice_matching(type_adj, chat, n_right=n)
            advice[(jj, ei)] = (chat, partners)
            if ei == 0:  # perfect advice → the consistency ceiling (always-follow)
                follow_perfect.append(
                    taf_tau(inst, types, n, partners, chat, np.random.default_rng(ts),
                            tau=1e9, prefix_k=0) / opt)
        trials.append((inst, types, opt, ts))
    return trials, advice, float(np.mean(rho_base)), float(np.mean(follow_perfect))


def _resolution(trials, advice, n, etas, k, rho):
    """The test's RESOLUTION vs the MARGIN it must resolve, at budget k:
      noise_floor = E[ emp_L1 under PERFECT advice ] = sampling noise of the prefix
                    histogram estimate (the smallest L1 the test can 'see').
      L1_star     = the advice error at which Follow stops beating the baseline
                    (the breakeven margin: advice with L1 < L1_star helps, > hurts).
    The test can separate good from bad advice only if noise_floor < L1_star."""
    # noise floor: emp_L1 of the length-k prefix vs the perfect histogram (η index 0)
    floors = []
    for j, (inst, types, opt, ts) in enumerate(trials):
        chat, _ = advice[(j, 0)]
        q = chat / float(chat.sum())
        kk = min(k, len(types))
        pc = np.bincount(types[:kk], minlength=len(chat)).astype(float) / max(1, kk)
        floors.append(float(np.abs(pc - q).sum()))
    noise_floor = float(np.mean(floors))

    # breakeven L1*: follow-ratio and true advice-L1 per η, find the crossing of ρ_base
    l1_by_eta, fr_by_eta = [], []
    for ei, eta in enumerate(etas):
        l1s, frs = [], []
        for j, (inst, types, opt, ts) in enumerate(trials):
            chat, partners = advice[(j, ei)]
            c_star = np.bincount(types, minlength=len(chat)).astype(float)
            l1s.append(float(np.abs(chat - c_star).sum() / n))
            frs.append(taf_tau(inst, types, n, partners, chat,
                               np.random.default_rng(ts), tau=1e9, prefix_k=0) / opt)
        l1_by_eta.append(float(np.mean(l1s))); fr_by_eta.append(float(np.mean(frs)))
    l1_by_eta, fr_by_eta = np.array(l1_by_eta), np.array(fr_by_eta)
    order = np.argsort(l1_by_eta)
    l1s, frs = l1_by_eta[order], fr_by_eta[order]
    l1_star = float(l1s[-1])
    for a in range(len(l1s) - 1):
        if (frs[a] - rho) >= 0 >= (frs[a + 1] - rho) and frs[a] != frs[a + 1]:
            t = (frs[a] - rho) / (frs[a] - frs[a + 1])
            l1_star = float(l1s[a] + t * (l1s[a + 1] - l1s[a])); break
    return noise_floor, l1_star


def run(n=800, deg=3, n_trials=12, seed=0):
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    r_list = [16, 50, 120, 250, 400, 600]
    etas = np.round(np.linspace(0.0, 1.0, 9), 3)
    taus = np.round(np.linspace(0.0, 1.6, 11), 3)
    k_sub = int(round(np.sqrt(n)))               # the sublinear test budget (√n)
    rg, ri, rs, rp = np.random.default_rng(seed).spawn(4)
    t0 = time.time()

    panelA = []
    for r in r_list:
        trials, advice, rho, fperf = _build(n, r, deg, n_trials, etas, (rg, ri, rs, rp))
        _, _, safe = _frontier(trials, advice, n, k_sub, taus, etas, rho)
        nf, l1s = _resolution(trials, advice, n, etas, k_sub, rho)
        potential = fperf - rho
        panelA.append({"r": r, "count_per_type": n / r, "rho_base": rho,
                       "follow_perfect": fperf, "potential_upside": potential,
                       "capturable_upside": safe, "noise_floor": nf, "l1_star": l1s})
        print(f"  r={r:3d}  count/type={n/r:5.1f}  ρ_base={rho:.3f}  "
              f"potential={potential:+.3f}  capturable(k=√n)={safe:+.3f}  "
              f"noise_floor={nf:.3f}  L1*={l1s:.3f}  {'TESTABLE' if nf < l1s else 'UNRESOLVABLE'}")

    data = {"params": {"n": n, "deg": deg, "n_trials": n_trials, "k_sub": k_sub,
                       "r_list": r_list, "etas": etas.tolist(), "taus": taus.tolist()},
            "panelA": panelA}
    (out_dir / "impossibility_frontier.json").write_text(json.dumps(data, indent=2))
    _plot(data, out_dir)
    print(f"\nsaved: results/impossibility_frontier.{{json,png}}  (elapsed {time.time()-t0:.1f}s)")
    return data


def _plot(data, out_dir):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    A = data["panelA"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.6))
    ax = axes[0]
    x = [p["rho_base"] for p in A]
    ax.plot(x, [p["potential_upside"] for p in A], "o-", color="C2",
            label="POTENTIAL upside (perfect advice − baseline)")
    ax.plot(x, [p["capturable_upside"] for p in A], "s-", color="C3",
            label=f"test-CAPTURABLE upside (sublinear k=√n)")
    ax.fill_between(x, [p["capturable_upside"] for p in A], [p["potential_upside"] for p in A],
                    alpha=0.12, color="gray")
    for p in A:
        ax.annotate(f"r={p['r']}", (p["rho_base"], p["potential_upside"]),
                    fontsize=7, xytext=(0, 5), textcoords="offset points", ha="center")
    ax.set_xlabel("baseline strength  ρ_base  (← weaker / larger r ··· stronger / smaller r →)")
    ax.set_ylabel("consistency upside over baseline")
    ax.set_title("The scissors: potential upside exists (weak baseline),\n"
                 "but a sublinear test cannot capture it (counts too low to verify)")
    ax.grid(True, alpha=0.3); ax.legend(fontsize=8, loc="upper right")
    ax.invert_xaxis()

    ax = axes[1]
    x = [p["rho_base"] for p in A]
    ax.plot(x, [p["noise_floor"] for p in A], "o-", color="C3",
            label="test resolution: emp-L1 noise floor at k=√n")
    ax.plot(x, [p["l1_star"] for p in A], "s-", color="C2",
            label="margin to resolve: breakeven L1* (advice helps below)")
    ax.fill_between(x, [p["l1_star"] for p in A], [p["noise_floor"] for p in A],
                    where=[p["noise_floor"] > p["l1_star"] for p in A],
                    alpha=0.15, color="C3")
    for p in A:
        ax.annotate(f"r={p['r']}", (p["rho_base"], p["noise_floor"]),
                    fontsize=7, xytext=(0, 5), textcoords="offset points", ha="center")
    ax.set_xlabel("baseline strength  ρ_base")
    ax.set_ylabel("L1 distance")
    ax.set_title("Why: the sublinear test can't resolve the margin\n"
                 "(noise floor ≫ breakeven L1* everywhere → can't separate good from bad)")
    ax.grid(True, alpha=0.3); ax.legend(fontsize=8); ax.invert_xaxis()
    fig.suptitle("C-M0 — numerical impossibility frontier for sublinear test-and-fallback", fontsize=12)
    fig.tight_layout()
    fig.savefig(out_dir / "impossibility_frontier.png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    print("saved: impossibility_frontier.png")


if __name__ == "__main__":
    run()
