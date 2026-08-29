#!/usr/bin/env bash
# Build the code archive submitted alongside the MSc thesis.
#
# Usage:
#   ./scripts/make_thesis_submission.sh [output.zip]
#
# The allowlist follows thesis/en/A_reproduction.md. Companion-paper sources, the Lean
# formalization, internal review material, third-party real graphs, and build caches are
# excluded by construction.
set -euo pipefail

cd "$(dirname "$0")/.."

OUT=${1:-dist/matching-experiments-thesis-code.zip}
NAME=matching-experiments-thesis-code
STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT
mkdir -p "$STAGE/$NAME"

CORE_FILES=(
  iid_sampler.py
  optimal.py
  algorithms/__init__.py
  algorithms/_common.py
  algorithms/capacity.py
  algorithms/combiner.py
  algorithms/dynamic.py
  algorithms/feldman.py
  algorithms/greedy.py
  algorithms/jaillet_lu.py
  algorithms/min_predicted_degree.py
  algorithms/prefix_cache.py
  algorithms/ranking.py
  algorithms/streaming.py
  algorithms/test_and_match.py
  graphs/__init__.py
  graphs/realworld.py
  graphs/serving.py
  graphs/synthetic.py
  graphs/trace.py
  predictions/__init__.py
  predictions/degree_truth.py
  predictions/error_models.py
  predictions/type_advice.py
)

SCRIPT_FILES=(
  scripts/plot_streaming_ladder.py
  scripts/plot_unified_panels.py
  scripts/run_arrival_order.py
  scripts/run_choo_bem.py
  scripts/run_consistency_robustness.py
  scripts/run_er_full.py
  scripts/run_impossibility_frontier.py
  scripts/run_left_regular.py
  scripts/run_metric_check.py
  scripts/run_order_vs_theory.py
  scripts/run_prefix_cache.py
  scripts/run_rank_real_trace.py
  scripts/run_rank_vs_mse_mve.py
  scripts/run_rank_when_it_matters.py
  scripts/run_real_predictor.py
  scripts/run_realworld.py
  scripts/run_realworld_robustness.py
  scripts/run_recalibration.py
  scripts/run_serving.py
  scripts/run_serving_dynamic.py
  scripts/run_serving_slo_probe.py
  scripts/run_serving_trace.py
  scripts/run_streaming_ladder.py
  scripts/run_unified_benchmark.py
  scripts/verify_witness_gap.py
)

TEST_FILES=(
  tests/test_arrival_order_small.py
  tests/test_choo_bem_small.py
  tests/test_combiner_small.py
  tests/test_feldman_small.py
  tests/test_jaillet_lu_small.py
  tests/test_mpd_small.py
  tests/test_serving_small.py
  tests/test_streaming_small.py
)

RESULT_FILES=(
  results/choo_bem.json
  results/choo_bem_envelope.png
  results/choo_bem_prefix.png
  results/consistency_robustness.json
  results/consistency_robustness.png
  results/er_full.json
  results/er_full.png
  results/impossibility_frontier.json
  results/impossibility_frontier.png
  results/left_regular.json
  results/left_regular.png
  results/metric_check.json
  results/order_vs_theory.json
  results/order_vs_theory.png
  results/prefix_cache.json
  results/prefix_cache_forecast.png
  results/prefix_cache_reversal.png
  results/rank_real_trace.json
  results/rank_real_trace.png
  results/rank_vs_mse_mve.json
  results/rank_vs_mse_mve.png
  results/rank_when_it_matters.json
  results/rank_when_it_matters.png
  results/real_predictor.json
  results/real_predictor.png
  results/realworld.json
  results/realworld_robustness.json
  results/realworld_robustness.png
  results/realworld_robustness_tables.md
  results/recalibration.json
  results/recalibration_envelope.png
  results/recalibration_prefix.png
  results/serving.json
  results/serving_cliff.png
  results/serving_dynamic.json
  results/serving_dynamic.png
  results/serving_envelope.png
  results/serving_slo_probe.json
  results/serving_slo_probe.png
  results/serving_trace.json
  results/serving_trace.png
  results/streaming_ladder.json
  results/streaming_ladder.png
  results/streaming_ladder_tables.md
  results/unified_benchmark.json
  results/unified_benchmark.png
  results/unified_benchmark_panelA.png
  results/unified_benchmark_panelB.png
  results/unified_benchmark_panelC.png
  results/unified_benchmark_tables.md
)

git archive HEAD "${CORE_FILES[@]}" "${SCRIPT_FILES[@]}" "${TEST_FILES[@]}" \
  "${RESULT_FILES[@]}" data/trace | tar -x -C "$STAGE/$NAME"

cp requirements.txt "$STAGE/$NAME/requirements.txt"
cp docs/THESIS_CODE_README.md "$STAGE/$NAME/README.md"

# Strip internal review comments. Update the data-packaging sentences because this private
# assessment archive ships the trace snapshots but not the six third-party graph datasets.
perl -0pe '
  s/<!--REV.*?-->//gs;
  s/The rest .*?scripts of the second class\./The real-graph results first need external data placed under `data\/realworld\/`; those six third-party graph datasets are not redistributed. The exact trace snapshots used in Chapters 7-9 are included under `data\/trace\/`. Section A.5 records the provenance. In the map below, a dagger (\$\\dagger\$) marks scripts that require external real-graph data./gs;
  s/Real data is stored locally under `data\/` \(large; excluded from version control\)\./The exact trace snapshots are included under `data\/trace\/`. The six third-party real graphs are not redistributed and must be placed under `data\/realworld\/`./g;
' thesis/en/A_reproduction.md \
  > "$STAGE/$NAME/REPRODUCTION.md"

mkdir -p "$(dirname "$OUT")"
rm -f "$OUT"
(
  cd "$STAGE"
  zip -qr "$NAME.zip" "$NAME"
)
mv "$STAGE/$NAME.zip" "$OUT"

echo "built $OUT ($(du -h "$OUT" | cut -f1), $(unzip -Z1 "$OUT" | wc -l | tr -d ' ') entries)"
