"""Arrival order as an independent variable — a bounded probe (thesis §10.3).

My proposal made arrival order an independent variable, to be reported separately
for random, adversarial and real order. The thesis works throughout in the
known-i.i.d. model, so this is the commitment it did not deliver. This script is
a PROBE in that direction, not the missing arm: for a fixed instance graph the
true adversarial order is a minimisation over all permutations, which we do not
compute. Every hostile order below is a structurally motivated heuristic, so each
reported ratio is an UPPER bound on what a real adversary could force.

Three parts:

  A. The tight construction. A graph on which arrival order ALONE moves Greedy
     between OPT and OPT/2 — the worst case its 1/2 bound is proved against.
     Does a degree prediction rescue it?

  B. Order as a variable on the thesis's own instances. Fix the instance, permute
     the arrivals: flexible-first (hostile: high-degree arrivals eat the scarce
     resources, low-degree ones starve later), random, inflexible-first
     (friendly). Same graph and same OPT throughout, so the ratios compare
     directly with Chapter 4.

  C. The prefix test under a hostile order. Chapter 6's test-and-fallback family
     estimates L1 on a sublinear PREFIX and bets that the prefix is
     representative; random arrival guarantees that, an adversary destroys it.
     Clustering arrivals by type is the natural attack. MinPredictedDegree, by
     contrast, consumes an order-independent degree ranking, so the two families
     should not degrade alike.

Outputs:
  results/arrival_order.json
  results/arrival_order_tables.md
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
from graphs.realworld import load_simple_graph, to_bipartite_random_partition
from iid_sampler import sample_instance
from optimal import max_matching_size
from algorithms.greedy import simple_greedy
from algorithms.ranking import ranking
from algorithms.min_predicted_degree import mpd
from algorithms.feldman import feldman_preprocess, feldman_online
from algorithms.jaillet_lu import jaillet_lu_preprocess, jaillet_lu_online
from algorithms.test_and_match import follow_prediction, test_and_match
from predictions.degree_truth import type_graph_degree, instance_degree
from predictions.type_advice import (
    true_type_counts, build_advice_matching, perturb_counts,
)

REAL_GRAPHS = {
    "Caltech36": "data/realworld/socfb-Caltech36/socfb-Caltech36.mtx",
    "Reed98": "data/realworld/socfb-Reed98/socfb-Reed98.mtx",
    "CE-GN": "data/realworld/bio-CE-GN/bio-CE-GN.edges",
    "CE-PG": "data/realworld/bio-CE-PG/bio-CE-PG.edges",
    "beause": "data/realworld/econ-beause/econ-beause.mtx",
    "mbeaw": "data/realworld/econ-mbeaflw/econ-mbeaflw.mtx",
}


def ci95(v) -> tuple[float, float]:
    a = np.asarray(v, dtype=float)
    if a.size == 0:
        return 0.0, 0.0
    if a.size < 2:
        return float(a.mean()), 0.0
    return float(a.mean()), float(1.96 * a.std(ddof=1) / np.sqrt(a.size))


def reorder(inst, types, idx):
    return [inst[i] for i in idx], np.asarray(types)[idx]


def order_index(inst, kind, rng):
    """flexible_first = hostile; inflexible_first = friendly; random = the model."""
    deg = np.array([len(nb) for nb in inst])
    if kind == "flexible_first":
        return np.argsort(-deg, kind="stable")
    if kind == "inflexible_first":
        return np.argsort(deg, kind="stable")
    if kind == "random":
        return rng.permutation(len(inst))
    raise ValueError(kind)


# ------------------------- A. the tight construction ----------------------

def hard_greedy_instance(m: int):
    """A graph where arrival order alone decides between OPT and OPT/2.

    Offline nodes 0..2m-1. Online node j (j<m) is adjacent to {j, m+j}; online
    node m+j is adjacent to {j} only. A perfect matching exists (j -> m+j,
    m+j -> j), so OPT = 2m. If the flexible arrivals come first, a lowest-index
    greedy takes j for each of them and every inflexible arrival then starves,
    giving exactly m. If they come last, greedy is optimal. The graph is
    identical in both cases; only the order changes.
    """
    flexible = [[j, m + j] for j in range(m)]
    inflexible = [[j] for j in range(m)]
    return flexible + inflexible, 2 * m


def part_a(m=250, n_trials=20, seed=0):
    rs = np.random.default_rng(seed)
    inst, n_right = hard_greedy_instance(m)
    opt = max_matching_size(inst, n_right)
    mu = instance_degree(inst, n_right)
    orders = {
        "flexible first (hostile)": list(range(2 * m)),
        "inflexible first (friendly)": list(range(m, 2 * m)) + list(range(m)),
    }
    rows = {}
    for oname, idx in orders.items():
        adj, _ = reorder(inst, np.zeros(2 * m, dtype=int), idx)
        g = simple_greedy(adj, n_right) / opt
        rk, mp = [], []
        for _ in range(n_trials):
            s = int(rs.integers(0, 2**31 - 1))
            rk.append(ranking(adj, n_right, np.random.default_rng(s)) / opt)
            mp.append(mpd(adj, n_right, mu, np.random.default_rng(s)) / opt)
        rows[oname] = {
            "Greedy": {"mean": g, "ci95": 0.0},
            "Ranking": dict(zip(("mean", "ci95"), ci95(rk))),
            "MPD (true degrees)": dict(zip(("mean", "ci95"), ci95(mp))),
        }
    return {"m": m, "n_right": n_right, "opt": opt, "n_trials": n_trials, "rows": rows}


# --------------- B. order as a variable on the thesis's instances ---------

B_ALGOS = ["Greedy", "Ranking", "Feldman", "JailletLu", "MPD (perfect)"]
B_ORDERS = ["inflexible_first", "random", "flexible_first"]


def part_b_family(name, build, n_arrivals, n_trials, seed):
    rg, ri, rs = np.random.default_rng(seed).spawn(3)
    acc = {o: {a: [] for a in B_ALGOS} for o in B_ORDERS}
    for _ in range(n_trials):
        type_adj, n_right = build(rg)
        m = len(type_adj) if n_arrivals is None else n_arrivals
        inst, types = sample_instance(type_adj, m=m, rng=ri)
        opt = max_matching_size(inst, n_right)
        if opt == 0:
            continue
        s = int(rs.integers(0, 2**31 - 1))
        mu = type_graph_degree(type_adj, n_right)
        Mb, Mr = feldman_preprocess(type_adj, n_right)
        rn, rp = jaillet_lu_preprocess(type_adj, n_right)
        for o in B_ORDERS:
            idx = order_index(inst, o, np.random.default_rng(s))
            adj, ty = reorder(inst, types, idx)
            acc[o]["Greedy"].append(simple_greedy(adj, n_right) / opt)
            acc[o]["Ranking"].append(
                ranking(adj, n_right, np.random.default_rng(s)) / opt)
            acc[o]["Feldman"].append(
                feldman_online(adj, ty, n_right, Mb, Mr) / opt)
            acc[o]["JailletLu"].append(
                jaillet_lu_online(adj, ty, n_right, rn, rp,
                                  np.random.default_rng(s)) / opt)
            acc[o]["MPD (perfect)"].append(
                mpd(adj, n_right, mu, np.random.default_rng(s)) / opt)
    return {"graph": name, "n_trials": len(acc["random"]["Greedy"]),
            "rows": {o: {a: dict(zip(("mean", "ci95"), ci95(acc[o][a])))
                         for a in B_ALGOS} for o in B_ORDERS}}


# ------------- C. the prefix test under a type-clustered order ------------

C_ALGOS = ["Ranking", "MPD (perfect)", "FollowPrediction",
           "TestAndMatch (Choo)", "TestAndMatch (BEM)"]


def part_c(n=2000, r=8, eta=0.15, prefix_k=200, n_trials=30, seed=3):
    """Random vs type-clustered arrival, at borderline advice quality η."""
    rg, ri, rp, rs = np.random.default_rng(seed).spawn(4)
    orders = ["random", "type_clustered"]
    acc = {o: {a: [] for a in C_ALGOS} for o in orders}
    judge = {o: {v: {"misjudge": [], "followed": []} for v in ("choo", "bem")}
             for o in orders}
    for _ in range(n_trials):
        type_adj = few_types_bipartite(n, r, rg)
        inst, types = sample_instance(type_adj, m=n, rng=ri)
        opt = max_matching_size(inst, n)
        if opt == 0:
            continue
        s = int(rs.integers(0, 2**31 - 1))
        mu = type_graph_degree(type_adj, n)
        c_star = true_type_counts(types, r)
        chat, l1 = perturb_counts(c_star, eta, rp)
        n_hat, partners = build_advice_matching(type_adj, chat, n)
        for o in orders:
            idx = (np.random.default_rng(s).permutation(n) if o == "random"
                   else np.argsort(types, kind="stable"))
            adj, ty = reorder(inst, types, idx)
            rk = ranking(adj, n, np.random.default_rng(s)) / opt
            acc[o]["Ranking"].append(rk)
            acc[o]["MPD (perfect)"].append(
                mpd(adj, n, mu, np.random.default_rng(s)) / opt)
            acc[o]["FollowPrediction"].append(
                follow_prediction(adj, ty, n, partners, chat) / opt)
            # oracle: following is the right call iff it beats the baseline here
            good = max(0.0, n_hat - n * l1 / 2.0) / opt > rk
            for v, label in (("choo", "TestAndMatch (Choo)"),
                             ("bem", "TestAndMatch (BEM)")):
                size, info = test_and_match(
                    adj, ty, n, partners, chat, n_hat,
                    rng=np.random.default_rng(s), variant=v, prefix_k=prefix_k)
                acc[o][label].append(size / opt)
                judge[o][v]["misjudge"].append(
                    0.0 if info["followed"] == good else 1.0)
                judge[o][v]["followed"].append(1.0 if info["followed"] else 0.0)
    return {"n": n, "r": r, "eta": eta, "prefix_k": prefix_k,
            "n_trials": len(acc["random"]["Ranking"]),
            "rows": {o: {a: dict(zip(("mean", "ci95"), ci95(acc[o][a])))
                         for a in C_ALGOS} for o in orders},
            "judge": {o: {v: {k: float(np.mean(judge[o][v][k]))
                              for k in ("misjudge", "followed")}
                          for v in ("choo", "bem")} for o in orders}}


# ------------------------------- rendering --------------------------------

def table(headers, rows) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def render(res) -> str:
    a = res["a"]
    L = ["# Arrival order as an independent variable (probe)", "",
         f"## A. The tight construction (m={a['m']}, OPT={a['opt']}, "
         f"{a['n_trials']} tie-break seeds)", "",
         "Same graph in both rows; only the arrival order differs.", ""]
    algos = ["Greedy", "Ranking", "MPD (true degrees)"]
    L.append(table(["Arrival order"] + algos,
                   [[o] + [f"{a['rows'][o][x]['mean']:.3f} ± {a['rows'][o][x]['ci95']:.3f}"
                           for x in algos] for o in a["rows"]]))

    L += ["## B. Order as a variable on the thesis's own instances", "",
          "inflexible-first (friendly) / random / flexible-first (hostile).", ""]
    names = {"inflexible_first": "friendly", "random": "random",
             "flexible_first": "hostile"}
    for p in res["b"]:
        L += [f"**{p['graph']}** ({p['n_trials']} trials)", ""]
        L.append(table(["Algorithm"] + list(names.values()),
                       [[x] + [f"{p['rows'][o][x]['mean']:.3f}" for o in B_ORDERS]
                        for x in B_ALGOS]))
    for key, c in res["c"].items():
        L += [f"## C. The prefix test under a type-clustered order, {key} "
              f"(n={c['n']}, r={c['r']}, k={c['prefix_k']}, "
              f"{c['n_trials']} trials)", ""]
        L.append(table(["Algorithm", "random arrival", "type-clustered arrival"],
                       [[x] + [f"{c['rows'][o][x]['mean']:.3f} ± {c['rows'][o][x]['ci95']:.3f}"
                               for o in ("random", "type_clustered")] for x in C_ALGOS]))
        L.append(table(["Test decision", "random arrival", "type-clustered arrival"],
                       [[f"{v.upper()} misjudgement rate"]
                        + [f"{c['judge'][o][v]['misjudge']:.2f}"
                           for o in ("random", "type_clustered")]
                        for v in ("choo", "bem")]
                       + [[f"{v.upper()} followed-advice rate"]
                          + [f"{c['judge'][o][v]['followed']:.2f}"
                             for o in ("random", "type_clustered")]
                          for v in ("choo", "bem")]))
    return "\n".join(L)


def main():
    t0 = time.time()
    root = Path(__file__).resolve().parent.parent
    N = 1000

    a = part_a()
    print(f"[{time.time()-t0:.0f}s] part A done", flush=True)

    b = [part_b_family("clvb_zipf",
                       lambda rng: (clvb_zipf_bipartite(N, 1.0, rng), N), N, 30, 0),
         part_b_family("left_regular d=5",
                       lambda rng: (left_regular_bipartite(N, 5, rng), N), N, 30, 1)]
    print(f"[{time.time()-t0:.0f}s] part B synthetic done", flush=True)
    for label, path in REAL_GRAPHS.items():
        n, edges = load_simple_graph(root / path)
        b.append(part_b_family(
            label,
            lambda rng, n=n, e=edges: to_bipartite_random_partition(n, e, rng),
            None, 20, 7))
        print(f"[{time.time()-t0:.0f}s] part B {label} done", flush=True)

    # eta=0 is the decisive case: the advice is PERFECT, so the right call is
    # always to follow it. eta=0.15 is Chapter 6's borderline setting.
    c = {f"eta={e}": part_c(eta=e) for e in (0.0, 0.15)}
    print(f"[{time.time()-t0:.0f}s] part C done", flush=True)

    res = {"a": a, "b": b, "c": c, "seconds": round(time.time() - t0, 1)}
    (root / "results/arrival_order.json").write_text(json.dumps(res, indent=2))
    md = render(res)
    (root / "results/arrival_order_tables.md").write_text(md)
    print(md)
    print(f"OK: {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
