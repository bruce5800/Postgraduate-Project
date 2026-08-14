#!/usr/bin/env bash
# Build the reviewer-facing artifact archive for the TALG submission.
#
#   ./scripts/make_artifact.sh [git-ref] [output.zip]
#
# The archive is an ALLOWLIST of the paths a reviewer needs to re-run the empirical
# claims of the paper.  It is built with `git archive`, so only committed content can
# get in, and anything not named below is excluded by construction — in particular:
#
#   thesis/       the MSc thesis this work grew out of
#   paper/        the manuscript sources, which carry the inline <!--REV --> review
#                 annotations (all 37 of them live in paper/*.md, not just in
#                 paper/review/) — reviewers get the PDF, not these
#   docs/         internal working notes and the self-verification checklist
#                 (docs/references.bib is the one exception, it is the bibliography)
#
# Attach the resulting zip to the GitHub Release for the submission tag; the paper's
# Appendix A cites that Release.  Nothing here needs maintaining between releases:
# re-run it when you cut a new tag.
set -euo pipefail
cd "$(dirname "$0")/.."

REF=${1:-HEAD}
OUT=${2:-dist/talg-artifact.zip}
NAME=talg-artifact

PATHS=(
  algorithms graphs predictions scripts tests
  iid_sampler.py optimal.py
  data/trace
  results
  docs/references.bib
)

STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT
mkdir -p "$STAGE/$NAME"

git archive "$REF" "${PATHS[@]}" | tar -x -C "$STAGE/$NAME"

cat > "$STAGE/$NAME/README.md" <<'EOF'
# Artifact — "The Limits of Predictions for Online Bipartite Matching"

This archive reproduces the empirical claims of the paper. **Appendix A of the paper is
the authoritative guide**: it maps every figure, table and quoted number to the script
that produces it, gives the runtimes, and records the data provenance. This file only
says how to get started.

## Requirements

Python 3.12 with NumPy 1.26, SciPy 1.13, NetworkX 3.3 and Matplotlib. No other
dependencies. Run everything from the root of this archive.

## What runs out of the box

Everything except the six-real-graph results of Section 6.2. The synthetic experiments
generate their own instances, and the request traces of Sections 6.1, 6.3 and 8 ship
here under `data/trace/`.

    python3 scripts/run_unified_benchmark.py       # Table 1
    python3 scripts/plot_unified_panels.py         # Table 1 panel charts
    python3 scripts/run_order_vs_theory.py         # Figure 1
    python3 scripts/run_directional_test.py        # Figures 4, 5, 9
    python3 scripts/run_impossibility_frontier.py  # Figure 8
    python3 scripts/run_real_predictor.py          # Figure 6  (shipped Wikipedia trace)

Correctness anchors, each hand-checkable and a few seconds each:

    for t in tests/test_*.py; do python3 "$t"; done

The two theory checks referenced in Section 7 are console scripts:

    python3 scripts/verify_witness_gap.py
    python3 scripts/verify_budget_stakes_hetero.py

## What needs a download first

`scripts/run_realworld_robustness.py` (Figure 7) and the Phase-2 `run_realworld.py` read
six third-party graphs that we are not able to redistribute. Place them under
`data/realworld/` as described in Appendix A.4; they come from the Network Repository
(networkrepository.com): socfb-Caltech36, socfb-Reed98, bio-CE-GN, bio-CE-PG,
econ-beause, econ-mbeaflw.

## Comparing against our numbers

`results/` contains the outputs behind the paper, so a fresh run can be diffed against
them directly. Results are deterministic given the seed: all randomness derives from one
master seed spawned into independent sub-streams, and the max-flow networks label nodes
with integers so that NetworkX's flow *decomposition* is stable across runs.
EOF

mkdir -p "$(dirname "$OUT")"
rm -f "$OUT"
( cd "$STAGE" && zip -qr "$NAME.zip" "$NAME" )
mv "$STAGE/$NAME.zip" "$OUT"

echo "built $OUT  ($(du -h "$OUT" | cut -f1), $(unzip -Z1 "$OUT" | wc -l | tr -d ' ') entries) from ref $REF"
echo "excluded by construction: $(git ls-tree -d --name-only "$REF" | tr '\n' ' ')-> only the allowlist above is present"
