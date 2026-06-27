"""M3 — rank vs MSE training with REAL temporal features on a REAL serving trace.

The decisive external-validity test for Research Plan A. M0/M1 used synthetic
features; here features and arrivals are genuine and the matching has a real gap.

Workload: the Azure LLM inference trace (19,366 requests, real timestamps). Request
TYPE = a bucket of its context length (log-scale); the live arrival stream is the
real per-request sequence. Resources are served via a fixed serving topology (each
type can be served by `deg` resources — MoE/cache affinity), which creates the
floor→OPT matching gap MPD needs. (The Mooncake prefix-cache trace was tried first
but its structure — one universal root block + a long unique-suffix tail — has no
balanced contention, so the matching saturates; see report.)

The predictor is LEARNED from real history: features for a RESOURCE = its induced
degree (arrivals that could use it) over the previous L windows; target = its degree
in the next window. We train an MSE-loss predictor (status-quo predict-then-optimize)
and a pairwise-RANK-loss predictor (proposed), and evaluate matching ratio on
held-out future windows — measuring (a) whether real temporal features induce the
order/magnitude divergence that lets rank-training win, and (b) the size of any
advantage relative to the (now real) floor→oracle gap.

Outputs: results/rank_real_trace.json, results/rank_real_trace.png
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import kendalltau

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.serving import serving_topology
from optimal import max_matching_size
from algorithms.ranking import ranking
from algorithms.min_predicted_degree import mpd
from scripts.run_rank_vs_mse_mve import fit_mse, fit_rank, score_mse, score_rank

AZURE = Path(__file__).resolve().parent.parent / "data" / "trace" / "azure_llm" / "AzureLLMInferenceTrace_conv.csv"


def load_context_tokens():
    """Return the per-request context-token counts in trace (time) order."""
    vals = []
    with AZURE.open() as f:
        next(f)  # header
        for line in f:
            parts = line.split(",")
            if len(parts) >= 2:
                vals.append(int(parts[1]))
    return np.array(vals, dtype=np.int64)


def bucketize(ctx, n_types):
    """Log-scale bucket of context length → request type in [0, n_types)."""
    lo, hi = np.log1p(ctx.min()), np.log1p(ctx.max())
    edges = np.linspace(lo, hi, n_types + 1)
    b = np.clip(np.digitize(np.log1p(ctx), edges[1:-1]), 0, n_types - 1)
    return b


def induced_degree(type_adj, type_counts, n_res):
    """μ(r) = number of arrivals (by type) whose neighbourhood includes r."""
    mu = np.zeros(n_res, dtype=np.float64)
    for l, c in enumerate(type_counts):
        if c:
            for r in type_adj[l]:
                mu[r] += c
    return mu


def make_lag_features(deg_hist, t, L):
    """Resource features for window t: previous L windows' induced degrees (log1p, z)."""
    X = np.stack([np.log1p(deg_hist[:, t - l]) for l in range(1, L + 1)], axis=1)
    return (X - X.mean(0)) / (X.std(0) + 1e-9)


def run(n_types=150, n_res=500, deg=8, n_windows=40, L=3, train_frac=0.6, seed=0):
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    ctx = load_context_tokens()
    types_all = bucketize(ctx, n_types)
    n = len(ctx)
    print(f"Azure LLM: {n} requests, {n_types} context-length types, "
          f"{n_res} resources (deg {deg}), {n_windows} windows")

    rng_topo = np.random.default_rng(seed)
    type_adj, _p = serving_topology(n_res, n_types, deg, rng_topo)

    # per-window arrival types and induced resource degrees
    per = n // n_windows
    win_types = []                         # arrival type sequence per window
    deg_hist = np.zeros((n_res, n_windows))
    for w in range(n_windows):
        lo, hi = w * per, (w + 1) * per if w < n_windows - 1 else n
        tw = types_all[lo:hi]
        win_types.append(tw)
        counts = np.bincount(tw, minlength=n_types).astype(float)
        deg_hist[:, w] = induced_degree(type_adj, counts, n_res)

    first = L
    split = int(first + train_frac * (n_windows - first))
    train_ts, test_ts = range(first, split), range(split, n_windows)
    print(f"train windows {list(train_ts)}  test windows {list(test_ts)}")

    Xs, ys = [], []
    for t in train_ts:
        Xs.append(make_lag_features(deg_hist, t, L)); ys.append(deg_hist[:, t])
    Xtr, ytr = np.concatenate(Xs), np.concatenate(ys)
    coef_mse, w_rank = fit_mse(Xtr, ytr), fit_rank(Xtr, ytr)
    print(f"fitted: MSE coef={np.round(coef_mse,2)}  rank w={np.round(w_rank,2)}")

    rng = np.random.default_rng(seed + 1)
    agg = {k: [] for k in ["mse", "rank", "oracle", "floor", "lastwin"]}
    tau = {"mse": [], "rank": [], "lastwin": []}
    rows = []
    for t in test_ts:
        X = make_lag_features(deg_hist, t, L)
        s_mse, s_rank, s_last = score_mse(coef_mse, X), score_rank(w_rank, X), deg_hist[:, t - 1]
        y = deg_hist[:, t]
        inst = [type_adj[int(l)] for l in win_types[t]]   # real arrivals, real order
        opt = max_matching_size(inst, n_right=n_res)
        if opt == 0:
            continue
        ts = int(rng.integers(0, 2**31 - 1))
        r = {"mse": mpd(inst, n_res, s_mse, np.random.default_rng(ts)) / opt,
             "rank": mpd(inst, n_res, s_rank, np.random.default_rng(ts)) / opt,
             "oracle": mpd(inst, n_res, y, np.random.default_rng(ts)) / opt,
             "floor": ranking(inst, n_res, np.random.default_rng(ts)) / opt,
             "lastwin": mpd(inst, n_res, s_last, np.random.default_rng(ts)) / opt}
        for k in agg:
            agg[k].append(r[k])
        tau["mse"].append((1 - kendalltau(s_mse, y)[0]) / 2)
        tau["rank"].append((1 - kendalltau(s_rank, y)[0]) / 2)
        tau["lastwin"].append((1 - kendalltau(s_last, y)[0]) / 2)
        rows.append({"t": t, "n_req": len(inst), "opt": opt, **r})

    def ci(v):
        a = np.asarray(v, float)
        return float(a.mean()), float(1.96 * a.std(ddof=1) / np.sqrt(len(a))) if len(a) > 1 else 0.0

    floor_m, oracle_m = ci(agg["floor"])[0], ci(agg["oracle"])[0]
    mse_m, rank_m = ci(agg["mse"])[0], ci(agg["rank"])[0]
    gap = oracle_m - floor_m
    cap = lambda x: (x - floor_m) / gap if abs(gap) > 1e-9 else float("nan")

    summary = {"params": {"n_types": n_types, "n_res": n_res, "deg": deg,
                          "n_windows": n_windows, "L": L, "n_test": len(rows)},
               "ratio": {k: ci(agg[k]) for k in agg},
               "tau_to_next": {k: ci(tau[k]) for k in tau},
               "gap": gap, "gap_capture": {k: cap(ci(agg[k])[0]) for k in ["rank", "mse", "lastwin"]},
               "rows": rows}
    (out_dir / "rank_real_trace.json").write_text(json.dumps(summary, indent=2))

    print(f"\n=== matching ratio over {len(rows)} held-out windows (mean ± CI) ===")
    for k in ["oracle", "rank", "mse", "lastwin", "floor"]:
        m, h = ci(agg[k])
        extra = f"   gap-capture {cap(m)*100:4.0f}%" if k in ("rank", "mse", "lastwin") else ""
        print(f"  {k:9s} ratio={m:.4f} ±{h:.4f}{extra}")
    print(f"\n  floor→oracle gap = {gap:.4f}")
    print(f"  order error to next window (Kendall-τ): "
          f"rank={ci(tau['rank'])[0]:.3f}  mse={ci(tau['mse'])[0]:.3f}  lastwin={ci(tau['lastwin'])[0]:.3f}")
    adv = rank_m - mse_m
    print(f"  rank-advantage over MSE = {adv:+.4f}  "
          f"(rank captures {cap(rank_m)*100:.0f}% of the gap vs MSE {cap(mse_m)*100:.0f}%)")

    _plot(summary, agg, ci, out_dir)
    return summary


def _plot(summary, agg, ci, out_dir):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.4))
    order = ["oracle", "rank", "mse", "lastwin", "floor"]
    labels = ["oracle\n(true next deg)", "rank-trained", "MSE-trained",
              "last-window\n(non-learned)", "Ranking\n(floor)"]
    colors = ["purple", "C0", "C3", "C1", "gray"]
    ax = axes[0]
    means = [ci(agg[k])[0] for k in order]; errs = [ci(agg[k])[1] for k in order]
    ax.bar(range(len(order)), means, yerr=errs, capsize=3, color=colors)
    ax.set_xticks(range(len(order))); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylim(min(means) - 0.02, 1.005)
    ax.set_ylabel("matching ratio (served / OPT)")
    ax.set_title("Azure LLM serving: learned-rank vs learned-MSE predictor\n(real arrivals + real temporal features, held-out windows)")
    ax.grid(True, axis="y", alpha=0.3)
    ax = axes[1]
    ts = [r["t"] for r in summary["rows"]]
    for k, c, m in [("rank", "C0", "o-"), ("mse", "C3", "s-"),
                    ("oracle", "purple", "^:"), ("floor", "gray", ":")]:
        ax.plot(ts, [r[k] for r in summary["rows"]], m, color=c, label=k, markersize=4)
    ax.set_xlabel("held-out window index (time)"); ax.set_ylabel("matching ratio")
    ax.set_title("Per-window (temporal generalisation)")
    ax.grid(True, alpha=0.3); ax.legend(fontsize=8)
    fig.suptitle("M3 — learning to rank on a REAL serving trace with REAL temporal features", fontsize=12)
    fig.tight_layout()
    fig.savefig(out_dir / "rank_real_trace.png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    print("\nsaved: results/rank_real_trace.png")


if __name__ == "__main__":
    run()
