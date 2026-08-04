"""E1: DirectionalTest-and-Match (test the payoff, not the prediction) on the
benchmark instances, head-to-head against the empirical-L1 threshold rules.

Three experiments, all on the few-types family the test-and-fallback chapters use:

  1. envelope   — ratio vs advice error L1(p,q) at k=200, comparing
                  FollowPrediction / TestAndMatch (Choo, worst-case beta) /
                  TestAndMatch (Choo, recalibrated beta-hat) / Directional /
                  Ranking floor, plus per-rule misjudgement rates.
                  Expectation: Directional tracks the upper envelope WITHOUT any
                  calibration constant — where worst-case tau over-accepts
                  (Fig 6.2 pathology) and recalibrated tau over-rejects
                  (the resolution limit), the payoff test does neither.
  2. prefix     — the Fig-6.2 pathology probe: ratio & misjudgement vs prefix
                  size k at borderline advice (eta=0.15). Expectation: the
                  "larger test, worse decision" pathology is absent for the
                  payoff rule (misjudgement flat / falling in k).
  3. r_sweep    — the budget-stakes wall made visible on the benchmark
                  generator: fix k=200, grow the number of types r (8 -> 512).
                  The plug-in L1 saturates (blind), so any L1 threshold must
                  eventually always-accept or always-reject; the payoff test
                  keeps making the right call at both good and bad advice.

Outputs: results/directional_test.json + directional_{envelope,prefix,rsweep}.png
Seeded and paired (same instance and shared algorithm seed per comparison).
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
from algorithms.test_and_match import (
    follow_prediction, test_and_match, directional_test_and_match,
)
from predictions.type_advice import (
    true_type_counts, build_advice_matching, perturb_counts,
)


def calibrate_beta(n, r, rng, n_trials=8):
    """Measured advice-free baseline ratio beta-hat for this family (as in
    scripts/run_recalibration.py)."""
    vals = []
    for _ in range(n_trials):
        type_adj = few_types_bipartite(n, r, rng)
        instance_adj, _ = sample_instance(type_adj, m=n, rng=rng)
        opt = max_matching_size(instance_adj, n_right=n)
        if opt:
            vals.append(ranking(instance_adj, n, rng) / opt)
    return float(np.mean(vals))


def one_trial(n, r, eta, k, beta_hat, rngs):
    """Run every algorithm on one paired instance. Returns dict of ratios/info."""
    rng_graph, rng_inst, rng_pert, rng_seed = rngs
    type_adj = few_types_bipartite(n, r, rng_graph)
    instance_adj, types = sample_instance(type_adj, m=n, rng=rng_inst)
    opt = max_matching_size(instance_adj, n_right=n)
    if opt == 0:
        return None
    c_star = true_type_counts(types, n_types=r)
    chat, l1 = perturb_counts(c_star, float(eta), rng_pert)
    n_hat, partners = build_advice_matching(type_adj, chat, n_right=n)
    s = int(rng_seed.integers(0, 2**31 - 1))

    f = follow_prediction(instance_adj, types, n, partners, chat) / opt
    rk = ranking(instance_adj, n, np.random.default_rng(s)) / opt
    good = f > rk

    out = {"l1": l1, "follow": f, "ranking": rk}
    wc, iwc = test_and_match(instance_adj, types, n, partners, chat, n_hat,
                             rng=np.random.default_rng(s), variant="choo",
                             prefix_k=k)
    rc, irc = test_and_match(instance_adj, types, n, partners, chat, n_hat,
                             rng=np.random.default_rng(s), variant="choo",
                             beta=beta_hat, prefix_k=k)
    dr, idr = directional_test_and_match(type_adj, instance_adj, types, n,
                                         partners, chat,
                                         rng=np.random.default_rng(s),
                                         prefix_k=k)
    out.update(choo=wc / opt, recal=rc / opt, directional=dr / opt,
               mis_choo=float(iwc["followed"] != good),
               mis_recal=float(irc["followed"] != good),
               mis_dir=float(idr["followed"] != good),
               emp_l1=iwc["emp_l1"], fol_dir=float(idr["followed"]))
    return out


def agg(rows, keys):
    out = {}
    for k in keys:
        vals = [r[k] for r in rows if r.get(k) is not None]
        out[k] = float(np.mean(vals)) if vals else None
    return out


KEYS = ["l1", "follow", "ranking", "choo", "recal", "directional",
        "mis_choo", "mis_recal", "mis_dir", "emp_l1", "fol_dir"]


def envelope(n=2000, r=8, k=200, n_trials=30, seed=0):
    rngs = np.random.default_rng(seed).spawn(4)
    beta_hat = calibrate_beta(n, r, np.random.default_rng(seed + 999))
    print(f"  beta_hat (measured baseline) = {beta_hat:.3f}")
    out = []
    for eta in np.round(np.arange(0.0, 1.01, 0.1), 2):
        rows = [t for t in (one_trial(n, r, eta, k, beta_hat, rngs)
                            for _ in range(n_trials)) if t]
        a = agg(rows, KEYS)
        a["eta"] = float(eta)
        out.append(a)
        print(f"  η={eta:.1f} L1={a['l1']:.3f}  follow={a['follow']:.3f} "
              f"choo={a['choo']:.3f} recal={a['recal']:.3f} "
              f"dir={a['directional']:.3f} rank={a['ranking']:.3f}  "
              f"mis(choo/recal/dir)={a['mis_choo']:.2f}/{a['mis_recal']:.2f}/"
              f"{a['mis_dir']:.2f}")
    return {"beta_hat": beta_hat, "rows": out}


def prefix_sweep(n=2000, r=8, eta=0.15, n_trials=30, seed=1):
    rngs = np.random.default_rng(seed).spawn(4)
    beta_hat = calibrate_beta(n, r, np.random.default_rng(seed + 999))
    out = []
    for k in [25, 50, 100, 200, 400, 800]:
        rows = [t for t in (one_trial(n, r, eta, k, beta_hat, rngs)
                            for _ in range(n_trials)) if t]
        a = agg(rows, KEYS)
        a["k"] = k
        out.append(a)
        print(f"  k={k:4d}  choo={a['choo']:.3f} recal={a['recal']:.3f} "
              f"dir={a['directional']:.3f}  mis={a['mis_choo']:.2f}/"
              f"{a['mis_recal']:.2f}/{a['mis_dir']:.2f}")
    return {"beta_hat": beta_hat, "eta": eta, "rows": out}


def r_sweep(n=2000, k=200, n_trials=30, seed=2):
    out = []
    for r in [8, 32, 128, 512]:
        beta_hat = calibrate_beta(n, r, np.random.default_rng(seed + r))
        for eta in [0.1, 0.9]:
            rngs = np.random.default_rng(seed * 1000 + r).spawn(4)
            rows = [t for t in (one_trial(n, r, eta, k, beta_hat, rngs)
                                for _ in range(n_trials)) if t]
            a = agg(rows, KEYS)
            a.update(r=r, eta=eta, beta_hat=beta_hat)
            out.append(a)
            el = a["emp_l1"] if a["emp_l1"] is not None else float("nan")
            print(f"  r={r:4d} η={eta}  true L1={a['l1']:.3f} "
                  f"emp_l1={el:.3f}  follow={a['follow']:.3f} "
                  f"choo={a['choo']:.3f} recal={a['recal']:.3f} "
                  f"dir={a['directional']:.3f} rank={a['ranking']:.3f}")
    return out


def main():
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    t0 = time.time()

    print("=== 1/3 envelope (ratio vs L1, k=200) ===")
    env = envelope()
    print("=== 2/3 prefix sweep (borderline η=0.15) ===")
    pre = prefix_sweep()
    print("=== 3/3 r sweep (the wall at k=200) ===")
    rsw = r_sweep()

    data = {"envelope": env, "prefix_sweep": pre, "r_sweep": rsw}
    (out_dir / "directional_test.json").write_text(json.dumps(data, indent=2))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        rows = env["rows"]
        l1 = [e["l1"] for e in rows]
        fig, ax = plt.subplots(figsize=(9, 5.5))
        ax.plot(l1, [e["follow"] for e in rows], "o--", color="C3",
                label="FollowPrediction (blind)")
        ax.plot(l1, [e["choo"] for e in rows], "^-", color="C0",
                label="TestAndMatch (worst-case τ)")
        ax.plot(l1, [e["recal"] for e in rows], "v-", color="C4",
                label="TestAndMatch (recalibrated τ̂)")
        ax.plot(l1, [e["directional"] for e in rows], "s-", color="C2", lw=2.2,
                label="Directional (payoff test, no constants)")
        ax.plot(l1, [e["ranking"] for e in rows], ":", color="gray",
                label="Ranking (floor)")
        ax.set_xlabel("advice error  L1(p, q)")
        ax.set_ylabel("competitive ratio")
        ax.set_title("Testing the payoff keeps the upper envelope without any "
                     "calibration constant")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="lower left", fontsize=9)
        fig.savefig(out_dir / "directional_envelope.png", dpi=120,
                    bbox_inches="tight")
        plt.close(fig)

        rows = pre["rows"]
        ks = [e["k"] for e in rows]
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))
        for key, c, lbl in [("choo", "C0", "worst-case τ"),
                            ("recal", "C4", "recalibrated τ̂"),
                            ("directional", "C2", "directional")]:
            ax1.plot(ks, [e[key] for e in rows], "o-", color=c, label=lbl)
            ax2.plot(ks, [e["mis_" + ("dir" if key == "directional" else key)]
                          for e in rows], "o-", color=c, label=lbl)
        ax1.set_xscale("log"); ax2.set_xscale("log")
        ax1.set_xlabel("prefix size k"); ax2.set_xlabel("prefix size k")
        ax1.set_ylabel("competitive ratio")
        ax2.set_ylabel("misjudgement rate")
        ax1.grid(True, alpha=0.3); ax2.grid(True, alpha=0.3)
        ax1.legend(fontsize=9)
        fig.suptitle("Borderline advice (η=0.15): a more accurate payoff test "
                     "never makes the worse decision")
        fig.savefig(out_dir / "directional_prefix.png", dpi=120,
                    bbox_inches="tight")
        plt.close(fig)

        fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
        for ax, eta, ttl in [(axes[0], 0.1, "good advice (η=0.1): capture"),
                             (axes[1], 0.9, "bad advice (η=0.9): safety")]:
            rows = [e for e in rsw if e["eta"] == eta]
            rs = [e["r"] for e in rows]
            ax.plot(rs, [e["follow"] for e in rows], "o--", color="C3",
                    label="FollowPrediction")
            ax.plot(rs, [e["choo"] for e in rows], "^-", color="C0",
                    label="worst-case τ")
            ax.plot(rs, [e["recal"] for e in rows], "v-", color="C4",
                    label="recalibrated τ̂")
            ax.plot(rs, [e["directional"] for e in rows], "s-", color="C2",
                    lw=2.2, label="directional")
            ax.plot(rs, [e["ranking"] for e in rows], ":", color="gray",
                    label="Ranking floor")
            ax.set_xscale("log", base=2)
            ax.set_xlabel("number of types r  (k=200 fixed)")
            ax.set_ylabel("competitive ratio")
            ax.set_title(ttl)
            ax.grid(True, alpha=0.3)
        axes[0].legend(fontsize=8, loc="lower left")
        fig.suptitle("Growing the support blinds the L1 statistic; "
                     "the payoff statistic keeps deciding")
        fig.savefig(out_dir / "directional_rsweep.png", dpi=120,
                    bbox_inches="tight")
        plt.close(fig)
        print("saved: directional_{envelope,prefix,rsweep}.png")
    except ImportError:
        print("(matplotlib unavailable)")

    print(f"saved: results/directional_test.json  (elapsed {time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
