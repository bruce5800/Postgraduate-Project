# Code submission — The Limits of Predictions for Online Bipartite Matching

This archive contains the code and empirical artifacts supporting the MSc thesis
*The Limits of Predictions for Online Bipartite Matching: A Unified Experimental Study*.
It intentionally excludes the separate companion-paper manuscript and its Lean
formalization of the budget–stakes law.

## Contents

- `algorithms/`, `graphs/`, `predictions/`: algorithm and instance implementations.
- `optimal.py`, `iid_sampler.py`: offline optima and i.i.d. arrival sampling.
- `scripts/`: drivers for the figures, tables, and checks cited by the thesis.
- `tests/`: small, hand-verifiable correctness tests.
- `results/`: the seeded JSON, PNG, and table outputs reported in the thesis.
- `data/trace/`: the exact trace snapshots used in Chapters 7–9.
- `REPRODUCTION.md`: figure/table-to-script map, commands, runtimes, and provenance.

## Requirements

Use Python 3.12. Install the Python dependencies with:

```bash
python3 -m pip install -r requirements.txt
```

All commands must be run from the archive root.

## Quick verification

Run the eight small correctness tests:

```bash
for t in tests/test_*.py; do python3 "$t"; done
```

Representative fast reproductions are:

```bash
python3 scripts/run_unified_benchmark.py
python3 scripts/plot_unified_panels.py
python3 scripts/run_order_vs_theory.py
python3 scripts/run_impossibility_frontier.py
```

See `REPRODUCTION.md` for the complete map and commands. Some full sweeps take about
20 minutes on the reference machine described there.

## External real-graph data

The six Network Repository graphs used in Chapter 7 and the reproduction validation
are third-party data and are not redistributed in this archive. The affected scripts
are `run_realworld.py`, `run_realworld_robustness.py`, and the real-graph portion of
`run_streaming_ladder.py`. Download the following datasets from Network Repository and
place their extracted files under `data/realworld/<dataset-name>/`:

- `socfb-Caltech36`
- `socfb-Reed98`
- `bio-CE-GN`
- `bio-CE-PG`
- `econ-beause`
- `econ-mbeaflw`

The shipped `results/` files preserve the outputs obtained from those datasets. All
synthetic experiments and the experiments using the shipped trace snapshots run without
the external real-graph files. The trace snapshots are included in this assessment archive
for exact reproduction; check their original source terms before republishing them.
