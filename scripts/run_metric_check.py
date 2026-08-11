"""Methodology check behind §3.1 and §3.5.

Two questions the thesis has to answer about how it reports numbers:

  §3.1  We average per-instance ratios, i.e. we report E[ALG/OPT]. How far is that
        from the ratio of expectations E[ALG]/E[OPT] on our own instances?
  §3.5  Trials are paired (same graph, same arrivals, same OPT, same tie-break seed),
        but the tables carry per-algorithm confidence intervals. How much tighter is
        the paired-difference interval for the comparisons the thesis actually draws?

Setup mirrors the unified benchmark exactly: Panel A (clvb_zipf, n=1000, 60 trials,
seed 0) and Panel C (few-types r=8, n=2000, 50 trials, seed 2).

Outputs: results/metric_check.json (+ printed table)
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.synthetic import clvb_zipf_bipartite, few_types_bipartite
from iid_sampler import sample_instance
from optimal import max_matching_size
from algorithms.ranking import ranking
from algorithms.feldman import feldman_preprocess, feldman_online_mpd
from algorithms.min_predicted_degree import mpd, mpd_rank
from algorithms.test_and_match import follow_prediction, test_and_match
from predictions.degree_truth import type_graph_degree
from predictions import error_models as em
from predictions.type_advice import (
    true_type_counts, build_advice_matching, perturb_counts,
)


def ci95(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()), float(1.96 * a.std(ddof=1) / np.sqrt(a.size))


def summarize(name, alg_counts, opt_counts):
    """Both estimators of the competitive ratio, plus the per-algorithm interval."""
    alg = np.asarray(alg_counts, dtype=float)
    opt = np.asarray(opt_counts, dtype=float)
    mean_of_ratio, half = ci95(alg / opt)
    ratio_of_means = float(alg.sum() / opt.sum())
    return {"algorithm": name, "mean_of_ratios": mean_of_ratio, "ci95": half,
            "ratio_of_means": ratio_of_means,
            "difference": mean_of_ratio - ratio_of_means}


def paired(name, a_counts, b_counts, opt_counts, rows):
    """Independent vs paired interval for the difference between two algorithms."""
    opt = np.asarray(opt_counts, dtype=float)
    ra = np.asarray(a_counts, dtype=float) / opt
    rb = np.asarray(b_counts, dtype=float) / opt
    ma, ha = ci95(ra)
    mb, hb = ci95(rb)
    d, hd = ci95(ra - rb)
    corr = (float(np.corrcoef(ra, rb)[0, 1])
            if ra.std() > 0 and rb.std() > 0 else None)   # None: one side is constant
    rows.append({"comparison": name, "difference": d,
                 "independent_halfwidth": float(np.hypot(ha, hb)),
                 "paired_halfwidth": hd,
                 "tightening": float(np.hypot(ha, hb) / hd) if hd > 0 else float("inf"),
                 "corr": corr})


def panel_a(n=1000, n_trials=60, seed=0):
    rng_graph, rng_inst, rng_seed, rng_pert = np.random.default_rng(seed).spawn(4)
    keep = {k: [] for k in ["opt", "Ranking", "MPD/perfect", "MPD/adversarial",
                            "Feldman(MPD)/perfect", "Feldman(MPD)/adversarial"]}
    for _ in range(n_trials):
        type_adj = clvb_zipf_bipartite(n, 1.0, rng_graph)
        instance_adj, types = sample_instance(type_adj, m=n, rng=rng_inst)
        opt = max_matching_size(instance_adj, n_right=n)
        if opt == 0:
            continue
        ts = int(rng_seed.integers(0, 2**31 - 1))
        mu_true = type_graph_degree(type_adj, n_right=n)
        Mb, Mr = feldman_preprocess(type_adj, n_right=n)
        keep["opt"].append(opt)
        keep["Ranking"].append(ranking(instance_adj, n, np.random.default_rng(ts)))
        for lv, mu_p in (("perfect", mu_true),
                         ("adversarial", em.adversarial(mu_true, 1.0, rng_pert)[0])):
            rank = mpd_rank(mu_p, np.random.default_rng(ts))
            keep[f"MPD/{lv}"].append(mpd(instance_adj, n, mu_p, np.random.default_rng(ts)))
            keep[f"Feldman(MPD)/{lv}"].append(
                feldman_online_mpd(instance_adj, types, n, Mb, Mr, rank))
    return keep


def panel_c(n=2000, r=8, n_trials=50, prefix_k=200, seed=2):
    rng_graph, rng_inst, rng_seed, rng_pert = np.random.default_rng(seed).spawn(4)
    keep = {k: [] for k in ["opt", "Ranking", "FollowPrediction/garbage",
                            "TestAndMatch(Choo)/perfect", "TestAndMatch(Choo)/garbage"]}
    trials = []
    for _ in range(n_trials):
        type_adj = few_types_bipartite(n, r, rng_graph)
        instance_adj, types = sample_instance(type_adj, m=n, rng=rng_inst)
        opt = max_matching_size(instance_adj, n_right=n)
        if opt == 0:
            continue
        ts = int(rng_seed.integers(0, 2**31 - 1))
        keep["opt"].append(opt)
        keep["Ranking"].append(ranking(instance_adj, n, np.random.default_rng(ts)))
        trials.append((type_adj, instance_adj, types, opt, true_type_counts(types, n_types=r), ts))

    for lv, eta in (("perfect", 0.0), ("garbage", 1.0)):
        for (type_adj, instance_adj, types, opt, c_star, ts) in trials:
            chat, _ = perturb_counts(c_star, float(eta), rng_pert)
            n_hat, partners = build_advice_matching(type_adj, chat, n_right=n)
            c, _ = test_and_match(instance_adj, types, n, partners, chat, n_hat,
                                  rng=np.random.default_rng(ts), variant="choo",
                                  prefix_k=prefix_k)
            keep[f"TestAndMatch(Choo)/{lv}"].append(c)
            if lv == "garbage":
                keep["FollowPrediction/garbage"].append(
                    follow_prediction(instance_adj, types, n, partners, chat))
    return keep


def main():
    t0 = time.time()
    out = {"panels": {}, "paired": []}
    for label, keep in (("A (clvb_zipf, n=1000, 60 trials)", panel_a()),
                        ("C (few-types r=8, n=2000, 50 trials)", panel_c())):
        opt = keep.pop("opt")
        rows = [summarize(k, v, opt) for k, v in keep.items()]
        out["panels"][label] = {"n_trials": len(opt), "rows": rows}
        print(f"\nPanel {label}: {len(opt)} trials")
        print(f"  {'algorithm':<28} {'mean of ratios':>14} {'ratio of means':>15} {'diff':>9}")
        for r in rows:
            print(f"  {r['algorithm']:<28} {r['mean_of_ratios']:>14.4f} "
                  f"{r['ratio_of_means']:>15.4f} {r['difference']:>+9.5f}")
        keep["opt"] = opt

    a, c = panel_a(), panel_c()
    rows = []
    paired("Panel A: MPD(adversarial) vs Ranking", a["MPD/adversarial"], a["Ranking"], a["opt"], rows)
    paired("Panel A: Feldman(MPD) perfect vs adversarial",
           a["Feldman(MPD)/perfect"], a["Feldman(MPD)/adversarial"], a["opt"], rows)
    paired("Panel C: FollowPrediction(garbage) vs Ranking",
           c["FollowPrediction/garbage"], c["Ranking"], c["opt"], rows)
    paired("Panel C: TestAndMatch(perfect) vs Ranking",
           c["TestAndMatch(Choo)/perfect"], c["Ranking"], c["opt"], rows)
    out["paired"] = rows
    print(f"\n  {'comparison':<46} {'diff':>8} {'indep ±':>9} {'paired ±':>9} {'×tighter':>9} {'corr':>6}")
    for r in rows:
        print(f"  {r['comparison']:<46} {r['difference']:>+8.4f} {r['independent_halfwidth']:>9.4f} "
              f"{r['paired_halfwidth']:>9.4f} {r['tightening']:>9.1f} "
              + ("  n/a" if r['corr'] is None else f"{r['corr']:>6.2f}"))

    biggest = max(abs(r["difference"]) for p in out["panels"].values() for r in p["rows"])
    out["max_abs_estimator_difference"] = biggest
    print(f"\nlargest |E[ALG/OPT] - E[ALG]/E[OPT]| across all cells: {biggest:.5f}")

    res = Path(__file__).resolve().parent.parent / "results"
    res.mkdir(exist_ok=True)
    (res / "metric_check.json").write_text(json.dumps(out, indent=2))
    print(f"saved: results/metric_check.json  (elapsed {time.time()-t0:.1f}s)")


if __name__ == "__main__":
    main()
