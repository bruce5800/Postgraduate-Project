"""Phase 3c: the consistency/robustness envelope of adaptive test-and-fallback.

The headline figure: competitive ratio vs advice error L1(p,q), comparing
  - FollowPrediction (blind trust)  — great when advice is good, CRASHES when bad,
  - TestAndMatch (Choo / BEM)        — tracks FollowPrediction when good, but
                                       detects bad advice and falls back to the
                                       Ranking baseline, staying robust,
  - Ranking                          — the advice-free floor.

This is exactly the engineered robustness that MPD (Phase 3a) lacked: there,
adversarial predictions pushed performance *below* the baseline; here, the test
catches bad advice and bails out.

Also reports RQ3 quantities: the test's misjudgement rate and the testing cost.

Outputs:
  results/choo_bem.json
  results/choo_bem_envelope.png    ratio vs L1 (the envelope)
  results/choo_bem_prefix.png      RQ3: ratio & misjudgement vs prefix size
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graphs.synthetic import few_types_bipartite
from iid_sampler import sample_instance
from optimal import max_matching_size
from algorithms.ranking import ranking
from algorithms.test_and_match import follow_prediction, test_and_match
from predictions.type_advice import (
    true_type_counts, build_advice_matching, perturb_counts,
)


def envelope(n=2000, r=8, n_trials=40, prefix_k=200, seed=0):
    etas = np.round(np.arange(0.0, 1.01, 0.1), 2)
    rng_graph, rng_inst, rng_pert, rng_seed = np.random.default_rng(seed).spawn(4)

    rows = {k: {"l1": [], "follow": [], "bem": [], "choo": [], "ranking": [],
                "misjudge_bem": []} for k in ["agg"]}
    per_eta = []

    for eta in etas:
        l1s, fol, bem, choo, rk, misjudge = [], [], [], [], [], []
        for _ in range(n_trials):
            type_adj = few_types_bipartite(n, r, rng_graph)
            instance_adj, types = sample_instance(type_adj, m=n, rng=rng_inst)
            opt = max_matching_size(instance_adj, n_right=n)
            if opt == 0:
                continue
            c_star = true_type_counts(types, n_types=r)
            chat, l1 = perturb_counts(c_star, float(eta), rng_pert)
            n_hat, partners = build_advice_matching(type_adj, chat, n_right=n)
            s = int(rng_seed.integers(0, 2**31 - 1))

            f = follow_prediction(instance_adj, types, n, partners, chat) / opt
            b, ib = test_and_match(instance_adj, types, n, partners, chat, n_hat,
                                   rng=np.random.default_rng(s), variant="bem",
                                   prefix_k=prefix_k)
            c, ic = test_and_match(instance_adj, types, n, partners, chat, n_hat,
                                   rng=np.random.default_rng(s), variant="choo",
                                   prefix_k=prefix_k)
            rkv = ranking(instance_adj, n, np.random.default_rng(s)) / opt
            b /= opt
            c /= opt

            l1s.append(l1)
            fol.append(f)
            bem.append(b)
            choo.append(c)
            rk.append(rkv)
            # Misjudgement: the test made the wrong call if it followed advice
            # that underperforms the baseline, or rejected advice that beats it.
            good_advice = f > rkv
            misjudge.append(0.0 if ib["followed"] == good_advice else 1.0)

        per_eta.append({
            "eta": float(eta), "l1": float(np.mean(l1s)),
            "follow": float(np.mean(fol)), "bem": float(np.mean(bem)),
            "choo": float(np.mean(choo)), "ranking": float(np.mean(rk)),
            "misjudge_bem": float(np.mean(misjudge)),
        })
        print(f"  η={eta:.1f}  L1={per_eta[-1]['l1']:.3f}  "
              f"follow={per_eta[-1]['follow']:.3f}  bem={per_eta[-1]['bem']:.3f}  "
              f"choo={per_eta[-1]['choo']:.3f}  rank={per_eta[-1]['ranking']:.3f}  "
              f"misjudge={per_eta[-1]['misjudge_bem']:.2f}")
    return per_eta


def prefix_sweep(n=2000, r=8, n_trials=30, seed=1, eta=0.15):
    """RQ3: how testing cost (prefix size) trades off decision quality.
    Use BORDERLINE advice (η≈0.15) — the regime where the test must work hardest;
    clearly-good or clearly-bad advice is decided correctly even with a tiny
    prefix, so the cost only bites where the stakes are lowest."""
    ks = [25, 50, 100, 200, 400, 800]
    rng_graph, rng_inst, rng_pert, rng_seed = np.random.default_rng(seed).spawn(4)
    out = []
    for k in ks:
        bem, misjudge = [], []
        for _ in range(n_trials):
            type_adj = few_types_bipartite(n, r, rng_graph)
            instance_adj, types = sample_instance(type_adj, m=n, rng=rng_inst)
            opt = max_matching_size(instance_adj, n_right=n)
            if opt == 0:
                continue
            c_star = true_type_counts(types, n_types=r)
            chat, l1 = perturb_counts(c_star, eta, rng_pert)
            n_hat, partners = build_advice_matching(type_adj, chat, n_right=n)
            s = int(rng_seed.integers(0, 2**31 - 1))
            f = follow_prediction(instance_adj, types, n, partners, chat) / opt
            b, ib = test_and_match(instance_adj, types, n, partners, chat, n_hat,
                                   rng=np.random.default_rng(s), variant="bem",
                                   prefix_k=k)
            rkv = ranking(instance_adj, n, np.random.default_rng(s)) / opt
            bem.append(b / opt)
            misjudge.append(0.0 if ib["followed"] == (f > rkv) else 1.0)
        out.append({"k": k, "bem": float(np.mean(bem)),
                    "misjudge": float(np.mean(misjudge))})
        print(f"  prefix k={k:4d}  bem={out[-1]['bem']:.3f}  "
              f"misjudge={out[-1]['misjudge']:.2f}")
    return out


def main():
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    t0 = time.time()

    print("=== Consistency/robustness envelope (ratio vs L1) ===")
    env = envelope()
    print("\n=== RQ3: testing-cost tradeoff (prefix sweep, borderline η=0.15) ===")
    pre = prefix_sweep()

    data = {"envelope": env, "prefix_sweep": pre}
    (out_dir / "choo_bem.json").write_text(json.dumps(data, indent=2))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        l1 = [e["l1"] for e in env]
        fig, ax = plt.subplots(figsize=(9, 5.5))
        ax.plot(l1, [e["follow"] for e in env], "o--", color="C3",
                label="FollowPrediction (blind trust)")
        ax.plot(l1, [e["bem"] for e in env], "s-", color="C2",
                label="TestAndMatch (BEM)")
        ax.plot(l1, [e["choo"] for e in env], "^-", color="C0",
                label="TestAndMatch (Choo)")
        ax.plot(l1, [e["ranking"] for e in env], ":", color="gray",
                label="Ranking (advice-free floor)")
        ax.set_xlabel("advice error  L1(p, q)")
        ax.set_ylabel("competitive ratio (alg / OPT)")
        ax.set_title("Adaptive fallback keeps the upper envelope of advice & baseline\n"
                     "(blind trust crashes below the floor as advice degrades; TestAndMatch does not)")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="lower left")
        fig.savefig(out_dir / "choo_bem_envelope.png", dpi=120, bbox_inches="tight")
        plt.close(fig)

        fig, ax1 = plt.subplots(figsize=(9, 5.5))
        ks = [p["k"] for p in pre]
        ax1.plot(ks, [p["bem"] for p in pre], "s-", color="C2", label="ratio (BEM)")
        ax1.set_xlabel("prefix / testing size k")
        ax1.set_ylabel("competitive ratio", color="C2")
        ax1.set_xscale("log")
        ax2 = ax1.twinx()
        ax2.plot(ks, [p["misjudge"] for p in pre], "o--", color="C1",
                 label="misjudgement rate")
        ax2.set_ylabel("misjudgement rate", color="C1")
        ax1.set_title("RQ3: at borderline advice (η=0.15, L1≈0.16), a larger prefix estimates\n"
                      "L1 more accurately — but the worst-case-calibrated threshold then accepts\n"
                      "mildly-bad advice an oracle would reject, so accuracy hurts here")
        ax1.grid(True, alpha=0.3)
        fig.savefig(out_dir / "choo_bem_prefix.png", dpi=120, bbox_inches="tight")
        plt.close(fig)
        print("\nsaved: choo_bem_envelope.png, choo_bem_prefix.png")
    except ImportError:
        print("(matplotlib unavailable)")

    print(f"saved: results/choo_bem.json   (elapsed {time.time()-t0:.1f}s)")


if __name__ == "__main__":
    main()
