"""Per-panel bar charts for Table 4.1 — compact companions placed beside each
panel's table in the thesis. Reads results/unified_benchmark.json (written by
run_unified_benchmark.py; no new simulation) and writes
results/unified_benchmark_panel{A,B,C}.png."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
IN = ROOT / "results" / "unified_benchmark.json"

COLORS = {
    "MPD": "tab:red",
    "Feldman(MPD)": "tab:green",
    "JailletLu(MPD)": "tab:blue",
    "FollowPrediction": "tab:red",
    "TestAndMatch (Choo)": "tab:green",
    "TestAndMatch (BEM)": "tab:blue",
    "Combiner": "tab:purple",
}
LETTER = {"clvb_zipf": "A", "left_regular_d5": "B", "few_types (r=8)": "C"}


def main() -> None:
    panels = json.loads(IN.read_text())
    for panel in panels:
        rows, levels = panel["rows"], panel["levels"]
        algos = panel["pred_algos"]
        floor = rows["Ranking"][levels[0]]["mean"]
        oracle_name = next(
            (a for a in panel["flat_algos"] if "oracle" in a or "true degrees" in a), None
        )
        oracle = rows[oracle_name][levels[0]]["mean"] if oracle_name else None

        fig, ax = plt.subplots(figsize=(4.0, 3.1))
        x = np.arange(len(levels))
        w = 0.8 / len(algos)
        lo = 1.0
        for i, algo in enumerate(algos):
            means = [rows[algo][lv]["mean"] for lv in levels]
            cis = [rows[algo][lv]["ci95"] for lv in levels]
            lo = min(lo, min(means))
            ax.bar(x + (i - (len(algos) - 1) / 2) * w, means, w, yerr=cis,
                   color=COLORS.get(algo, "gray"), label=algo,
                   error_kw={"lw": 0.8}, zorder=3)
        ax.axhline(floor, color="gray", ls="--", lw=1.1, zorder=4)
        ax.annotate("floor", (len(levels) - 0.42, floor), fontsize=7,
                    color="gray", va="bottom", ha="right")
        if oracle is not None:
            ax.axhline(oracle, color="gray", ls=":", lw=1.1, zorder=4)
            ax.annotate("oracle", (len(levels) - 0.42, oracle), fontsize=7,
                        color="gray", va="bottom", ha="right")
        pad = max(0.02, (1.0 - lo) * 0.1)
        ax.set_ylim(lo - pad, max(1.0, oracle or 1.0) + pad / 2)
        ax.set_xticks(x, levels, fontsize=8)
        ax.tick_params(axis="y", labelsize=8)
        ax.set_ylabel("competitive ratio", fontsize=8)
        ax.legend(fontsize=6.5, loc="lower left", framealpha=0.9)
        ax.grid(True, axis="y", alpha=0.3)
        fig.tight_layout(pad=0.4)
        letter = LETTER.get(panel["graph"], "X")
        out = ROOT / "results" / f"unified_benchmark_panel{letter}.png"
        fig.savefig(out, dpi=150)
        plt.close(fig)
        print(f"wrote {out.name}  (floor={floor:.3f}, ymin={lo:.3f})")


if __name__ == "__main__":
    main()
