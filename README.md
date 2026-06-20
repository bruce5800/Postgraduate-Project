# matching-experiments

Experimental study of algorithms for online bipartite matching under the
known-i.i.d. input model, building toward a thesis on
**learning-augmented (prediction-based)** online matching.

Phase 1–2 reproduces a subset of Borodin, Karavasilis & Pankratov,
*"An Experimental Study of Algorithms for Online Bipartite Matching"*,
[arXiv:1808.04863](https://arxiv.org/pdf/1808.04863). Phase 3 will extend the
benchmark with prediction-based algorithms (MinPredictedDegree, the Choo et al.
framework, etc.).

See [`docs/PHASE2_REPORT.md`](docs/PHASE2_REPORT.md) for the full reproduction
report and result analysis.

## Status

| Phase | Goal | Status |
|---|---|---|
| 1 | Scaffolding + first verified number | done |
| 2 | Core 4 algorithms + ER & Left-Regular reproduction | done |
| 3a | MinPredictedDegree + 4 error models + RQ2 spectrum | done — see [`docs/PHASE3_REPORT.md`](docs/PHASE3_REPORT.md) |
| 3b | (MPD)-augmented Feldman/JailletLu comparison | done — (MPD)≥(g)≥base confirmed |
| 3d | Real-world graphs (Borodin Tables 3/4 + MPD) | done — random-partition validated; MPD tops all 6 graphs |
| 3c | Choo (TestAndMatch) + BEM adaptive fallback | done — robustness envelope + threshold-miscalibration finding + recalibration fix ([`docs/PHASE3C_REPORT.md`](docs/PHASE3C_REPORT.md)) |
| 4 | AI inference serving instantiation (online b-matching) | done — capacity-c routing + traffic forecasts; "capacity is the safe substitute" finding, hardened on a real Wikipedia trace (forecast staleness) ([`docs/PHASE4_SERVING_REPORT.md`](docs/PHASE4_SERVING_REPORT.md)) |

## Directory layout

```
matching-experiments/
├── optimal.py              # Hopcroft–Karp via NetworkX (OPT)
├── iid_sampler.py          # type graph → i.i.d. instance
├── graphs/
│   └── synthetic.py        # ER, left-regular bipartite generators
├── algorithms/
│   ├── _common.py          # GreedyWithPermutation primitive
│   ├── greedy.py           # SimpleGreedy
│   ├── ranking.py          # Ranking (KVV)
│   ├── feldman.py          # FeldmanEtAl + greedy variant + blue-red decomp
│   └── jaillet_lu.py       # JailletLu + greedy variant + cap-3 max-flow LP
├── tests/                  # hand-verifiable correctness tests
├── scripts/                # smoke tests and full experiment drivers
├── results/                # JSON + PNG outputs (gitignore in real use)
└── docs/
    ├── PHASE2_REPORT.md, PHASE3_REPORT.md, PHASE3C_REPORT.md, ...
    ├── VISUAL_GUIDE.md     # browser-openable explainers for talks/thesis
    └── visuals/            # standalone interactive HTML visuals
```

For explaining the work to a non-technical audience (advisor, examiners), see
[`docs/VISUAL_GUIDE.md`](docs/VISUAL_GUIDE.md) — standalone interactive HTML
visuals: an online-matching explainer and a real-world applications map.

## Dependencies

```
Python 3.12
numpy 1.26+      # spawn-based RNG streams
scipy 1.13
networkx 3.3
matplotlib       # plots only
```

No installation script — every dependency is in the conda/pip stdlib
distribution we assume.

## Running experiments

From the project root:

```bash
# fast smoke tests (< 5s each)
python3 scripts/smoke_er.py
python3 scripts/smoke_er_curve.py

# unit tests
python3 tests/test_feldman_small.py
python3 tests/test_jaillet_lu_small.py

# full reproduction runs (~10-20 min each)
python3 scripts/run_er_full.py            # Fig 9 partial: 6 algos, 75 c-values
python3 scripts/run_left_regular.py       # Fig 18 partial: 6 algos, 30 d-values
```

Each script:
- writes `results/<name>.json` (raw means + std per parameter value)
- writes `results/<name>.png` (plot)
- prints per-step progress with ETA

## Reproducing a single result

The scripts are deterministic given a seed. To reproduce
[`results/er_full.png`](results/er_full.png) exactly:

```bash
python3 scripts/run_er_full.py    # defaults: n=1000, n_trials=100, seed=0
```

## Design notes

See [`docs/PHASE2_REPORT.md`](docs/PHASE2_REPORT.md) for:
- Implementation rationale (Python vs C++ trade-off, NetworkX max-flow vs C
  Edmonds-Karp, RNG stream design)
- Algorithm-by-algorithm verification against paper claims
- Limitations and what's intentionally not reproduced
