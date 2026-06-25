"""★2 — The unified head-to-head benchmark (the paper's lead contribution).

No prior work benchmarks the learning-augmented online-matching algorithms
*together*: ACI (MPD / degree predictions), Choo & BEM (type-histogram advice,
test-and-fallback), and the classic advice-free baselines were each studied in
isolation, on their own graphs, with their own error models. This script puts
them on ONE harness — shared graphs, a shared prediction-quality knob, shared OPT,
and a shared confidence-interval methodology — and reports one rigorous
head-to-head table per graph family.

It also includes a Chłędowski-style dynamic switching **combiner** as a BASELINE
(not a contribution): the "blind-follow + baseline with switching" insurance that
the caching literature already established empirically — here benchmarked against
the one-shot test-and-fallback algorithms.

Honest scope note. The algorithm families consume DIFFERENT prediction objects
(degree vectors μ vs type-count histograms ĉ); there is no single scalar that
makes them strictly comparable. We therefore unify on a per-family *corruption
knob* and present the families in parallel panels with a common methodology — and
flag this heterogeneity explicitly, since it is exactly why no unified benchmark
existed before.

Panels:
  A. clvb_zipf  (n=1000) — heavy-tailed degrees; the degree-prediction regime.
  B. left_regular d=5 (n=1000) — homogeneous degrees; predictions add little.
  C. few_types r=8 (n=2000) — near-perfect-matchable; the type-advice regime
     (FollowPrediction / Choo / BEM / Combiner).

Outputs:
  results/unified_benchmark.json
  results/unified_benchmark_tables.md   (machine-generated tables, CI = 95%)
  results/unified_benchmark.png          (grouped summary bars)
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.synthetic import (
    clvb_zipf_bipartite, left_regular_bipartite, few_types_bipartite,
)
from iid_sampler import sample_instance
from optimal import max_matching_size
from algorithms.greedy import simple_greedy
from algorithms.ranking import ranking
from algorithms.feldman import feldman_preprocess, feldman_online, feldman_online_mpd
from algorithms.jaillet_lu import (
    jaillet_lu_preprocess, jaillet_lu_online, jaillet_lu_online_mpd,
)
from algorithms.min_predicted_degree import mpd, mpd_rank
from algorithms.test_and_match import follow_prediction, test_and_match
from algorithms.combiner import combiner
from predictions.degree_truth import type_graph_degree, instance_degree
from predictions import error_models as em
from predictions.type_advice import (
    true_type_counts, build_advice_matching, perturb_counts,
)


# ----------------------------- statistics ---------------------------------

def ci95(values) -> tuple[float, float]:
    """Return (mean, 95% half-width) over trials (normal approx, ddof=1)."""
    a = np.asarray(values, dtype=float)
    n = a.size
    if n == 0:
        return 0.0, 0.0
    m = float(a.mean())
    if n < 2:
        return m, 0.0
    se = a.std(ddof=1) / np.sqrt(n)
    return m, float(1.96 * se)


def _cell(values) -> dict:
    m, h = ci95(values)
    return {"mean": m, "ci95": h, "n": len(values)}


# --------------------------- degree-prediction panels ----------------------

# Quality columns for the degree family: a true predictor, an honestly-noisy one,
# the order-reversing adversarial worst case, and a fully-random (≡Ranking) one.
DEGREE_LEVELS = ["perfect", "noisy", "adversarial", "garbage"]


def _degree_predictor(level: str, mu_true: np.ndarray, rng: np.random.Generator):
    if level == "perfect":
        return mu_true
    if level == "noisy":
        return em.random_flip(mu_true, 0.5, rng)[0]
    if level == "adversarial":
        return em.adversarial(mu_true, 1.0, rng)[0]
    if level == "garbage":
        return em.random_flip(mu_true, 1.0, rng)[0]
    raise ValueError(level)


def run_degree_panel(name, gen, n, n_trials, seed):
    """Greedy/Ranking/Feldman/JailletLu (advice-free) + MPD/Feldman(MPD)/
    JailletLu(MPD) (degree predictions) + MinDegree oracle anchor."""
    rng_graph, rng_inst, rng_seed, rng_pert = np.random.default_rng(seed).spawn(4)

    # advice-free algorithms: one value per trial (prediction-independent)
    flat = {a: [] for a in ["SimpleGreedy", "Ranking", "Feldman", "JailletLu",
                            "MinDegree (oracle)"]}
    # prediction algorithms: one list per (algo, level)
    pred_algos = ["MPD", "Feldman(MPD)", "JailletLu(MPD)"]
    swept = {a: {lv: [] for lv in DEGREE_LEVELS} for a in pred_algos}

    for _ in range(n_trials):
        type_adj = gen(rng_graph)
        instance_adj, types = sample_instance(type_adj, m=n, rng=rng_inst)
        opt = max_matching_size(instance_adj, n_right=n)
        if opt == 0:
            continue
        ts = int(rng_seed.integers(0, 2**31 - 1))
        mu_true = type_graph_degree(type_adj, n_right=n)
        mu_real = instance_degree(instance_adj, n_right=n)
        Mb, Mr = feldman_preprocess(type_adj, n_right=n)
        rn, rp = jaillet_lu_preprocess(type_adj, n_right=n)

        flat["SimpleGreedy"].append(simple_greedy(instance_adj, n) / opt)
        flat["Ranking"].append(ranking(instance_adj, n, np.random.default_rng(ts)) / opt)
        flat["Feldman"].append(feldman_online(instance_adj, types, n, Mb, Mr) / opt)
        flat["JailletLu"].append(
            jaillet_lu_online(instance_adj, types, n, rn, rp, np.random.default_rng(ts)) / opt)
        flat["MinDegree (oracle)"].append(
            mpd(instance_adj, n, mu_real, np.random.default_rng(ts)) / opt)

        for lv in DEGREE_LEVELS:
            mu_p = _degree_predictor(lv, mu_true, rng_pert)
            rank = mpd_rank(mu_p, np.random.default_rng(ts))
            swept["MPD"][lv].append(mpd(instance_adj, n, mu_p, np.random.default_rng(ts)) / opt)
            swept["Feldman(MPD)"][lv].append(
                feldman_online_mpd(instance_adj, types, n, Mb, Mr, rank) / opt)
            swept["JailletLu(MPD)"][lv].append(
                jaillet_lu_online_mpd(instance_adj, types, n, rn, rp,
                                      np.random.default_rng(ts), rank) / opt)

    rows = {a: {lv: _cell(flat[a]) for lv in DEGREE_LEVELS} for a in flat}  # flat → same across cols
    for a in pred_algos:
        rows[a] = {lv: _cell(swept[a][lv]) for lv in DEGREE_LEVELS}
    return {"kind": "degree", "graph": name, "n": n,
            "n_trials": len(flat["Ranking"]), "levels": DEGREE_LEVELS,
            "flat_algos": list(flat.keys()), "pred_algos": pred_algos, "rows": rows}


# ------------------------------ advice panel -------------------------------

ADVICE_LEVELS = [("perfect", 0.0), ("mild", 0.3), ("bad", 0.6), ("garbage", 1.0)]


def run_advice_panel(n=2000, r=8, n_trials=50, prefix_k=200, seed=2):
    """Ranking floor + MPD(true degree) cross-ref + the type-advice family
    (FollowPrediction / Choo / BEM / Combiner) across advice quality η."""
    rng_graph, rng_inst, rng_seed, rng_pert = np.random.default_rng(seed).spawn(4)
    level_names = [lv for lv, _ in ADVICE_LEVELS]

    flat = {a: [] for a in ["Ranking", "MPD (true degrees)"]}
    advice_algos = ["FollowPrediction", "TestAndMatch (Choo)",
                    "TestAndMatch (BEM)", "Combiner"]
    swept = {a: {lv: [] for lv in level_names} for a in advice_algos}

    # Pre-generate paired trials (OPT independent of advice quality).
    trials = []
    for _ in range(n_trials):
        type_adj = few_types_bipartite(n, r, rng_graph)
        instance_adj, types = sample_instance(type_adj, m=n, rng=rng_inst)
        opt = max_matching_size(instance_adj, n_right=n)
        if opt == 0:
            continue
        ts = int(rng_seed.integers(0, 2**31 - 1))
        c_star = true_type_counts(types, n_types=r)
        mu_true = type_graph_degree(type_adj, n_right=n)
        flat["Ranking"].append(ranking(instance_adj, n, np.random.default_rng(ts)) / opt)
        flat["MPD (true degrees)"].append(
            mpd(instance_adj, n, mu_true, np.random.default_rng(ts)) / opt)
        trials.append((type_adj, instance_adj, types, opt, c_star, ts))

    for lv, eta in ADVICE_LEVELS:
        for (type_adj, instance_adj, types, opt, c_star, ts) in trials:
            chat, _l1 = perturb_counts(c_star, float(eta), rng_pert)
            n_hat, partners = build_advice_matching(type_adj, chat, n_right=n)
            swept["FollowPrediction"][lv].append(
                follow_prediction(instance_adj, types, n, partners, chat) / opt)
            c, _ = test_and_match(instance_adj, types, n, partners, chat, n_hat,
                                  rng=np.random.default_rng(ts), variant="choo",
                                  prefix_k=prefix_k)
            swept["TestAndMatch (Choo)"][lv].append(c / opt)
            b, _ = test_and_match(instance_adj, types, n, partners, chat, n_hat,
                                  rng=np.random.default_rng(ts), variant="bem",
                                  prefix_k=prefix_k)
            swept["TestAndMatch (BEM)"][lv].append(b / opt)
            # γ in its intended "cheap insurance" tuning (scales with n): large
            # enough to avoid the irrevocable mid-stream hybrid penalty, so the
            # combiner cleanly captures the robustness floor. See report §"combiner"
            # for the small-γ pathology (switching dips BELOW the baseline).
            cm, _ = combiner(instance_adj, types, n, partners, chat,
                             rng=np.random.default_rng(ts), gamma=max(20, n // 40))
            swept["Combiner"][lv].append(cm / opt)

    rows = {a: {lv: _cell(flat[a]) for lv in level_names} for a in flat}
    for a in advice_algos:
        rows[a] = {lv: _cell(swept[a][lv]) for lv in level_names}
    return {"kind": "advice", "graph": f"few_types (r={r})", "n": n,
            "n_trials": len(trials), "levels": level_names,
            "flat_algos": list(flat.keys()), "pred_algos": advice_algos, "rows": rows}


# ------------------------------ presentation -------------------------------

def panel_to_md(panel) -> str:
    lv = panel["levels"]
    head = "| Algorithm | " + " | ".join(lv) + " |"
    sep = "|" + "---|" * (len(lv) + 1)
    lines = [f"### {panel['graph']}  (n={panel['n']}, {panel['n_trials']} trials, "
             f"{'degree-prediction' if panel['kind']=='degree' else 'type-advice'} regime)",
             "", head, sep]
    order = panel["flat_algos"] + panel["pred_algos"]
    for a in order:
        cells = []
        for l in lv:
            c = panel["rows"][a][l]
            cells.append(f"{c['mean']:.3f} ±{c['ci95']:.3f}")
        tag = "  *(advice-free)*" if a in panel["flat_algos"] else ""
        lines.append(f"| {a}{tag} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    t0 = time.time()
    N = 1000

    print("=== Panel A: clvb_zipf (degree-prediction regime) ===")
    panel_a = run_degree_panel(
        "clvb_zipf", lambda rng: clvb_zipf_bipartite(N, 1.0, rng), N, n_trials=60, seed=0)
    print("=== Panel B: left_regular d=5 (homogeneous regime) ===")
    panel_b = run_degree_panel(
        "left_regular_d5", lambda rng: left_regular_bipartite(N, 5, rng), N, n_trials=60, seed=1)
    print("=== Panel C: few_types (type-advice regime) ===")
    panel_c = run_advice_panel(n=2000, r=8, n_trials=50, prefix_k=200, seed=2)

    panels = [panel_a, panel_b, panel_c]
    (out_dir / "unified_benchmark.json").write_text(json.dumps(panels, indent=2))

    md = ["# Unified benchmark — machine-generated tables (95% CI)", "",
          "Auto-emitted by `scripts/run_unified_benchmark.py`. Cells are mean "
          "competitive ratio (alg/OPT) ± 95% half-width over trials.", ""]
    for p in panels:
        md.append(panel_to_md(p)); md.append("")
        # console echo
        print("\n" + panel_to_md(p))
    (out_dir / "unified_benchmark_tables.md").write_text("\n".join(md))

    # Summary figure: one grouped-bar subplot per panel.
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 3, figsize=(19, 5.6))
        for ax, p in zip(axes, panels):
            lv = p["levels"]
            order = p["flat_algos"] + p["pred_algos"]
            x = np.arange(len(lv))
            w = 0.8 / len(order)
            for j, a in enumerate(order):
                means = [p["rows"][a][l]["mean"] for l in lv]
                errs = [p["rows"][a][l]["ci95"] for l in lv]
                ax.bar(x + j * w, means, w, yerr=errs, capsize=2, label=a)
            ax.set_xticks(x + 0.4 - w / 2)
            ax.set_xticklabels(lv, fontsize=9)
            ax.set_ylim(0.4, 1.02)
            ax.set_title(f"{p['graph']}\n({'degree predictions' if p['kind']=='degree' else 'type advice'})",
                         fontsize=10)
            ax.set_ylabel("competitive ratio")
            ax.grid(True, axis="y", alpha=0.3)
            ax.legend(fontsize=6.5, loc="lower left", ncol=2)
        fig.suptitle("Unified benchmark: every learning-augmented matching algorithm on one harness, "
                     "across prediction quality (95% CI)", fontsize=12)
        fig.tight_layout()
        fig.savefig(out_dir / "unified_benchmark.png", dpi=120, bbox_inches="tight")
        plt.close(fig)
        print("\nsaved: unified_benchmark.png")
    except ImportError:
        print("(matplotlib unavailable)")

    print(f"saved: results/unified_benchmark.{{json,png}}, unified_benchmark_tables.md "
          f"(elapsed {time.time()-t0:.1f}s)")


if __name__ == "__main__":
    main()
