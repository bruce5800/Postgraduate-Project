"""Phase 4 — real trace: forecast STALENESS as a real prediction-error axis.

Workload = real Wikipedia daily pageviews (data/trace/wiki/). The live day's
traffic is the request stream; an EARLIER day's distribution is the "forecast".
Forecast error is therefore real temporal drift — the older the forecast day, the
staler (and more wrong) the forecast. No synthetic perturbation anywhere.

This hardens the Phase 4 finding on real data: blindly trusting a stale traffic
forecast degrades goodput as the forecast ages, while the adaptive test-and-
fallback stays robust at every staleness.

Outputs:
  results/serving_trace.json
  results/serving_trace.png
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.trace import build_trace
from graphs.serving import serving_topology
from iid_sampler import sample_instance
from optimal import max_b_matching_size
from algorithms.capacity import (
    greedy_with_capacity, build_advice_b_matching,
    follow_prediction_capacity, test_and_match_capacity,
)

WIKI = Path(__file__).resolve().parent.parent / "data" / "trace" / "wiki"
LIVE = WIKI / "2024-06-15.json"
FORECASTS = {"1 day": WIKI / "2024-06-14.json",
             "7 days": WIKI / "2024-06-08.json",
             "30 days": WIKI / "2024-05-15.json"}
N_TYPES, N_RES, DEG, M = 500, 300, 10, 3000
CAPS = [2, 8]


def run(n_trials=20, seed=0):
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    types, p_live, forecasts = build_trace(LIVE, FORECASTS, N_TYPES)
    n_types = len(types)
    drift = {lab: l1 for lab, (q, l1) in forecasts.items()}
    print(f"real Wikipedia trace: {n_types} request types (pages)")
    print("real forecast drift L1 by staleness: " +
          ", ".join(f"{lab}={l1:.2f}" for lab, l1 in drift.items()))

    rg, ri, rs = np.random.default_rng(seed).spawn(3)
    results = {"types": n_types, "drift": drift, "caps": CAPS, "M": M, "by_cap": {}}

    t0 = time.time()
    for cap in CAPS:
        results["by_cap"][cap] = {}
        for lab, (q, l1) in forecasts.items():
            chat_dist = q
            blind, adapt, base = [], [], []
            for _ in range(n_trials):
                type_adj, _ = serving_topology(N_RES, n_types, DEG, rg)
                inst, t_arr = sample_instance(type_adj, m=M, rng=ri, p=p_live)
                opt = max_b_matching_size(t_arr, type_adj, N_RES, cap)
                if opt == 0:
                    continue
                chat = np.round(M * chat_dist).astype(np.float64)
                n_hat, partners = build_advice_b_matching(type_adj, chat, N_RES, cap)
                s = int(rs.integers(0, 2**31 - 1))
                blind.append(follow_prediction_capacity(inst, t_arr, N_RES, partners, chat, cap) / opt)
                tm, _ = test_and_match_capacity(inst, t_arr, N_RES, partners, chat, n_hat, cap,
                                                rng=np.random.default_rng(s), variant="bem", prefix_k=400)
                adapt.append(tm / opt)
                rank = np.empty(N_RES, dtype=np.int64)
                perm = np.random.default_rng(s).permutation(N_RES); rank[perm] = np.arange(N_RES)
                base.append(greedy_with_capacity(inst, rank, N_RES, cap) / opt)
            results["by_cap"][cap][lab] = {
                "l1": l1, "blind": float(np.mean(blind)),
                "adapt": float(np.mean(adapt)), "base": float(np.mean(base))}
            r = results["by_cap"][cap][lab]
            print(f"  cap={cap} {lab:>8} stale (L1={l1:.2f}): "
                  f"blind={r['blind']:.3f} adapt={r['adapt']:.3f} base={r['base']:.3f}")

    (out_dir / "serving_trace.json").write_text(json.dumps(results, indent=2))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        labels = list(forecasts.keys())
        x = list(range(len(labels)))
        xt = [f"{lab}\n(drift {drift[lab]:.2f})" for lab in labels]
        fig, axes = plt.subplots(1, len(CAPS), figsize=(6 * len(CAPS), 5), sharey=True)
        if len(CAPS) == 1:
            axes = [axes]
        for ax, cap in zip(axes, CAPS):
            d = results["by_cap"][cap]
            ax.plot(x, [d[l]["blind"] for l in labels], "o--", color="C3", label="blindly follow forecast")
            ax.plot(x, [d[l]["adapt"] for l in labels], "s-", color="C2", label="TestAndMatch (adaptive)")
            ax.plot(x, [d[l]["base"] for l in labels], ":", color="gray", label="forecast-free baseline")
            ax.set_xticks(x); ax.set_xticklabels(xt)
            ax.set_xlabel("forecast staleness (real temporal drift)")
            ax.set_title(f"capacity c = {cap}")
            ax.grid(True, alpha=0.3)
        axes[0].set_ylabel("goodput (served / best possible)")
        axes[0].legend(loc="lower left")
        fig.suptitle("Real Wikipedia traffic: the staler the traffic forecast, the worse blind trust\n"
                     "does — the adaptive test stays robust at every staleness")
        fig.savefig(out_dir / "serving_trace.png", dpi=120, bbox_inches="tight")
        plt.close(fig)
        print("\nsaved: serving_trace.png")
    except ImportError:
        print("(matplotlib unavailable)")
    print(f"saved: results/serving_trace.json  (elapsed {time.time()-t0:.1f}s)")


if __name__ == "__main__":
    run()
