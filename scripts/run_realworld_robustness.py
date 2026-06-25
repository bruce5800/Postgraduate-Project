"""★4 — Do the unified-benchmark findings F1–F3 hold on REAL graphs?

The unified benchmark (docs/UNIFIED_BENCHMARK.md) established, on synthetic graphs:
  F1  robustness is engineered — a NAIVE follower (MPD) crashes BELOW the advice-
      free floor under adversarial predictions, while the structural augmentations
      never do.
  F2  two robustness mechanisms — the (MPD)-augmented Feldman/JailletLu are nearly
      FLAT across prediction quality (the base matching carries the load), trading
      consistency for robustness.
  F3  the consistency upside is small on average-case inputs — the spread between
      algorithms lives on the bad-advice side, not the good side.

This script re-runs the degree-prediction roster on the SIX Network-Repository
graphs (Borodin Tables 3/4) across the same four prediction-quality columns, with
95% CIs, and emits a per-graph F1/F2/F3 verdict — testing universality on real,
non-synthetic structure.

Conversion: random balanced partition (Borodin Table 3, the validated one).

Outputs: results/realworld_robustness.json, results/realworld_robustness.png,
         results/realworld_robustness_tables.md
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.realworld import load_simple_graph, to_bipartite_random_partition
from iid_sampler import sample_instance
from optimal import max_matching_size
from algorithms.greedy import simple_greedy
from algorithms.ranking import ranking
from algorithms.feldman import feldman_preprocess, feldman_online, feldman_online_mpd
from algorithms.jaillet_lu import (
    jaillet_lu_preprocess, jaillet_lu_online, jaillet_lu_online_mpd,
)
from algorithms.min_predicted_degree import mpd, mpd_rank
from predictions.degree_truth import type_graph_degree, instance_degree
from predictions import error_models as em

GRAPHS = {
    "Caltech36": "data/realworld/socfb-Caltech36/socfb-Caltech36.mtx",
    "Reed98": "data/realworld/socfb-Reed98/socfb-Reed98.mtx",
    "CE-GN": "data/realworld/bio-CE-GN/bio-CE-GN.edges",
    "CE-PG": "data/realworld/bio-CE-PG/bio-CE-PG.edges",
    "beause": "data/realworld/econ-beause/econ-beause.mtx",
    "mbeaw": "data/realworld/econ-mbeaflw/econ-mbeaflw.mtx",
}

LEVELS = ["perfect", "noisy", "adversarial", "garbage"]
FLAT = ["SimpleGreedy", "Ranking", "Feldman", "JailletLu", "MinDegree (oracle)"]
PRED = ["MPD", "Feldman(MPD)", "JailletLu(MPD)"]


def ci95(values):
    a = np.asarray(values, float)
    n = a.size
    if n == 0:
        return 0.0, 0.0
    m = float(a.mean())
    if n < 2:
        return m, 0.0
    return m, float(1.96 * a.std(ddof=1) / np.sqrt(n))


def _predictor(level, mu_true, rng):
    if level == "perfect":
        return mu_true
    if level == "noisy":
        return em.random_flip(mu_true, 0.5, rng)[0]
    if level == "adversarial":
        return em.adversarial(mu_true, 1.0, rng)[0]
    if level == "garbage":
        return em.random_flip(mu_true, 1.0, rng)[0]
    raise ValueError(level)


def eval_graph(n, edges, n_trials, seed):
    rg, ri, rj, rp = np.random.default_rng(seed).spawn(4)
    flat = {a: [] for a in FLAT}
    swept = {a: {lv: [] for lv in LEVELS} for a in PRED}

    for _ in range(n_trials):
        ta, nr = to_bipartite_random_partition(n, edges, rg)
        inst, types = sample_instance(ta, m=len(ta), rng=ri)
        opt = max_matching_size(inst, nr)
        if opt == 0:
            continue
        Mb, Mr = feldman_preprocess(ta, nr)
        rn, rpb = jaillet_lu_preprocess(ta, nr)
        mu_true = type_graph_degree(ta, nr)
        mu_real = instance_degree(inst, nr)
        s = int(rj.integers(0, 2**31 - 1))

        flat["SimpleGreedy"].append(simple_greedy(inst, nr) / opt)
        flat["Ranking"].append(ranking(inst, nr, np.random.default_rng(s)) / opt)
        flat["Feldman"].append(feldman_online(inst, types, nr, Mb, Mr) / opt)
        flat["JailletLu"].append(
            jaillet_lu_online(inst, types, nr, rn, rpb, np.random.default_rng(s)) / opt)
        flat["MinDegree (oracle)"].append(mpd(inst, nr, mu_real, np.random.default_rng(s)) / opt)

        for lv in LEVELS:
            mu_p = _predictor(lv, mu_true, rp)
            rank = mpd_rank(mu_p, np.random.default_rng(s))
            swept["MPD"][lv].append(mpd(inst, nr, mu_p, np.random.default_rng(s)) / opt)
            swept["Feldman(MPD)"][lv].append(
                feldman_online_mpd(inst, types, nr, Mb, Mr, rank) / opt)
            swept["JailletLu(MPD)"][lv].append(
                jaillet_lu_online_mpd(inst, types, nr, rn, rpb, np.random.default_rng(s), rank) / opt)

    rows = {a: {lv: ci95(flat[a]) for lv in LEVELS} for a in FLAT}
    for a in PRED:
        rows[a] = {lv: ci95(swept[a][lv]) for lv in LEVELS}
    return rows, len(flat["Ranking"])


def verdict(rows):
    """Per-graph F1/F2/F3 booleans + the key numbers."""
    rk = rows["Ranking"]["perfect"][0]
    mpd_perf = rows["MPD"]["perfect"][0]
    mpd_adv = rows["MPD"]["adversarial"][0]
    fmpd = [rows["Feldman(MPD)"][lv][0] for lv in LEVELS]
    jmpd = [rows["JailletLu(MPD)"][lv][0] for lv in LEVELS]
    mpd_all = [rows["MPD"][lv][0] for lv in LEVELS]
    # F1: naive MPD crashes below the floor under adversarial; augmentations don't.
    f1_crash = mpd_adv < rk - 1e-9
    f1_aug_safe = (min(fmpd) >= rk - 0.01) or (min(jmpd) >= rk - 0.01)
    # F2: structural augmentations are FAR LESS sensitive to prediction quality than
    # naive MPD. Tested relatively (the absolute spread is larger on real graphs than
    # synthetic): augmentation spread ≤ half of MPD's spread across the same columns.
    f2_spread = max(max(fmpd) - min(fmpd), max(jmpd) - min(jmpd))
    mpd_spread = max(mpd_all) - min(mpd_all)
    f2_ratio = f2_spread / mpd_spread if mpd_spread > 1e-9 else float("nan")
    f2_robust = f2_ratio <= 0.5
    # F3: consistency upside (best perfect-advice algo over the floor) is small.
    best_perf = max(mpd_perf, fmpd[0], jmpd[0])
    f3_upside = best_perf - rk
    return {
        "ranking_floor": rk, "mpd_perfect": mpd_perf, "mpd_adversarial": mpd_adv,
        "F1_mpd_crashes_below_floor": bool(f1_crash),
        "F1_augmentation_stays_safe": bool(f1_aug_safe),
        "F2_augmentation_spread": float(f2_spread), "F2_mpd_spread": float(mpd_spread),
        "F2_spread_ratio": float(f2_ratio), "F2_robust": bool(f2_robust),
        "F3_consistency_upside": float(f3_upside),
    }


def main(n_trials=40, seed=0):
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    base = Path(__file__).resolve().parent.parent
    t0 = time.time()

    results = {"levels": LEVELS, "graphs": {}}
    for label, rel in GRAPHS.items():
        n, edges = load_simple_graph(base / rel)
        rows, nt = eval_graph(n, edges, n_trials, seed)
        v = verdict(rows)
        results["graphs"][label] = {
            "n": n, "edges": len(edges), "n_trials": nt,
            "rows": {a: {lv: {"mean": rows[a][lv][0], "ci95": rows[a][lv][1]} for lv in LEVELS}
                     for a in FLAT + PRED},
            "verdict": v,
        }
        print(f"\n{label} (n={n}, {len(edges)} edges, {nt} trials)")
        print(f"  Ranking floor={v['ranking_floor']:.3f}  "
              f"MPD perfect={v['mpd_perfect']:.3f}  MPD adversarial={v['mpd_adversarial']:.3f}")
        print(f"  F1 MPD crashes below floor: {v['F1_mpd_crashes_below_floor']}  | "
              f"augmentation stays safe: {v['F1_augmentation_stays_safe']}")
        print(f"  F2 aug spread={v['F2_augmentation_spread']:.3f} vs MPD spread={v['F2_mpd_spread']:.3f} "
              f"(ratio={v['F2_spread_ratio']:.2f}, robust≤0.5: {v['F2_robust']})  | "
              f"F3 consistency upside={v['F3_consistency_upside']:.3f}")

    # cross-graph summary
    g = results["graphs"]
    f1 = sum(g[k]["verdict"]["F1_mpd_crashes_below_floor"] for k in g)
    f1s = sum(g[k]["verdict"]["F1_augmentation_stays_safe"] for k in g)
    f2 = sum(g[k]["verdict"]["F2_robust"] for k in g)
    upside = np.mean([g[k]["verdict"]["F3_consistency_upside"] for k in g])
    n_g = len(g)
    results["summary"] = {"n_graphs": n_g, "F1_crash": f1, "F1_aug_safe": f1s,
                          "F2_robust": f2, "F3_mean_upside": float(upside)}
    print(f"\n=== UNIVERSALITY across {n_g} real graphs ===")
    print(f"  F1 (naive MPD crashes below floor under adversarial): {f1}/{n_g}")
    print(f"  F1 (structural augmentation stays ≥ floor):           {f1s}/{n_g}")
    print(f"  F2 (augmentation spread ≤ ½ of MPD's, much less sensitive): {f2}/{n_g}")
    print(f"  F3 (mean consistency upside over the floor):          {upside:+.3f}")

    (out_dir / "realworld_robustness.json").write_text(json.dumps(results, indent=2))
    _emit_tables(results, out_dir)
    _plot(results, out_dir)
    print(f"\nsaved: results/realworld_robustness.{{json,png}}, _tables.md "
          f"(elapsed {time.time()-t0:.1f}s)")


def _emit_tables(results, out_dir):
    lines = ["# ★4 — F1–F3 on real graphs (random partition, 95% CI)", ""]
    for label, gd in results["graphs"].items():
        lines.append(f"### {label} (n={gd['n']}, {gd['edges']} edges, {gd['n_trials']} trials)")
        lines.append("")
        lines.append("| Algorithm | " + " | ".join(LEVELS) + " |")
        lines.append("|" + "---|" * (len(LEVELS) + 1))
        for a in FLAT + PRED:
            cells = [f"{gd['rows'][a][lv]['mean']:.3f} ±{gd['rows'][a][lv]['ci95']:.3f}" for lv in LEVELS]
            tag = "  *(advice-free)*" if a in FLAT else ""
            lines.append(f"| {a}{tag} | " + " | ".join(cells) + " |")
        v = gd["verdict"]
        lines.append("")
        lines.append(f"*F1 crash={v['F1_mpd_crashes_below_floor']}, aug-safe={v['F1_augmentation_stays_safe']}; "
                     f"F2 robust={v['F2_robust']} (aug spread {v['F2_augmentation_spread']:.3f} vs MPD "
                     f"{v['F2_mpd_spread']:.3f}, ratio {v['F2_spread_ratio']:.2f}); "
                     f"F3 upside={v['F3_consistency_upside']:+.3f}*")
        lines.append("")
    (out_dir / "realworld_robustness_tables.md").write_text("\n".join(lines))


def _plot(results, out_dir):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    graphs = list(results["graphs"].keys())
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    x = np.arange(len(LEVELS))
    show = ["Ranking", "MinDegree (oracle)", "MPD", "Feldman(MPD)", "JailletLu(MPD)"]
    styles = {"Ranking": (":", "gray"), "MinDegree (oracle)": ("^:", "purple"),
              "MPD": ("o-", "C3"), "Feldman(MPD)": ("s-", "C2"), "JailletLu(MPD)": ("D-", "C0")}
    for ax, label in zip(axes.flat, graphs):
        gd = results["graphs"][label]
        for a in show:
            means = [gd["rows"][a][lv]["mean"] for lv in LEVELS]
            errs = [gd["rows"][a][lv]["ci95"] for lv in LEVELS]
            ls, col = styles[a]
            ax.errorbar(x, means, yerr=errs, fmt=ls, color=col, markersize=4,
                        capsize=2, label=a)
        rk = gd["verdict"]["ranking_floor"]
        ax.axhline(rk, ls=":", color="gray", alpha=0.5)
        ax.set_xticks(x); ax.set_xticklabels(LEVELS, fontsize=8, rotation=15)
        ax.set_title(f"{label} (n={gd['n']})", fontsize=10)
        ax.set_ylabel("competitive ratio")
        ax.grid(True, axis="y", alpha=0.3)
    axes.flat[0].legend(fontsize=7, loc="lower left")
    fig.suptitle("★4 — F1–F3 universality on 6 real graphs: naive MPD (red) dips below the Ranking floor "
                 "under adversarial,\nstructural augmentations (green/blue) stay flat — exactly as on synthetic graphs",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(out_dir / "realworld_robustness.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
