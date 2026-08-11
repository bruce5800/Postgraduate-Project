"""Phase 4 (deepened) — DYNAMIC serving: requests occupy a slot for a real
service time, then free it. Real Azure LLM trace: real arrival timestamps + real
service durations (generated-token counts). This drops the static b-matching's
unrealistic "all requests concurrent forever" assumption.

Metric: competitive ratio = served / OPT, where OPT is the offline optimum of the
same dynamic instance (admit a subset of requests, each held on one compatible
replica for its whole service time, at most `cap` concurrent per replica).

That optimum is NP-hard in general (interval scheduling with machine eligibility),
so we divide by a computable UPPER bound on it: relax the per-replica capacity to a
per-type capacity cap*deg(type). Dropping the requirement that the cap*deg slots sit
on identified replicas can only help the benchmark, so the bound is valid and the
reported ratios are lower bounds on the true competitive ratio. Under the relaxation
the problem decomposes by type into k-track interval scheduling, which the
earliest-end-time greedy solves exactly. A feasible offline assignment gives the
matching lower bound, so the print-out also shows how tight the bracket is.

Policies:
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
import heapq
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


def ktrack_max(starts, ends, k):
    """Max #fixed intervals selectable with <= k simultaneously (exact).

    Earliest-end-time greedy, accepting whenever the interval fits — the classic
    optimal rule for a maximum k-colourable subgraph of an interval graph.
    """
    order = sorted(range(len(starts)), key=lambda i: (ends[i], starts[i]))
    acc_s, acc_e = [], []
    for i in order:
        s, e = starts[i], ends[i]
        events = []
        for a, b in zip(acc_s, acc_e):
            lo, hi = max(a, s), min(b, e)
            if lo < hi:
                events.append((lo, 1)); events.append((hi, -1))
        cover = mx = 0
        for _, d in sorted(events):
            cover += d
            mx = max(mx, cover)
        if mx < k:
            acc_s.append(s); acc_e.append(e)
    return len(acc_s)


def offline_opt_upper(arr_t, arr_l, arr_dur, n_types, deg, cap):
    """Upper bound on the dynamic offline optimum (see module docstring)."""
    ends = arr_t + arr_dur
    total = 0
    for l in range(n_types):
        idx = np.where(arr_l == l)[0]
        if idx.size:
            total += ktrack_max(arr_t[idx], ends[idx], cap * deg)
    return total


def offline_feasible(arr_t, arr_l, arr_dur, type_adj, n_res, cap):
    """A feasible offline assignment (least-loaded), i.e. a lower bound on OPT."""
    free_at = [[] for _ in range(n_res)]
    served = 0
    for t, l, d in zip(arr_t, arr_l, arr_dur):
        best, best_load = -1, cap + 1
        for j in type_adj[l]:
            h = free_at[j]
            while h and h[0] <= t:
                heapq.heappop(h)
            if len(h) < best_load:
                best, best_load = j, len(h)
        if best >= 0 and best_load < cap:
            heapq.heappush(free_at[best], t + d); served += 1
    return served


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
        opt_ub = offline_opt_upper(arr_t, arr_l, arr_dur, nb, DEG, cap)
        opt_lb = offline_feasible(arr_t, arr_l, arr_dur,
                                  serving_topology(N_RES, nb, DEG,
                                                   np.random.default_rng(seed))[0],
                                  N_RES, cap)
        res["by_cap"][cap] = {"offered_load": float(rho), "opt_upper": opt_ub,
                              "opt_lower": opt_lb, "opt_upper_over_m": opt_ub / m}
        print(f"  cap={cap:2d}: offline OPT in [{opt_lb}, {opt_ub}] "
              f"= [{opt_lb/m:.4f}, {opt_ub/m:.4f}] of m  (bracket {100*(opt_ub-opt_lb)/m:.1f}% of m)")
        for lab, q in forecasts.items():
            chat = np.round(m * q)
            ll, bf, ad = [], [], []
            for _ in range(n_trials):
                type_adj, _ = serving_topology(N_RES, nb, DEG, rg)
                n_hat, partners = build_advice_b_matching(type_adj, chat, N_RES, cap)
                preferred = [list(dict.fromkeys(p)) for p in partners]
                s = int(rs.integers(0, 2**31 - 1))
                ll.append(served_least_loaded(arr_t, arr_l, arr_dur, type_adj, N_RES, cap, np.random.default_rng(s)) / opt_ub)
                bf.append(served_blind_forecast(arr_t, arr_l, arr_dur, type_adj, preferred, N_RES, cap, np.random.default_rng(s)) / opt_ub)
                a, _ = served_adaptive(arr_t, arr_l, arr_dur, type_adj, preferred, q, N_RES, cap,
                                       np.random.default_rng(s), prefix_k=max(1, m // 10))
                ad.append(a / opt_ub)
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
        axes[0].set_ylabel("competitive ratio\n(served / offline-optimum bound)")
        axes[0].legend(loc="lower left", fontsize=9)
        fig.suptitle("Dynamic serving (real LLM timestamps + service times): the forecast-free load\n"
                     "balancer is near-optimal; blindly following a stale forecast degrades; the test recovers it",
                     y=1.04)
        fig.tight_layout()
        fig.savefig(out_dir / "serving_dynamic.png", dpi=120, bbox_inches="tight")
        plt.close(fig)
        print("\nsaved: serving_dynamic.png")
    except ImportError:
        print("(matplotlib unavailable)")
    print(f"saved: results/serving_dynamic.json  (elapsed {time.time()-t0:.1f}s)")


if __name__ == "__main__":
    run()
