<!--
Thesis Appendix A — Reproduction Guide. This is the [REPRO] reference deferred to from
Ch 3 (§3.5, §3.6) and elsewhere. Figure/table → script map, exact commands, seeds,
runtimes, full Phase-2 tables (from PHASE2_REPORT.md), data provenance, theory-verification
snippets. Figure numbers match the thesis chapters. Runtimes are approximate (machine-dependent).
-->

# Appendix A. Reproduction Guide

Every quantitative result in this thesis is regenerated from a fixed seed by a single
script. This appendix maps each figure and table to its script, gives the commands and
runtimes, lists the full Phase-2 reproduction tables deferred from Chapter 3, and records
data provenance.

## A.1 Environment and principles

- **Stack:** Python 3.12; NumPy 1.26+, SciPy 1.13, NetworkX 3.3, Matplotlib (plots only).
- **Determinism:** all randomness derives from one master seed (default `0`) via NumPy's
  `default_rng(seed).spawn(k)`, which yields independent, reproducible streams (graph,
  instance, algorithm randomness, prediction perturbation). Results are bit-stable across
  NumPy minor versions from 1.25 (BitGenerator-based spawning).
- **Paired trials:** within a comparison, every algorithm and error level reuses the same
  graph, arrival sequence, `OPT`, and tie-break seed, so differences are attributable to the
  prediction alone.
- **Confidence intervals:** 95% normal-approximation half-widths over trials.
- Each script writes `results/<name>.json` (raw means/CIs) and `results/<name>.png` (plot),
  and prints per-step progress.

## A.2 Figure / table → script map

| Thesis object | Script | Output | ≈ runtime |
|---|---|---|---|
| Fig 3.1 (ER U-curve) | `scripts/run_er_full.py` | `results/er_full.{json,png}` | ~20 min |
| Fig 3.2 (left-regular) | `scripts/run_left_regular.py` | `results/left_regular.{json,png}` | ~10 min |
| **Table 4.1**, Fig 4.1 (unified benchmark) | `scripts/run_unified_benchmark.py` | `results/unified_benchmark.{json,png}`, `unified_benchmark_tables.md` | ~100 s |
| Fig 5.1 (order-error vs ACI) | `scripts/run_order_vs_theory.py` | `results/order_vs_theory.{json,png}` | ~30 s |
| Fig 6.1 (envelope), Fig 6.2 (prefix sweep) | `scripts/run_choo_bem.py` | `results/choo_bem_{envelope,prefix}.png` | ~20 min |
| Recalibration (§6.3) | `scripts/run_recalibration.py` | `results/recalibration_*.png` | ~1.5 min |
| Fig 7.1 (real predictor) | `scripts/run_real_predictor.py` | `results/real_predictor.{json,png}` | ~15 s |
| Fig 7.2 (six real graphs) | `scripts/run_realworld_robustness.py` | `results/realworld_robustness.{json,png}` | ~65 s |
| Fig 8.1 (M0 rank vs MSE) | `scripts/run_rank_vs_mse_mve.py` | `results/rank_vs_mse_mve.{json,png}` | ~10 s |
| Fig 8.2 (M1 when it matters) | `scripts/run_rank_when_it_matters.py` | `results/rank_when_it_matters.{json,png}` | ~20 s |
| Fig 8.3 (M3 real-trace learning) | `scripts/run_rank_real_trace.py` | `results/rank_real_trace.{json,png}` | ~10 s |
| Fig 8.4 (serving SLO probe) | `scripts/run_serving_slo_probe.py` | `results/serving_slo_probe.{json,png}` | ~1 s |
| Fig 9.1 (impossibility frontier) | `scripts/run_impossibility_frontier.py` | `results/impossibility_frontier.{json,png}` | ~6 s |
| Serving (Ch 10) | `scripts/run_serving.py`, `run_serving_trace.py`, `run_serving_dynamic.py`, `run_prefix_cache.py` | `results/serving_*.png`, `prefix_cache.png` | varies |
| Real-world Borodin Tables 3/4 (validation) | `scripts/run_realworld.py` | `results/realworld.json` | ~few min |

## A.3 Reproduction commands

```bash
# from the project root (matching-experiments/)
# correctness anchors — 7 hand-verifiable test files, all pass:
for t in tests/test_*.py; do python3 "$t"; done

# regenerate the headline results (fast ones):
python3 scripts/run_unified_benchmark.py        # Table 4.1, Fig 4.1
python3 scripts/run_order_vs_theory.py          # Fig 5.1
python3 scripts/run_real_predictor.py           # Fig 7.1
python3 scripts/run_realworld_robustness.py     # Fig 7.2
python3 scripts/run_impossibility_frontier.py   # Fig 9.1
python3 scripts/run_rank_vs_mse_mve.py          # Fig 8.1
python3 scripts/run_rank_when_it_matters.py     # Fig 8.2
python3 scripts/run_serving_slo_probe.py        # Fig 8.4

# the long (max-flow / Hopcroft–Karp-bound) sweeps:
python3 scripts/run_er_full.py                  # Fig 3.1  (~20 min)
python3 scripts/run_left_regular.py             # Fig 3.2  (~10 min)
python3 scripts/run_choo_bem.py                 # Fig 6.1, 6.2 (~20 min)
```

All scripts hardcode seed `0` unless noted; re-running reproduces the reported numbers.

## A.4 Full Phase-2 reproduction tables (deferred from §3.6)

Setup: $n=1000$, $m=n$, 100 trials per parameter value, seed 0. Target is *qualitative*
agreement with Borodin et al. (Python/NetworkX vs the paper's C++/Edmonds–Karp; absolute
differences $\le 0.02$ accepted).

**Erdős–Rényi, competitive ratio at selected $c$** (SG=SimpleGreedy, Rk=Ranking,
F/J = Feldman/Jaillet–Lu, -NG/-G = non-greedy/greedy):

| $c$ | SG | Rk | F-NG | F-G | J-NG | J-G |
|---:|---:|---:|---:|---:|---:|---:|
| 0.10 | 0.9995 | 0.9994 | 1.0000 | 1.0000 | 0.9991 | 1.0000 |
| 1.90 | 0.9362 | 0.9363 | 0.9033 | 0.9637 | 0.9202 | 0.9602 |
| **4.90** | **0.8640** | 0.8655 | 0.7648 | **0.8845** | 0.7949 | **0.8854** |
| 8.90 | 0.9094 | 0.9088 | 0.7314 | 0.9123 | 0.7662 | 0.9120 |
| 14.90 | 0.9487 | 0.9486 | 0.7290 | 0.9488 | 0.7640 | 0.9483 |

Per-algorithm minima (ER): SG 0.8640 @ $c$=4.9; Rk 0.8649 @ 4.7; F-NG 0.7288 @ 13.5;
F-G 0.8833 @ 5.3; J-NG 0.7616 @ 14.1; J-G 0.8839 @ 5.3.

**Random left-regular, competitive ratio at selected $d$:**

| $d$ | SG | Rk | F-NG | F-G | J-NG | J-G |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1.0000 | 1.0000 | 0.9845 | 1.0000 | 0.9845 | 1.0000 |
| 2 | 0.9539 | 0.9537 | 0.8769 | 0.9679 | 0.8945 | 0.9659 |
| **5** | **0.8905** | 0.8900 | 0.7595 | 0.9008 | 0.7909 | 0.9022 |
| 10 | 0.9275 | 0.9278 | 0.7317 | 0.9276 | 0.7677 | 0.9290 |
| 30 | 0.9770 | 0.9767 | 0.7308 | 0.9757 | 0.7633 | 0.9754 |

**Paper-claim checklist (all verified ✓):** greedy minima near $c\approx4.9$ / $d=5$;
Ranking $\approx$ SimpleGreedy (max diff 0.0017 ER, 0.005 LR — the paper omits Ranking's
curve for this reason); non-greedy variants degrade monotonically as $c,d$ grow; greedy
complex variants $\approx$ SimpleGreedy asymptotically; the $c$=14.9 non-greedy ordering
(J-NG 0.764 > F-NG 0.729) matches the paper's worst-case-bound ordering. A cross-family
observation: the non-greedy algorithms converge to the same asymptotic constants in both
families (0.729 Feldman, 0.764 Jaillet–Lu, within 0.002), above their worst-case bounds by
+0.06 / +0.03 — an early instance of the average case being more benign than the worst case.

## A.5 Data provenance

Real data is stored locally under `data/` (large; excluded from version control).

- **Real graphs (Chapter 7, §3.6 validation):** six Network Repository graphs —
  `socfb-Caltech36`, `socfb-Reed98`, `bio-CE-GN`, `bio-CE-PG`, `econ-beause`,
  `econ-mbeaflw` — as MatrixMarket `.mtx` / whitespace `.edges`, reduced to simple
  undirected graphs and converted to bipartite by random balanced partition (Borodin
  Table 3) or duplicating double-cover (Table 4).
- **Traces (Chapters 7, 8, 10):** Wikipedia "top articles per day" JSON for four days
  (`data/trace/wiki/`, used as live day vs 1/7/30-day-stale forecasts); the Azure LLM
  inference trace (`data/trace/azure_llm/`, context/generated token counts with
  timestamps); the Mooncake conversation trace (`data/trace/mooncake/`, per-request
  `hash_ids` for prefix-cache blocks).

## A.6 Theory verification snippets (Chapter 9)

The single-cell constants of the construction (per-cell OPT, baseline, and the
advantage/L1 formulas, §9.3 Pillar-3 / Chapter 9) and the exact affine conversion law
$\mathbb E[\text{follow-ratio}] = \rho_{\mathrm{perfect}} - \tfrac12\ell_1(p,q)$ were
verified numerically to three decimals by short simulations documented in the project notes
(`docs/T1_W1_single_cell.md`, `T1_W2_W3a_closeout.md`); e.g. at $\theta=0.6$, bias
$|s-\tfrac12|=0.3$, the simulated per-cell advantage $\pm0.119$ matches the formula
$\pm\theta|s-\tfrac12|=\pm0.12$, and the aggregate follow-ratio matches the affine law at
every advice level. These are sanity checks on the construction, not part of the formal
proof, whose remaining step is noted in §9.5.
