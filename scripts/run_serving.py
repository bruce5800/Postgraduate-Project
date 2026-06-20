"""Phase 4 — AI inference serving instantiation: capacity vs algorithmic robustness.

Online b-matching: requests (drawn from a Zipfian traffic distribution) are routed
to serving resources of capacity c. The "advice" is a traffic forecast (predicted
request-type histogram); a bad forecast is a stale / drifted one.

Domain finding — "capacity and forecasts are substitutes, and capacity is the
safe one." As resource capacity c grows, the forecast-FREE greedy baseline
approaches optimal (capacity buys robustness for free). So a good forecast's
upside is small and concentrated at tight capacity, while a stale forecast's
downside is large and *worsens* with capacity (in competitive-ratio terms, since
OPT grows but the wrong routing does not). The adaptive test-and-fallback stays
robust at every capacity (within ~0.05 of the forecast-free baseline), so its
protective value — the gap to blind trust — actually GROWS with capacity. Net: in
a well-provisioned serving system, a forecast-free policy is already near-optimal,
and the real risk is a routing layer that blindly trusts a stale forecast — which
is exactly what the test guards against, most valuably when capacity is ample.

Outputs:
  results/serving.json
  results/serving_cliff.png      goodput vs capacity under a garbage forecast
  results/serving_envelope.png   goodput vs forecast error, at low vs high capacity
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.serving import serving_topology
from iid_sampler import sample_instance
from optimal import max_b_matching_size
from algorithms.capacity import (
    greedy_with_capacity, build_advice_b_matching,
    follow_prediction_capacity, test_and_match_capacity,
)
from predictions.type_advice import true_type_counts, perturb_counts

NRES, NTYPES, DEG, M = 200, 40, 8, 800
CAPS = [1, 2, 4, 8, 16]
ETAS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]


def cell(cap, eta, n_trials, seed):
    rg, ri, rp, rs = np.random.default_rng(seed).spawn(4)
    blind, adapt, base, l1s = [], [], [], []
    for _ in range(n_trials):
        type_adj, p = serving_topology(NRES, NTYPES, DEG, rg)
        inst, types = sample_instance(type_adj, m=M, rng=ri, p=p)
        opt = max_b_matching_size(types, type_adj, NRES, cap)
        if opt == 0:
            continue
        c_star = true_type_counts(types, NTYPES)
        chat, l1 = perturb_counts(c_star, eta, rp, concentration=0.3)
        n_hat, partners = build_advice_b_matching(type_adj, chat, NRES, cap)
        s = int(rs.integers(0, 2**31 - 1))
        blind.append(follow_prediction_capacity(inst, types, NRES, partners, chat, cap) / opt)
        tm, _ = test_and_match_capacity(inst, types, NRES, partners, chat, n_hat, cap,
                                        rng=np.random.default_rng(s), variant="bem",
                                        prefix_k=120)
        adapt.append(tm / opt)
        rank = np.empty(NRES, dtype=np.int64)
        perm = np.random.default_rng(s).permutation(NRES); rank[perm] = np.arange(NRES)
        base.append(greedy_with_capacity(inst, rank, NRES, cap) / opt)
        l1s.append(l1)
    return {"blind": float(np.mean(blind)), "adapt": float(np.mean(adapt)),
            "base": float(np.mean(base)), "l1": float(np.mean(l1s))}


def main(n_trials=25, seed=0):
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    t0 = time.time()
    grid = {}
    for cap in CAPS:
        grid[cap] = {}
        for eta in ETAS:
            grid[cap][eta] = cell(cap, eta, n_trials, seed)
        g = grid[cap]
        print(f"cap={cap:2d}  garbage(η=1): blind={g[1.0]['blind']:.3f} "
              f"adapt={g[1.0]['adapt']:.3f} base={g[1.0]['base']:.3f}  "
              f"robustness-value(adapt-blind)={g[1.0]['adapt']-g[1.0]['blind']:+.3f}")

    data = {"caps": CAPS, "etas": ETAS, "grid": {str(c): grid[c] for c in CAPS},
            "params": {"n_resources": NRES, "n_types": NTYPES, "deg": DEG, "m": M}}
    (out_dir / "serving.json").write_text(json.dumps(data, indent=2,
        default=lambda o: {str(k): v for k, v in o.items()} if isinstance(o, dict) else o))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        # Cliff: goodput vs capacity, garbage forecast (η=1).
        fig, ax = plt.subplots(figsize=(9, 5.5))
        blind = [grid[c][1.0]["blind"] for c in CAPS]
        adapt = [grid[c][1.0]["adapt"] for c in CAPS]
        base = [grid[c][1.0]["base"] for c in CAPS]
        ax.plot(CAPS, blind, "o--", color="C3", label="blindly follow forecast")
        ax.plot(CAPS, adapt, "s-", color="C2", label="TestAndMatch (adaptive)")
        ax.plot(CAPS, base, ":", color="gray", label="forecast-free baseline")
        ax.set_xscale("log", base=2)
        ax.set_xticks(CAPS); ax.set_xticklabels(CAPS)
        ax.set_xlabel("resource capacity c (requests served per resource)")
        ax.set_ylabel("goodput (served / best possible)")
        ax.set_title("Capacity is the safe substitute — forecast-free greedy → optimal as\n"
                     "capacity grows, while trusting a stale forecast stays catastrophic")
        ax.grid(True, alpha=0.3); ax.legend(loc="lower right")
        fig.savefig(out_dir / "serving_cliff.png", dpi=120, bbox_inches="tight")
        plt.close(fig)

        # Envelope at low vs high capacity.
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
        for ax, cap in zip(axes, [1, 8]):
            l1 = [grid[cap][e]["l1"] for e in ETAS]
            ax.plot(l1, [grid[cap][e]["blind"] for e in ETAS], "o--", color="C3", label="blind follow")
            ax.plot(l1, [grid[cap][e]["adapt"] for e in ETAS], "s-", color="C2", label="adaptive")
            ax.plot(l1, [grid[cap][e]["base"] for e in ETAS], ":", color="gray", label="baseline")
            ax.set_title(f"capacity c = {cap}")
            ax.set_xlabel("forecast error L1(p, q)"); ax.grid(True, alpha=0.3)
        axes[0].set_ylabel("goodput (served / best possible)"); axes[0].legend(loc="lower left")
        fig.suptitle("Forecast-error envelope: trusting a stale forecast crashes goodput at both\n"
                     "capacities — and DEEPER at ample capacity (c=8); the adaptive test stays flat")
        fig.savefig(out_dir / "serving_envelope.png", dpi=120, bbox_inches="tight")
        plt.close(fig)
        print("\nsaved: serving_cliff.png, serving_envelope.png")
    except ImportError:
        print("(matplotlib unavailable)")

    print(f"saved: results/serving.json  (elapsed {time.time()-t0:.1f}s)")


if __name__ == "__main__":
    main()
