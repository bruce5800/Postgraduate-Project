"""Phase 4 (deepest) — prefix-cache-aware routing on a real Mooncake LLM trace.

Two findings:
 1) REVERSAL vs dynamic serving: for KV-cache reuse, STABLE placement (consistent
    hashing of the prefix family to a fixed replica) beats REACTIVE cache-affinity
    routing — the opposite of load balancing, where reactive (least-loaded) wins.
    Caching wants a prefix pinned to one replica; reactive routing fragments it.
 2) Prediction angle: a forecast of prefix-family popularity can PLACE families to
    balance load (forecast_home), beating blind consistent-hash when the forecast
    is good; a stale/wrong forecast hurts, and the prefix-test recovers it.

Connects matching-with-predictions to learning-augmented CACHING (Lykouris &
Vassilvitskii). Data: Mooncake conversation_trace (real prefix block hashes);
toolagent_trace as a wrong-workload forecast source.

Outputs: results/prefix_cache.json, results/prefix_cache_reversal.png,
         results/prefix_cache_forecast.png
"""
from __future__ import annotations
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from algorithms.prefix_cache import (
    run_router, signature, cache_affinity_chooser, least_loaded_chooser,
    consistent_hash_chooser, home_chooser, build_forecast_home, run_adaptive,
)

MC = Path(__file__).resolve().parent.parent / "data" / "trace" / "mooncake"
K = 2
N_REP = 16


def _load(path):
    return [json.loads(l)["hash_ids"] for l in open(path)]


def main(seed=0):
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    conv = _load(MC / "conversation_trace.jsonl")
    tool = _load(MC / "toolagent_trace.jsonl")
    half = len(conv) // 2
    live = conv[half:]
    n = len(live)
    print(f"Mooncake prefix-cache: {n} live requests, k={K}-block family signature, R={N_REP}")

    # ---- Finding 1: reversal — stable vs reactive, across cache capacity ----
    caps = [200, 500, 1000, 2000, 4000]
    reversal = {"caps": caps, "cache_affinity": [], "least_loaded": [], "consistent_hash": []}
    for B in caps:
        reversal["cache_affinity"].append(run_router(live, cache_affinity_chooser(N_REP), N_REP, B))
        reversal["least_loaded"].append(run_router(live, least_loaded_chooser(N_REP), N_REP, B))
        reversal["consistent_hash"].append(run_router(live, consistent_hash_chooser(N_REP, K), N_REP, B))
        print(f"  B={B:4d}: affinity={reversal['cache_affinity'][-1]:.3f} "
              f"least_loaded={reversal['least_loaded'][-1]:.3f} "
              f"consistent_hash={reversal['consistent_hash'][-1]:.3f}")

    # ---- Finding 2: forecast-placed homing vs consistent-hash, by forecast quality ----
    sig_index = {s: i for i, s in enumerate(sorted({signature(h, K) for h in live}))}
    r_types = len(sig_index)
    p_live = np.zeros(r_types)
    for h in live:
        p_live[sig_index[signature(h, K)]] += 1.0
    p_live /= p_live.sum()

    def counts_from(reqs):
        return Counter(signature(h, K) for h in reqs)

    def dist_over_index(counts):
        v = np.zeros(r_types)
        tot = sum(counts.values())
        for s, c in counts.items():
            if s in sig_index:
                v[sig_index[s]] += c
        return v / max(1, tot)

    forecast_sources = {
        "perfect": counts_from(live),
        "stale\n(conv older half)": counts_from(conv[:half]),
        "wrong workload\n(toolagent)": counts_from(tool),
    }
    B_fix = 500
    fc = {}
    for lab, cnt in forecast_sources.items():
        q = dist_over_index(cnt)
        l1 = float(np.abs(p_live - q).sum())
        home = build_forecast_home(dict(cnt), N_REP)
        h_home = run_router(live, home_chooser(home, N_REP, K), N_REP, B_fix)
        h_adapt, followed = run_adaptive(live, home, q, sig_index, N_REP, B_fix, K,
                                         prefix_k=max(1, n // 10))
        fc[lab] = {"l1": l1, "forecast_home": h_home, "adaptive": h_adapt, "followed": followed}
        print(f"  forecast '{lab.splitlines()[0]:>12}' (L1={l1:.2f}): "
              f"home={h_home:.3f} adaptive={h_adapt:.3f} followed={followed}")
    ch_fix = run_router(live, consistent_hash_chooser(N_REP, K), N_REP, B_fix)

    data = {"n": n, "R": N_REP, "k": K, "reversal": reversal,
            "consistent_hash_at_Bfix": ch_fix, "B_fix": B_fix, "forecast": fc}
    (out_dir / "prefix_cache.json").write_text(json.dumps(data, indent=2))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8.5, 5.2))
        ax.plot(caps, reversal["consistent_hash"], "s-", color="C2", label="consistent-hash (stable placement)")
        ax.plot(caps, reversal["cache_affinity"], "o--", color="C3", label="cache-affinity (reactive)")
        ax.plot(caps, reversal["least_loaded"], "^:", color="gray", label="least-loaded (reactive, cache-blind)")
        ax.set_xlabel("cache capacity per replica (blocks)")
        ax.set_ylabel("KV-cache hit fraction")
        ax.set_title("Reversal: for cache reuse, STABLE placement beats REACTIVE routing\n"
                     "(opposite of load balancing) — real Mooncake LLM prefix trace")
        ax.grid(True, alpha=0.3); ax.legend()
        fig.savefig(out_dir / "prefix_cache_reversal.png", dpi=120, bbox_inches="tight")
        plt.close(fig)

        labels = list(forecast_sources.keys())
        order = sorted(labels, key=lambda l: fc[l]["l1"])
        x = [fc[l]["l1"] for l in order]
        fig, ax = plt.subplots(figsize=(8.5, 5.2))
        ax.plot(x, [fc[l]["forecast_home"] for l in order], "o--", color="C3", label="forecast-placed homing")
        ax.plot(x, [fc[l]["adaptive"] for l in order], "s-", color="C2", label="adaptive (test + fall back)")
        ax.axhline(ch_fix, ls=":", color="gray", label=f"consistent-hash (no forecast) = {ch_fix:.3f}")
        for xi, l in zip(x, order):
            ax.annotate(l.splitlines()[0], (xi, ax.get_ylim()[0]), fontsize=8, ha="center", color="gray")
        ax.set_xlabel("forecast error L1 (prefix-family popularity)")
        ax.set_ylabel(f"KV-cache hit fraction (B={B_fix})")
        ax.set_title("Prediction-placed homing beats blind consistent-hash with a good\n"
                     "forecast, degrades when stale; the prefix-test recovers it")
        ax.grid(True, alpha=0.3); ax.legend(loc="best")
        fig.savefig(out_dir / "prefix_cache_forecast.png", dpi=120, bbox_inches="tight")
        plt.close(fig)
        print("\nsaved: prefix_cache_reversal.png, prefix_cache_forecast.png")
    except ImportError:
        print("(matplotlib unavailable)")
    print(f"saved: results/prefix_cache.json")


if __name__ == "__main__":
    main()
