"""PROBE — is there a prediction-shaped GAP on an SLO/tail objective in serving?

The throughput objective is forgiving (finding F3): every serving variant we tried
re-derived known systems results because a reactive baseline already fills capacity,
so goodput ≈ OPT and predictions add nothing. This probe changes the OBJECTIVE to
one where the baseline can be genuinely far from optimal, to test whether the
with-predictions lens can yield a NEW actionable serving result (rescuing it from
case-study status) — before building anything.

Setup. Event-driven serving with real service durations (requests hold a slot).
Requests have an SLO CLASS: HIGH (tight SLO — a drop is a violation) or LOW
(best-effort). Arrivals are BURSTY and non-stationary (periodic bursts concentrated
on a hot type-set), in an OVERLOADED regime so capacity is genuinely contended.

Objective: the HIGH-class violation rate (HIGH requests dropped / HIGH total).

Policies (all PRIORITISE HIGH; they differ only in whether they RESERVE capacity):
  - reactive (reserve=0)      : serve greedily, HIGH-first, no reservation. Drops a
                                HIGH request only if every capable resource is full —
                                but LOW requests admitted earlier may be holding those
                                slots (it could not foresee the HIGH burst).
  - static-reserve (best R0)  : always keep R0 slots free for HIGH. The strongest
                                NON-predictive policy; we sweep R0 and take its best.
  - clairvoyant (oracle)      : reserve per resource the upcoming HIGH demand within a
                                horizon (perfect future knowledge). Upper bound on what
                                a burst predictor could achieve.

If clairvoyant ≪ best non-predictive on HIGH violations → a real gap exists → a burst
predictor can rescue serving on the SLO objective. If clairvoyant ≈ reactive → the
SLO objective is forgiving too → serving stays a case study.

Outputs: results/serving_slo_probe.json, results/serving_slo_probe.png
"""
from __future__ import annotations
import bisect
import heapq
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.serving import serving_topology


def make_bursty_arrivals(n_types, rng, T=3000.0, base_rate=4.0, burst_rate=40.0,
                         period=500.0, burst_len=120.0, hot_frac=0.12,
                         high_frac=0.25, high_frac_burst=None, dur_mean=25.0):
    """Non-stationary Poisson arrivals with periodic bursts concentrated on a hot
    type-set. If high_frac_burst is set, the HIGH-class probability is high_frac_burst
    DURING bursts and high_frac off-peak — making the tight-SLO demand itself bursty
    (the regime where a forecast could beat a static reservation). Returns
    (t, type, dur, is_high) sorted by time."""
    if high_frac_burst is None:
        high_frac_burst = high_frac
    hot_list = np.array(sorted(rng.choice(n_types, size=max(1, int(hot_frac * n_types)),
                                          replace=False).tolist()))
    cold_list = np.array([l for l in range(n_types) if l not in set(hot_list.tolist())])
    ts, tps, durs, highs = [], [], [], []
    t = 0.0
    while t < T:
        in_burst = (t % period) < burst_len
        rate = burst_rate if in_burst else base_rate
        t += rng.exponential(1.0 / rate)
        if t >= T:
            break
        if in_burst and rng.random() < 0.85:
            l = int(rng.choice(hot_list))
        elif len(cold_list) and rng.random() < 0.6:
            l = int(rng.choice(cold_list))
        else:
            l = int(rng.integers(n_types))
        ts.append(t); tps.append(l)
        durs.append(rng.exponential(dur_mean))
        highs.append(rng.random() < (high_frac_burst if in_burst else high_frac))
    order = np.argsort(ts)
    return (np.array(ts)[order], np.array(tps)[order],
            np.array(durs)[order], np.array(highs, dtype=bool)[order])


def simulate_slo(arr_t, arr_type, arr_dur, arr_high, type_adj, n_right, capacity,
                 reserve_at, base_rank):
    """Event-driven. `reserve_at(r, t)` = slots to keep free on resource r for HIGH;
    HIGH requests ignore it, LOW obey it. Returns (high_total, high_violations, served)."""
    load = np.zeros(n_right, dtype=np.int64)
    heap: list[tuple[float, int]] = []
    high_total = high_viol = served = low_total = low_served = 0
    for i in range(len(arr_t)):
        t, l, dur, hi = arr_t[i], int(arr_type[i]), arr_dur[i], bool(arr_high[i])
        while heap and heap[0][0] <= t:
            _, r = heapq.heappop(heap)
            load[r] -= 1
        best, best_key = None, None
        for r in type_adj[l]:
            thresh = capacity if hi else capacity - reserve_at(r, t)
            if load[r] < thresh:
                key = (load[r], base_rank[r])
                if best_key is None or key < best_key:
                    best_key, best = key, r
        if hi:
            high_total += 1
        else:
            low_total += 1
        if best is not None:
            load[best] += 1
            heapq.heappush(heap, (t + dur, best))
            served += 1
            if not hi:
                low_served += 1
        elif hi:
            high_viol += 1
    return high_total, high_viol, served, low_total, low_served


def _per_resource_high_times(arr_t, arr_type, arr_high, type_adj, n_right):
    times: list[list[float]] = [[] for _ in range(n_right)]
    wts: list[list[float]] = [[] for _ in range(n_right)]
    for j in range(len(arr_t)):
        if arr_high[j]:
            cap = type_adj[int(arr_type[j])]
            w = 1.0 / max(1, len(cap))
            for r in cap:
                times[r].append(arr_t[j]); wts[r].append(w)
    tarr = [np.array(x) for x in times]
    cum = [np.concatenate([[0.0], np.cumsum(w)]) for w in wts]
    return tarr, cum


def build_clairvoyant(arr_t, arr_type, arr_high, type_adj, n_right, horizon, deg):
    """Reservation for r at t = expected upcoming HIGH demand in (t, t+horizon]
    (perfect FUTURE knowledge). O(log n) range query per call."""
    tarr, cum = _per_resource_high_times(arr_t, arr_type, arr_high, type_adj, n_right)

    def reserve_at(r, t):
        ta = tarr[r]
        if ta.size == 0:
            return 0
        lo = bisect.bisect_right(ta, t)
        hi = bisect.bisect_right(ta, t + horizon)
        return int(round(cum[r][hi] - cum[r][lo]))
    return reserve_at


def build_reactive_adaptive(arr_t, arr_type, arr_high, type_adj, n_right, window, deg):
    """Non-predictive but adaptive: reservation for r at t = observed HIGH demand on r
    in the RECENT PAST (t-window, t] — react to observed load, assuming persistence. No
    foresight. This is the strong baseline a burst predictor must beat."""
    tarr, cum = _per_resource_high_times(arr_t, arr_type, arr_high, type_adj, n_right)

    def reserve_at(r, t):
        ta = tarr[r]
        if ta.size == 0:
            return 0
        lo = bisect.bisect_right(ta, t - window)
        hi = bisect.bisect_right(ta, t)
        return int(round(cum[r][hi] - cum[r][lo]))
    return reserve_at


def run(n_types=80, n_res=60, deg=4, capacity=2, horizon=80.0, window=80.0,
        w_low=0.3, seed=0, n_trials=6):
    """Intermittent-overload regime (off-peak uncontended, bursts overload). Joint
    objective COST = HIGH_violation_rate + w_low·LOW_drop_rate: a policy must protect
    HIGH during bursts WITHOUT needlessly dropping LOW off-peak. Static reserve trades
    one against the other; the question is whether the FUTURE-aware clairvoyant
    dominates BOTH the best static reserve and the REACTIVE-ADAPTIVE (observed-load)
    policy — i.e. whether forecasting the burst beats reacting to it."""
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    rng_top, rng_arr, rng_pol = np.random.default_rng(seed).spawn(3)
    type_adj, _p = serving_topology(n_res, n_types, deg, rng_top)
    reserve_levels = [0, 1, 2]

    policies = ["reactive"] + [f"static={R}" for R in reserve_levels] + ["reactive-adaptive", "clairvoyant"]
    rec = {p: {"hv": [], "ld": [], "tput": []} for p in policies}
    util = []
    t0 = time.time()
    for _ in range(n_trials):
        at, atype, adur, ahigh = make_bursty_arrivals(
            n_types, rng_arr, T=3000.0, base_rate=0.5, burst_rate=6.0,
            period=500.0, burst_len=80.0, hot_frac=0.12, high_frac=0.02,
            high_frac_burst=0.55, dur_mean=15.0)
        base_rank = rng_pol.permutation(n_res)
        util.append(len(at))
        fns = {"reactive": lambda r, t: 0}
        for R in reserve_levels:
            fns[f"static={R}"] = (lambda RR: (lambda r, t: RR))(R)
        fns["reactive-adaptive"] = build_reactive_adaptive(at, atype, ahigh, type_adj, n_res, window, deg)
        fns["clairvoyant"] = build_clairvoyant(at, atype, ahigh, type_adj, n_res, horizon, deg)
        for p, fn in fns.items():
            ht, hv, sv, lt, ls = simulate_slo(at, atype, adur, ahigh, type_adj, n_res, capacity, fn, base_rank)
            rec[p]["hv"].append(hv / max(1, ht))
            rec[p]["ld"].append((lt - ls) / max(1, lt))
            rec[p]["tput"].append(sv / len(at))

    def ms(v):
        a = np.asarray(v, float)
        return float(a.mean()), float(1.96 * a.std(ddof=1) / np.sqrt(len(a))) if len(a) > 1 else 0.0

    cost = {p: ms(rec[p]["hv"])[0] + w_low * ms(rec[p]["ld"])[0] for p in policies}
    non_pred = ["reactive"] + [f"static={R}" for R in reserve_levels] + ["reactive-adaptive"]
    best_np = min(non_pred, key=lambda p: cost[p])
    clair = cost["clairvoyant"]
    gap = cost[best_np] - clair
    rel = gap / cost[best_np] if cost[best_np] > 1e-9 else 0.0

    summary = {"params": {"n_res": n_res, "deg": deg, "capacity": capacity, "horizon": horizon,
                          "window": window, "w_low": w_low, "n_trials": n_trials,
                          "mean_arrivals": float(np.mean(util))},
               "by_policy": {p: {"high_viol": ms(rec[p]["hv"]), "low_drop": ms(rec[p]["ld"]),
                                 "throughput": ms(rec[p]["tput"]), "cost": cost[p]} for p in policies},
               "best_non_predictive": best_np, "gap": gap, "relative_gap": rel}
    (out_dir / "serving_slo_probe.json").write_text(json.dumps(summary, indent=2))

    print(f"intermittent overload: mean {np.mean(util):.0f} arrivals; reactive throughput "
          f"{ms(rec['reactive']['tput'])[0]:.3f}")
    print(f"\n{'policy':20s} {'HIGH-viol':>9s} {'LOW-drop':>9s} {'tput':>6s} {'COST':>7s}")
    for p in policies:
        print(f"  {p:18s} {ms(rec[p]['hv'])[0]:>9.3f} {ms(rec[p]['ld'])[0]:>9.3f} "
              f"{ms(rec[p]['tput'])[0]:>6.3f} {cost[p]:>7.3f}")
    print(f"\n  best NON-predictive = {best_np} (cost {cost[best_np]:.3f}); clairvoyant cost {clair:.3f}")
    print(f"  GAP = {gap:.4f}  ({rel*100:.0f}% relative)   "
          f"[COST = HIGH-viol + {w_low}·LOW-drop]")
    verdict = ("GAP EXISTS — forecasting the burst beats reacting to it → predictions can rescue serving"
               if rel > 0.15 and gap > 0.01 else
               "forgiving — reacting to observed load matches foresight → serving stays a case study")
    print(f"  VERDICT: {verdict}")
    _plot2(summary, policies, rec, ms, out_dir)
    print(f"  (elapsed {time.time()-t0:.1f}s)")
    return summary


def _plot2(summary, policies, rec, ms, out_dir):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    # the HIGH-viol vs LOW-drop tradeoff plane; clairvoyant should sit closest to origin
    for p in policies:
        x, y = ms(rec[p]["ld"])[0], ms(rec[p]["hv"])[0]
        col = "C0" if p == "clairvoyant" else ("C2" if p == "reactive-adaptive" else "C1")
        ax.scatter([x], [y], s=110, color=col, zorder=3)
        ax.annotate(p, (x, y), fontsize=8, xytext=(5, 4), textcoords="offset points")
    ax.set_xlabel("LOW-class drop rate (off-peak waste)")
    ax.set_ylabel("HIGH-class SLO violation rate")
    ax.set_title("Serving SLO probe — HIGH-violation vs LOW-waste tradeoff\n"
                 "(does clairvoyant/foresight dominate reactive-adaptive + static?)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "serving_slo_probe.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    run()
