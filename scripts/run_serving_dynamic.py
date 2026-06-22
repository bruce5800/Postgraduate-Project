"""Phase 4 (deepened) — DYNAMIC serving: requests occupy a slot for a real
service time, then free it. Real Azure LLM trace: real arrival timestamps + real
service durations (generated-token counts). This drops the static b-matching's
unrealistic "all requests concurrent forever" assumption.

Metric: goodput = served / total (admission rate). Policies:
  - least_loaded   : forecast-free real load balancer (uses all capable resources)
  - blind_forecast : route only to forecast-preferred resources (fragile)
  - adaptive       : prefix-test, then follow forecast or switch to least_loaded

Finding to confirm under dynamics: a forecast-free load balancer is robust;
blindly following a stale traffic forecast degrades as the forecast diverges, and
the adaptive test recovers the robustness — now with real occupy/release dynamics.

Outputs: results/serving_dynamic.json, results/serving_dynamic.png
"""
from __future__ import annotations
import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.serving import serving_topology
from algorithms.capacity import build_advice_b_matching
from algorithms.dynamic import (
    served_least_loaded, served_blind_forecast, served_adaptive,
)

TRACE = Path(__file__).resolve().parent.parent / "data" / "trace" / "azure_llm"
NB, N_RES, DEG, TOK = 40, 100, 10, 0.10
CAPS = [3, 6, 12]


def _load(path):
    ts, ctx, gen = [], [], []
    for r in csv.DictReader(open(path)):
        ts.append(r["TIMESTAMP"]); ctx.append(int(r["ContextTokens"])); gen.append(int(r["GeneratedTokens"]))
    t0 = datetime.fromisoformat(ts[0][:26])
    sec = np.array([(datetime.fromisoformat(t[:26]) - t0).total_seconds() for t in ts])
    return sec, np.array(ctx), np.array(gen)


def run(n_trials=8, seed=0):
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    sec, ctx, gen = _load(TRACE / "AzureLLMInferenceTrace_conv.csv")
    _, ctx_code, _ = _load(TRACE / "AzureLLMInferenceTrace_code.csv")
    edges = np.unique(np.geomspace(max(1, int(ctx.min())), int(ctx.max()), NB + 1))
    nb = len(edges) - 1
    bk = lambda a: np.clip(np.digitize(a, edges[1:-1]), 0, nb - 1)

    half = len(sec) // 2
    arr_t = sec[half:] - sec[half]
    arr_l = bk(ctx[half:])
    arr_dur = gen[half:].astype(float) * TOK
    m = len(arr_l)

    def hist(a):
        h = np.bincount(bk(a), minlength=nb).astype(float); return h / h.sum()
    p_live = np.bincount(arr_l, minlength=nb).astype(float); p_live /= p_live.sum()
    forecasts = {
        "perfect": p_live,
        "same workload\n(conv, older half)": hist(ctx[:half]),
        "wrong workload\n(code trace)": hist(ctx_code),
    }
    drift = {lab: float(np.abs(p_live - q).sum()) for lab, q in forecasts.items()}
    span = arr_t[-1]
    print(f"dynamic serving: {m} real arrivals, span={span:.0f}s, median dur={np.median(arr_dur):.1f}")
    for lab, l1 in drift.items():
        print(f"  forecast '{lab.splitlines()[0]}': real L1={l1:.3f}")

    rg, rs = np.random.default_rng(seed).spawn(2)
    res = {"m": m, "caps": CAPS, "drift": drift, "by_cap": {}}
    t0 = time.time()
    for cap in CAPS:
        rho = arr_dur.sum() / (span * N_RES * cap)
        res["by_cap"][cap] = {"offered_load": float(rho)}
        for lab, q in forecasts.items():
            chat = np.round(m * q)
            ll, bf, ad = [], [], []
            for _ in range(n_trials):
                type_adj, _ = serving_topology(N_RES, nb, DEG, rg)
                n_hat, partners = build_advice_b_matching(type_adj, chat, N_RES, cap)
                preferred = [list(dict.fromkeys(p)) for p in partners]
                s = int(rs.integers(0, 2**31 - 1))
                ll.append(served_least_loaded(arr_t, arr_l, arr_dur, type_adj, N_RES, cap, np.random.default_rng(s)) / m)
                bf.append(served_blind_forecast(arr_t, arr_l, arr_dur, type_adj, preferred, N_RES, cap, np.random.default_rng(s)) / m)
                a, _ = served_adaptive(arr_t, arr_l, arr_dur, type_adj, preferred, q, N_RES, cap,
                                       np.random.default_rng(s), prefix_k=max(1, m // 10))
                ad.append(a / m)
            res["by_cap"][cap][lab] = {"l1": drift[lab], "least_loaded": float(np.mean(ll)),
                                       "blind": float(np.mean(bf)), "adaptive": float(np.mean(ad))}
            r = res["by_cap"][cap][lab]
            print(f"  cap={cap:2d} ρ={rho:.2f} {lab.splitlines()[0]:>24} (L1={r['l1']:.2f}): "
                  f"least_loaded={r['least_loaded']:.3f} blind={r['blind']:.3f} adaptive={r['adaptive']:.3f}")

    (out_dir / "serving_dynamic.json").write_text(json.dumps(res, indent=2))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        labels = list(forecasts.keys())
        order = sorted(labels, key=lambda l: drift[l])
        x = [drift[l] for l in order]
        fig, axes = plt.subplots(1, len(CAPS), figsize=(5.2 * len(CAPS), 5), sharey=True)
        for ax, cap in zip(axes, CAPS):
            d = res["by_cap"][cap]
            ax.plot(x, [d[l]["blind"] for l in order], "o--", color="C3", label="blindly follow forecast")
            ax.plot(x, [d[l]["adaptive"] for l in order], "s-", color="C2", label="adaptive (test + fall back)")
            ax.plot(x, [d[l]["least_loaded"] for l in order], "^:", color="gray", label="least-loaded (forecast-free LB)")
            ax.set_xlabel("real forecast error L1")
            ax.set_title(f"capacity c = {cap}  (offered load ρ≈{d['offered_load']:.2f})")
            ax.grid(True, alpha=0.3)
        axes[0].set_ylabel("goodput (served / total)")
        axes[0].legend(loc="lower left", fontsize=9)
        fig.suptitle("Dynamic serving (real LLM timestamps + service times): a forecast-free load\n"
                     "balancer is robust; blindly following a stale forecast degrades; the test recovers it")
        fig.savefig(out_dir / "serving_dynamic.png", dpi=120, bbox_inches="tight")
        plt.close(fig)
        print("\nsaved: serving_dynamic.png")
    except ImportError:
        print("(matplotlib unavailable)")
    print(f"saved: results/serving_dynamic.json  (elapsed {time.time()-t0:.1f}s)")


if __name__ == "__main__":
    run()
