"""Phase 4 — real AI-inference trace (Azure LLM Inference, Splitwise/OSDI'24).

A real LLM inference serving trace: each request has a context length. Following
size-aware serving (Splitwise / DistServe / Sarathi route by request size), we
type requests by CONTEXT-LENGTH bucket; the popularity over size-buckets is the
request mix, and a traffic forecast is a predicted size-mix. We use the REAL
arrival stream (conv trace, second half) and three GENUINE forecast sources of
increasing error, measured by real L1:

  - perfect       : the live size-mix itself (consistency anchor, L1 = 0)
  - same workload : the conv FIRST half (a realistic recent forecast)
  - wrong workload: the CODE trace (a badly-mismatched forecast)

This complements the Wikipedia experiment with a real *inference* workload: the
same result (blind trust crashes as the forecast diverges; the adaptive test stays
robust; the cliff deepens with capacity) holds on real LLM serving traffic.

Outputs: results/serving_llm.json, results/serving_llm.png
"""
from __future__ import annotations
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.serving import serving_topology
from optimal import max_b_matching_size
from algorithms.capacity import (
    greedy_with_capacity, build_advice_b_matching,
    follow_prediction_capacity, test_and_match_capacity,
)

TRACE = Path(__file__).resolve().parent.parent / "data" / "trace" / "azure_llm"
NB, N_RES, DEG = 40, 350, 12
CAPS = [4, 16]
M_LIMIT = 2500   # a contiguous real window of the trace (balanced-load regime)


def _ctx(path):
    return np.array([int(r["ContextTokens"]) for r in csv.DictReader(open(path))])


def _bucketize(arr, edges):
    return np.clip(np.digitize(arr, edges[1:-1]), 0, len(edges) - 2)


def run(n_trials=15, seed=0):
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    conv = _ctx(TRACE / "AzureLLMInferenceTrace_conv.csv")
    code = _ctx(TRACE / "AzureLLMInferenceTrace_code.csv")
    # Log-spaced FIXED size buckets keep the real skew (many short requests, few
    # long ones); quantile buckets would flatten it to near-uniform.
    edges = np.unique(np.geomspace(max(1, int(conv.min())), int(conv.max()), NB + 1))
    nb = len(edges) - 1

    half = len(conv) // 2
    live_types = _bucketize(conv[half:half + M_LIMIT], edges)  # real contiguous window
    m = len(live_types)

    def hist(arr):
        h = np.bincount(_bucketize(arr, edges), minlength=nb).astype(float)
        return h / h.sum()

    p_live = np.bincount(live_types, minlength=nb).astype(float); p_live /= p_live.sum()
    forecasts = {
        "perfect": p_live,
        "same workload\n(conv, older half)": hist(conv[:half]),
        "wrong workload\n(code trace)": hist(code),
    }
    drift = {lab: float(np.abs(p_live - q).sum()) for lab, q in forecasts.items()}
    print(f"Azure LLM trace: {m} real arrivals, {nb} size-bucket types")
    for lab, l1 in drift.items():
        print(f"  forecast '{lab.splitlines()[0]}': real L1={l1:.3f}")

    rg, rs = np.random.default_rng(seed).spawn(2)
    res = {"m": m, "nb": nb, "caps": CAPS, "drift": drift, "by_cap": {}}
    t0 = time.time()
    for cap in CAPS:
        res["by_cap"][cap] = {}
        for lab, q in forecasts.items():
            blind, adapt, base = [], [], []
            for _ in range(n_trials):
                type_adj, _ = serving_topology(N_RES, nb, DEG, rg)
                instance_adj = [type_adj[t] for t in live_types]
                opt = max_b_matching_size(live_types, type_adj, N_RES, cap)
                if opt == 0:
                    continue
                chat = np.round(m * q).astype(np.float64)
                n_hat, partners = build_advice_b_matching(type_adj, chat, N_RES, cap)
                s = int(rs.integers(0, 2**31 - 1))
                blind.append(follow_prediction_capacity(instance_adj, live_types, N_RES, partners, chat, cap) / opt)
                tm, _ = test_and_match_capacity(instance_adj, live_types, N_RES, partners, chat, n_hat, cap,
                                                rng=np.random.default_rng(s), variant="bem", prefix_k=max(1, m // 8))
                adapt.append(tm / opt)
                rank = np.empty(N_RES, dtype=np.int64)
                perm = np.random.default_rng(s).permutation(N_RES); rank[perm] = np.arange(N_RES)
                base.append(greedy_with_capacity(instance_adj, rank, N_RES, cap) / opt)
            res["by_cap"][cap][lab] = {"l1": drift[lab], "blind": float(np.mean(blind)),
                                       "adapt": float(np.mean(adapt)), "base": float(np.mean(base))}
            r = res["by_cap"][cap][lab]
            print(f"  cap={cap} {lab.splitlines()[0]:>24} (L1={r['l1']:.2f}): "
                  f"blind={r['blind']:.3f} adapt={r['adapt']:.3f} base={r['base']:.3f}")

    (out_dir / "serving_llm.json").write_text(json.dumps(res, indent=2))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        labels = list(forecasts.keys())
        order = sorted(labels, key=lambda l: drift[l])
        x = [drift[l] for l in order]
        fig, axes = plt.subplots(1, len(CAPS), figsize=(6 * len(CAPS), 5), sharey=True)
        for ax, cap in zip(axes, CAPS):
            d = res["by_cap"][cap]
            ax.plot(x, [d[l]["blind"] for l in order], "o--", color="C3", label="blindly follow forecast")
            ax.plot(x, [d[l]["adapt"] for l in order], "s-", color="C2", label="TestAndMatch (adaptive)")
            ax.plot(x, [d[l]["base"] for l in order], ":", color="gray", label="forecast-free baseline")
            for xi, l in zip(x, order):
                ax.annotate(l.splitlines()[0], (xi, 0.30), fontsize=8, ha="center", color="gray")
            ax.set_xlabel("real forecast error L1(live size-mix, forecast)")
            ax.set_title(f"capacity c = {cap}")
            ax.grid(True, alpha=0.3)
        axes[0].set_ylabel("goodput (served / best possible)")
        axes[0].legend(loc="lower left")
        fig.suptitle("Real Azure LLM inference trace (size-bucket routing): as the traffic forecast\n"
                     "diverges from the live request mix, blind trust crashes; the adaptive test stays robust")
        fig.savefig(out_dir / "serving_llm.png", dpi=120, bbox_inches="tight")
        plt.close(fig)
        print("\nsaved: serving_llm.png")
    except ImportError:
        print("(matplotlib unavailable)")
    print(f"saved: results/serving_llm.json  (elapsed {time.time()-t0:.1f}s)")


if __name__ == "__main__":
    run()
