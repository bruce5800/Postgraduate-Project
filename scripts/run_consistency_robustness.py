"""Fig 4.2 — the consistency-robustness plane, re-plotted from unified_benchmark.json.

No new simulation: reads results/unified_benchmark.json (written by
run_unified_benchmark.py) and plots, per panel, one point per prediction-consuming
algorithm at (robustness, consistency) where
  consistency = mean ratio under perfect advice (first quality level),
  robustness  = worst mean ratio across all quality levels.
Reference lines: the advice-free Ranking floor (dashed, both axes) and the oracle
consistency ceiling (dotted). Writes results/consistency_robustness.{json,png}.
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
IN = ROOT / "results" / "unified_benchmark.json"
OUT_JSON = ROOT / "results" / "consistency_robustness.json"
OUT_PNG = ROOT / "results" / "consistency_robustness.png"

PANEL_TITLES = {
    "clvb_zipf": "Panel A — clvb_zipf (degree predictions)",
    "left_regular_d5": "Panel B — left-regular d=5 (degree predictions)",
    "few_types (r=8)": "Panel C — few-types r=8 (histogram advice)",
}
COLORS = {
    "MPD": "tab:red",
    "Feldman(MPD)": "tab:green",
    "JailletLu(MPD)": "tab:blue",
    "FollowPrediction": "tab:red",
    "TestAndMatch (Choo)": "tab:green",
    "TestAndMatch (BEM)": "tab:blue",
    "Combiner": "tab:purple",
}
# per-point label offsets (points), tuned so labels don't collide
OFFSETS = {
    "MPD": (6, -10),
    "Feldman(MPD)": (6, 4),
    "JailletLu(MPD)": (6, -12),
    "FollowPrediction": (8, -4),
    "TestAndMatch (Choo)": (-8, -12),
    "TestAndMatch (BEM)": (-8, -4),
    "Combiner": (-8, 6),
    "Ranking": (6, 6),
}


def main() -> None:
    panels = json.loads(IN.read_text())
    summary = []

    fig, axes = plt.subplots(1, len(panels), figsize=(5.2 * len(panels), 4.6))
    for ax, panel in zip(axes, panels):
        rows, levels = panel["rows"], panel["levels"]
        floor = rows["Ranking"][levels[0]]["mean"]
        oracle_name = next(
            (a for a in panel["flat_algos"] if "oracle" in a or "true degrees" in a), None
        )
        oracle = rows[oracle_name][levels[0]]["mean"] if oracle_name else None

        pts = {}
        for algo in panel["pred_algos"]:
            cons = rows[algo][levels[0]]["mean"]
            rob = min(rows[algo][lv]["mean"] for lv in levels)
            pts[algo] = (rob, cons)
        pts["Ranking"] = (floor, floor)  # the advice-free point

        ax.margins(0.14)
        ax.axvline(floor, color="gray", ls="--", lw=1, alpha=0.7)
        ax.axhline(floor, color="gray", ls="--", lw=1, alpha=0.7)
        if oracle is not None:
            ax.axhline(oracle, color="gray", ls=":", lw=1, alpha=0.7)
            ax.annotate(
                "oracle ceiling", (0.45, oracle), xycoords=("axes fraction", "data"),
                fontsize=7, color="gray", va="bottom",
            )
        for algo, (rob, cons) in pts.items():
            marker = "*" if algo == "Ranking" else "o"
            color = COLORS.get(algo, "black")
            ax.scatter([rob], [cons], s=110 if marker == "*" else 45,
                       marker=marker, color=color, zorder=3)
            dx, dy = OFFSETS.get(algo, (6, 4))
            ax.annotate(algo, (rob, cons), textcoords="offset points",
                        xytext=(dx, dy), fontsize=8,
                        ha="left" if dx >= 0 else "right")
        ax.set_title(PANEL_TITLES.get(panel["graph"], panel["graph"]), fontsize=10)
        ax.set_xlabel("robustness (worst ratio across advice quality)")
        ax.grid(alpha=0.25)
        summary.append(
            {"graph": panel["graph"], "floor": floor, "oracle": oracle,
             "points": {a: {"robustness": r, "consistency": c}
                        for a, (r, c) in pts.items()}}
        )
    axes[0].set_ylabel("consistency (ratio under perfect advice)")
    fig.suptitle(
        "The consistency-robustness plane (data: the unified benchmark, Table 4.1) — "
        "up and to the right is better", fontsize=11,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(OUT_PNG, dpi=150)
    OUT_JSON.write_text(json.dumps(summary, indent=2))
    print(f"wrote {OUT_PNG}")
    for s in summary:
        print(f"  {s['graph']}: floor={s['floor']:.3f}", {a: (round(p['robustness'], 3), round(p['consistency'], 3)) for a, p in s['points'].items()})


if __name__ == "__main__":
    main()
