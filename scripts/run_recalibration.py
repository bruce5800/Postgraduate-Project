"""Phase 3c follow-up: recalibrating the acceptance threshold to the MEASURED
baseline instead of the worst-case β.

PHASE3C_REPORT §5 found that the Choo/BEM acceptance threshold τ is calibrated
for the worst-case baseline β≈0.696, but on average-case instances the baseline
(Ranking) is ≈0.99 — so the threshold is too lenient: it accepts mildly-bad
advice an oracle would reject, and a more-accurate test only follows that
miscalibrated threshold more faithfully (larger prefix → worse outcome).

The fix: estimate the baseline's empirical competitive ratio β̂ from a small
calibration sample and use β̂ in the Choo threshold τ = 2(n̂/n − β̂). The
empirical break-even (where following advice stops beating the baseline) is
L1* ≈ 2(n̂/n − β̂·n*/n), so β̂ makes τ track the real break-even instead of the
worst-case one.

This experiment compares the worst-case threshold (β=0.696) against the
recalibrated one (β=β̂) on:
  (1) the borderline prefix sweep — does recalibration kill the pathology?
  (2) the full L1 envelope — does it stay robust and not lose anything?

Outputs:
  results/recalibration.json
  results/recalibration_prefix.png
  results/recalibration_envelope.png
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.synthetic import few_types_bipartite
from iid_sampler import sample_instance
from optimal import max_matching_size
from algorithms.ranking import ranking
from algorithms.test_and_match import test_and_match
from predictions.type_advice import (
    true_type_counts, build_advice_matching, perturb_counts,
)

N = 1200
R = 8
VARIANT = "choo"   # τ = 2(n̂/n − β): the direct break-even form, easiest to recalibrate


def calibrate_beta(n_samples=15, seed=100):
    """β̂ = mean empirical Ranking competitive ratio on the instance family."""
    rg, ri, rj = np.random.default_rng(seed).spawn(3)
    ratios = []
    for _ in range(n_samples):
        type_adj = few_types_bipartite(N, R, rg)
        inst, types = sample_instance(type_adj, m=N, rng=ri)
        opt = max_matching_size(inst, N)
        if opt:
            ratios.append(ranking(inst, N, rj) / opt)
    return float(np.mean(ratios))


def _trial(type_adj, inst, types, opt, eta, rng_pert, betas, prefix_k, s):
    """Run both β settings on ONE shared instance/advice (HK paid once)."""
    c_star = true_type_counts(types, R)
    chat, l1 = perturb_counts(c_star, eta, rng_pert)
    n_hat, partners = build_advice_matching(type_adj, chat, N)
    rk = ranking(inst, N, np.random.default_rng(s)) / opt
    out = {"l1": l1, "ranking": rk}
    for name, beta in betas.items():
        size, info = test_and_match(inst, types, N, partners, chat, n_hat,
                                    rng=np.random.default_rng(s), variant=VARIANT,
                                    beta=beta, prefix_k=prefix_k)
        ratio = size / opt
        # oracle: should we have followed?  (following beats baseline on this instance)
        # we approximate "would-follow ratio" by n_hat - n*l1/2 over opt
        follow_est = max(0.0, (n_hat - N * l1 / 2.0)) / opt
        good = follow_est > rk
        out[name] = {"ratio": ratio, "followed": info["followed"],
                     "misjudge": 0.0 if info["followed"] == good else 1.0}
    return out


def prefix_sweep(betas, eta=0.15, n_trials=30, seed=1):
    ks = [25, 100, 400, 1000]
    rg, ri, rp, rs = np.random.default_rng(seed).spawn(4)
    rows = []
    for k in ks:
        acc = {name: {"ratio": [], "misjudge": []} for name in betas}
        for _ in range(n_trials):
            type_adj = few_types_bipartite(N, R, rg)
            inst, types = sample_instance(type_adj, m=N, rng=ri)
            opt = max_matching_size(inst, N)
            if not opt:
                continue
            s = int(rs.integers(0, 2**31 - 1))
            t = _trial(type_adj, inst, types, opt, eta, rp, betas, k, s)
            for name in betas:
                acc[name]["ratio"].append(t[name]["ratio"])
                acc[name]["misjudge"].append(t[name]["misjudge"])
        row = {"k": k}
        for name in betas:
            row[name] = {"ratio": float(np.mean(acc[name]["ratio"])),
                         "misjudge": float(np.mean(acc[name]["misjudge"]))}
        rows.append(row)
        msg = "  ".join(f"{name}: r={row[name]['ratio']:.3f} mis={row[name]['misjudge']:.2f}"
                        for name in betas)
        print(f"  k={k:4d}  {msg}")
    return rows


def envelope(betas, n_trials=25, prefix_k=200, seed=2):
    etas = np.round(np.arange(0.0, 1.01, 0.1), 2)
    rg, ri, rp, rs = np.random.default_rng(seed).spawn(4)
    rows = []
    for eta in etas:
        acc = {name: [] for name in betas}
        l1s = []
        for _ in range(n_trials):
            type_adj = few_types_bipartite(N, R, rg)
            inst, types = sample_instance(type_adj, m=N, rng=ri)
            opt = max_matching_size(inst, N)
            if not opt:
                continue
            s = int(rs.integers(0, 2**31 - 1))
            t = _trial(type_adj, inst, types, opt, float(eta), rp, betas, prefix_k, s)
            l1s.append(t["l1"])
            for name in betas:
                acc[name].append(t[name]["ratio"])
        row = {"eta": float(eta), "l1": float(np.mean(l1s))}
        for name in betas:
            row[name] = float(np.mean(acc[name]))
        rows.append(row)
        print(f"  η={eta:.1f} L1={row['l1']:.3f}  " +
              "  ".join(f"{name}={row[name]:.3f}" for name in betas))
    return rows


def main():
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    t0 = time.time()

    beta_hat = calibrate_beta()
    print(f"Calibrated baseline β̂ (mean Ranking ratio) = {beta_hat:.3f}\n")
    betas = {"worstcase(β=0.696)": 0.696, f"recal(β̂={beta_hat:.2f})": beta_hat}

    print("=== Borderline prefix sweep (η=0.15): worst-case vs recalibrated τ ===")
    pre = prefix_sweep(betas)
    print("\n=== L1 envelope: worst-case vs recalibrated τ ===")
    env = envelope(betas)

    names = list(betas.keys())
    data = {"beta_hat": beta_hat, "names": names, "prefix": pre, "envelope": env}
    (out_dir / "recalibration.json").write_text(json.dumps(data, indent=2))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        # Prefix: misjudgement vs k for both thresholds.
        ks = [p["k"] for p in pre]
        fig, ax = plt.subplots(figsize=(9, 5.5))
        ax.plot(ks, [p[names[0]]["misjudge"] for p in pre], "o--", color="C3",
                label=names[0] + " — misjudgement")
        ax.plot(ks, [p[names[1]]["misjudge"] for p in pre], "s-", color="C2",
                label=names[1] + " — misjudgement")
        ax.set_xscale("log")
        ax.set_xlabel("prefix / testing size k")
        ax.set_ylabel("misjudgement rate (vs empirical oracle)")
        ax.set_title("Recalibrating τ to the measured baseline removes the\n"
                     "'larger prefix → worse decision' pathology (borderline η=0.15)")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.savefig(out_dir / "recalibration_prefix.png", dpi=120, bbox_inches="tight")
        plt.close(fig)

        # Envelope: ratio vs L1 for both thresholds.
        l1 = [e["l1"] for e in env]
        fig, ax = plt.subplots(figsize=(9, 5.5))
        ax.plot(l1, [e[names[0]] for e in env], "o--", color="C3", label=names[0])
        ax.plot(l1, [e[names[1]] for e in env], "s-", color="C2", label=names[1])
        ax.set_xlabel("advice error L1(p, q)")
        ax.set_ylabel("competitive ratio (alg / OPT)")
        ax.set_title("Both thresholds stay robust; the recalibrated one also avoids\n"
                     "following mildly-bad advice in the L1≈0.1–0.3 confusion zone")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="lower left")
        fig.savefig(out_dir / "recalibration_envelope.png", dpi=120, bbox_inches="tight")
        plt.close(fig)
        print("\nsaved: recalibration_prefix.png, recalibration_envelope.png")
    except ImportError:
        print("(matplotlib unavailable)")

    print(f"saved: results/recalibration.json  (elapsed {time.time()-t0:.1f}s)")


if __name__ == "__main__":
    main()
