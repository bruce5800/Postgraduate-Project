"""Figure for Appendix A.7 — the relaxation ladder. Reads
results/streaming_ladder.json (written by run_streaming_ladder.py; no new
simulation) and writes results/streaming_ladder.png."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
IN = ROOT / "results" / "streaming_ladder.json"

SERIES = [
    ("Greedy (online)", "Greedy — online, advice-free", "tab:gray"),
    ("MPD, perfect prediction (online)", "MPD — online, perfect prediction", "tab:red"),
    ("Semi-streaming, 1 pass", "Semi-streaming, 1 pass", "tab:blue"),
    ("Semi-streaming, 2 passes", "Semi-streaming, 2 passes", "tab:green"),
]


def draw(ax, panels, title, ylo):
    x = np.arange(len(panels))
    w = 0.8 / len(SERIES)
    for i, (key, label, color) in enumerate(SERIES):
        m = np.array([p["rows"][key]["mean"] for p in panels])
        e = np.array([p["rows"][key]["ci95"] for p in panels])
        ax.bar(x + i * w - 0.4 + w / 2, m, w, yerr=e, capsize=2,
               color=color, label=label, edgecolor="white", linewidth=0.4)
    ax.axhline(1.0, color="black", linewidth=0.9, linestyle="--")
    ax.text(-0.42, 1.0 + 0.004, "offline OPT", va="bottom", ha="left", fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels([p["graph"] for p in panels], fontsize=7.5, rotation=12)
    ax.set_ylim(ylo, 1.03)
    ax.set_ylabel("empirical competitive ratio", fontsize=8)
    ax.set_title(title, fontsize=9)
    ax.tick_params(axis="y", labelsize=7.5)
    ax.grid(axis="y", linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)


def floor_of(res):
    lo = 1.0
    for group in ("synthetic", "realworld"):
        for p in res[group]:
            for key, _, _ in SERIES:
                lo = min(lo, p["rows"][key]["mean"] - p["rows"][key]["ci95"])
    return max(0.0, lo - 0.015)


def main() -> None:
    res = json.loads(IN.read_text())
    ylo = floor_of(res)
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.5), sharey=True,
                             gridspec_kw={"width_ratios": [1, 1.9]})
    draw(axes[0], res["synthetic"], "Synthetic families", ylo)
    draw(axes[1], res["realworld"], "Real-world graphs (random partition)", ylo)
    axes[1].set_ylabel("")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=7.5, ncol=4, frameon=False,
               loc="lower center", bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    out = ROOT / "results" / "streaming_ladder.png"
    fig.savefig(out, dpi=200)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
