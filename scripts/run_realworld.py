"""Real-world graph validation (Borodin et al. 2018 Tables 3 & 4) + MPD extension.

For each Network Repository graph, both bipartite conversions are applied and
the i.i.d. instance ratios are compared against the paper's reported values.
We add MPD and MinDegree columns (the Phase 3 extension; ACI also evaluated
real graphs).

  random partition  → Borodin Table 3
  duplicating       → Borodin Table 4

Paper reference values are embedded for side-by-side comparison.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.realworld import (
    load_simple_graph, to_bipartite_duplicating, to_bipartite_random_partition,
)
from iid_sampler import sample_instance
from optimal import max_matching_size
from algorithms.greedy import simple_greedy
from algorithms.ranking import ranking
from algorithms.min_predicted_degree import mpd, mpd_rank
from algorithms.feldman import feldman_preprocess, feldman_online, feldman_online_greedy
from algorithms.jaillet_lu import (
    jaillet_lu_preprocess, jaillet_lu_online, jaillet_lu_online_greedy,
)
from predictions.degree_truth import type_graph_degree, instance_degree


# Graph files (dataset label used in the paper → file path).
GRAPHS = {
    "Caltech36": "data/realworld/socfb-Caltech36/socfb-Caltech36.mtx",
    "Reed98": "data/realworld/socfb-Reed98/socfb-Reed98.mtx",
    "CE-GN": "data/realworld/bio-CE-GN/bio-CE-GN.edges",
    "CE-PG": "data/realworld/bio-CE-PG/bio-CE-PG.edges",
    "beause": "data/realworld/econ-beause/econ-beause.mtx",
    "mbeaw": "data/realworld/econ-mbeaflw/econ-mbeaflw.mtx",
}

# Paper reference (SG, Rk, F, Fg, J, Jg) — Borodin Tables 3 (random) & 4 (dup).
PAPER = {
    "random": {
        "Caltech36": (0.87, 0.86, 0.78, 0.91, 0.81, 0.91),
        "Reed98": (0.87, 0.87, 0.78, 0.91, 0.81, 0.91),
        "CE-GN": (0.93, 0.93, 0.78, 0.94, 0.80, 0.94),
        "CE-PG": (0.94, 0.94, 0.81, 0.96, 0.82, 0.96),
        "beause": (0.94, 0.94, 0.76, 0.94, 0.78, 0.95),
        "mbeaw": (0.95, 0.95, 0.74, 0.95, 0.77, 0.96),
    },
    "duplicating": {
        "Caltech36": (0.72, 0.86, 0.77, 0.90, 0.79, 0.90),
        "Reed98": (0.72, 0.86, 0.77, 0.90, 0.79, 0.90),
        "CE-GN": (0.95, 0.93, 0.77, 0.95, 0.79, 0.95),
        "CE-PG": (0.95, 0.94, 0.80, 0.95, 0.81, 0.96),
        "beause": (0.91, 0.94, 0.74, 0.94, 0.77, 0.95),
        "mbeaw": (0.94, 0.97, 0.73, 0.97, 0.76, 0.97),
    },
}

ALGOS = ["SG", "Rk", "F", "Fg", "J", "Jg", "MPD", "MinDeg"]


def eval_graph(n, edges, conversion, n_trials, seed):
    rg, ri, rj = np.random.default_rng(seed).spawn(3)
    # For duplicating the type graph is fixed; build once.
    fixed = None
    if conversion == "duplicating":
        fixed = to_bipartite_duplicating(n, edges)

    acc = {a: [] for a in ALGOS}
    for _ in range(n_trials):
        ta, nr = fixed if fixed else to_bipartite_random_partition(n, edges, rg)
        Mb, Mr = feldman_preprocess(ta, nr)
        rn, rp = jaillet_lu_preprocess(ta, nr)
        mu = type_graph_degree(ta, nr)
        inst, types = sample_instance(ta, m=len(ta), rng=ri)
        opt = max_matching_size(inst, nr)
        if opt == 0:
            continue
        mu_real = instance_degree(inst, nr)
        s = int(rj.integers(0, 2**31 - 1))
        rank = mpd_rank(mu, np.random.default_rng(s))
        acc["SG"].append(simple_greedy(inst, nr) / opt)
        acc["Rk"].append(ranking(inst, nr, np.random.default_rng(s)) / opt)
        acc["F"].append(feldman_online(inst, types, nr, Mb, Mr) / opt)
        acc["Fg"].append(feldman_online_greedy(inst, types, nr, Mb, Mr) / opt)
        acc["J"].append(jaillet_lu_online(inst, types, nr, rn, rp, np.random.default_rng(s)) / opt)
        acc["Jg"].append(jaillet_lu_online_greedy(inst, types, nr, rn, rp, np.random.default_rng(s)) / opt)
        acc["MPD"].append(mpd(inst, nr, mu, np.random.default_rng(s)) / opt)
        acc["MinDeg"].append(mpd(inst, nr, mu_real, np.random.default_rng(s)) / opt)
    return {a: float(np.mean(acc[a])) for a in ALGOS}


def main(n_trials=50, seed=0):
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    base = Path(__file__).resolve().parent.parent
    results = {}
    t0 = time.time()

    for conversion in ["random", "duplicating"]:
        conv_key = "random" if conversion == "random" else "duplicating"
        print(f"\n{'='*78}\n{conversion.upper()} CONVERSION  "
              f"(vs Borodin Table {'3' if conversion=='random' else '4'})\n{'='*78}")
        print(f"{'graph':10s} | {'algo':6s} | {'ours':>6s} {'paper':>6s} {'Δ':>6s}    "
              f"| MPD/MinDeg (Phase 3 ext.)")
        results[conversion] = {}
        for label, rel in GRAPHS.items():
            n, edges = load_simple_graph(base / rel)
            conv_name = "random" if conversion == "random" else "duplicating"
            res = eval_graph(n, edges, conv_name, n_trials, seed)
            results[conversion][label] = res
            paper = PAPER[conv_key][label]
            paper_map = dict(zip(["SG", "Rk", "F", "Fg", "J", "Jg"], paper))
            deltas = []
            for a in ["SG", "Rk", "F", "Fg", "J", "Jg"]:
                d = res[a] - paper_map[a]
                deltas.append(abs(d))
            maxd = max(deltas)
            flag = "  <-- large Δ" if maxd > 0.06 else ""
            print(f"{label:10s} | n={n:5d} edges={len(edges):6d}  maxΔ={maxd:.3f}{flag}")
            for a in ["SG", "Rk", "F", "Fg", "J", "Jg"]:
                d = res[a] - paper_map[a]
                mark = " *" if abs(d) > 0.06 else ""
                print(f"           | {a:6s} | {res[a]:6.3f} {paper_map[a]:6.3f} {d:+6.3f}{mark}")
            print(f"           | MPD={res['MPD']:.3f}  MinDeg={res['MinDeg']:.3f}")

    (out_dir / "realworld.json").write_text(json.dumps(results, indent=2))
    print(f"\nsaved: results/realworld.json    (elapsed {time.time()-t0:.1f}s)")


if __name__ == "__main__":
    main()
