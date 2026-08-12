<!--
Thesis Appendix A — Reproduction Guide. This is the [REPRO] reference deferred to from
Ch 3 (§3.5, §3.6) and elsewhere. Figure/table → script map, exact commands, seeds,
runtimes, full Phase-2 tables (from PHASE2_REPORT.md), data provenance, theory-verification
snippets. Figure numbers match the thesis chapters. Runtimes are approximate (machine-dependent).
-->

# Appendix A. Reproduction Guide

Every quantitative result in this thesis is regenerated from a fixed seed by a single
script. Two classes of script must be distinguished. Most are *self-contained*: they
generate their own synthetic instances and run as-is on a clean checkout. The rest — the
real-graph and real-trace results of Chapters 7, 8 and 9 — first need external data placed
under `data/`; that data is not redistributed with the code, and §A.5 records what each
dataset is and where it comes from. In the map below, a dagger ($\dagger$) marks the
scripts of the second class.

This appendix maps each figure and table to its script, gives the commands and
runtimes, lists the full Phase-2 reproduction tables deferred from Chapter 3, and records
data provenance.

<!--REV
id: AP-01
role: R1 二审考官
level: 必改
kind: 复现前提缺失
mark: Every quantitative result in this thesis
quote: Every quantitative result in this thesis is regenerated from a fixed seed by a single script.
note: 开场断言每个结果都能一键复现，但 A.5 说真实数据不在版本库里（体积大、已排除）。读者按 A.3 的命令跑，凡是依赖 data/ 的脚本都会直接失败，而这包括第 7、8、9 章的大部分图。
fix: 在这里就分类说清楚：哪些脚本是自足的（合成数据，开箱即跑），哪些需要先获取外部数据（附获取方式与预期目录结构）。并在 A.3 的命令块里给这两类加标记。
-->

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
- **Flow decompositions.** Three preprocessing steps — Feldman, Jaillet–Lu, and the serving
  advice $b$-matching — take a maximum flow and consume its *decomposition*, which, unlike
  the flow value, is not unique. Their networks label nodes with integers rather than
  strings, so that the decomposition NetworkX returns is stable from run to run; with
  string labels it followed Python's per-process string hashing and every number derived
  from it moved between runs of the same script.
- Each script writes `results/<name>.json` (raw means/CIs) and `results/<name>.png` (plot),
  and prints per-step progress.

<!--REV
id: AP-02
role: R2 领域审稿人
level: 建议
kind: 可证伪的断言
quote: Results are bit-stable across NumPy minor versions from 1.25
note: 逐位稳定是一个很强且可被证伪的断言。如果只在一两个版本上试过，就不该这样写；而如果真的验证过多个版本，应该说明验证到哪个版本。
fix: 改成实际验证过的范围：verified bit-stable on NumPy 1.26 and 2.x（填你真正跑过的），或降级为 deterministic under a fixed NumPy version。
-->

## A.2 Figure / table → script map

| Thesis object | Script | Output | ≈ runtime |
|---|---|---|---|
| Fig 3.1 (ER U-curve) | `scripts/run_er_full.py` | `results/er_full.{json,png}` | ~20 min |
| Fig 3.2 (left-regular) | `scripts/run_left_regular.py` | `results/left_regular.{json,png}` | ~10 min |
| §3.1 / §3.5 methodology checks | `scripts/run_metric_check.py` | `results/metric_check.json` | ~90 s |
| **Table 4.1** (unified benchmark) | `scripts/run_unified_benchmark.py`, then `plot_unified_panels.py` | `results/unified_benchmark.{json,png}`, `unified_benchmark_panel{A,B,C}.png`, `unified_benchmark_tables.md` | ~100 s |
| Fig 4.1 (consistency–robustness plane) | `scripts/run_consistency_robustness.py` | `results/consistency_robustness.{json,png}` | ~1 s |
| Fig 5.1 (order-error vs ACI) | `scripts/run_order_vs_theory.py` | `results/order_vs_theory.{json,png}` | ~30 s |
| Fig 6.1 (envelope), Fig 6.2 (prefix sweep) | `scripts/run_choo_bem.py` | `results/choo_bem_{envelope,prefix}.png` | ~20 min |
| Fig 6.3, recalibration (§6.3) | `scripts/run_recalibration.py` | `results/recalibration_*.png` | ~1.5 min |
| Fig 6.4 (testing-wall frontier) | `scripts/run_impossibility_frontier.py` | `results/impossibility_frontier.{json,png}` | ~6 s |
| Fig 7.1 (real predictor) $\dagger$ | `scripts/run_real_predictor.py` | `results/real_predictor.{json,png}` | ~15 s |
| Fig 7.2 (six real graphs) $\dagger$ | `scripts/run_realworld_robustness.py` | `results/realworld_robustness.{json,png}` | ~65 s |
| Fig 8.1 (M0 rank vs MSE) | `scripts/run_rank_vs_mse_mve.py` | `results/rank_vs_mse_mve.{json,png}` | ~10 s |
| M1 sweep (§8.1, no figure) | `scripts/run_rank_when_it_matters.py` | `results/rank_when_it_matters.{json,png}` | ~20 s |
| Fig 8.2 (M3 real-trace learning) $\dagger$ | `scripts/run_rank_real_trace.py` | `results/rank_real_trace.{json,png}` | ~10 s |
| Fig 8.3 (serving SLO probe) | `scripts/run_serving_slo_probe.py` | `results/serving_slo_probe.{json,png}` | ~1 s |
| Figs 9.1–9.3, serving (Ch 9) $\dagger$ | `scripts/run_serving.py`, `run_serving_trace.py`, `run_serving_dynamic.py`, `run_prefix_cache.py` | `results/serving_*.png`, `prefix_cache_*.png` | varies |
| Outlook checks (§A.6) | `scripts/verify_witness_gap.py` | console output | seconds |
| Real-world Borodin Tables 3/4 (validation) $\dagger$ | `scripts/run_realworld.py` | `results/realworld.json` | ~few min |

Runtimes are wall-clock on one machine (Apple M4 Pro, 12 cores); the scripts are
single-threaded apart from NumPy's own vectorization, so they scale with single-core speed.

<!--REV
id: AP-03
role: R4 体例校对
level: 必改
kind: 表格顺序错乱
mark: -
quote: Fig 6.4 (testing-wall frontier) 这一行排在 Fig 8.3 之后
note: 映射表大体按章号排列，但 Fig 6.4 被排到了 Fig 8.3 后面，Figs 9.1 到 9.3 又排在它前面。读者按图号查表时会找不到。
fix: 按图号重排整张表（3.1、3.2、4.1、5.1、6.1 到 6.4、7.1、7.2、8.1 到 8.3、9.1 到 9.3），最后再放校验类脚本。
-->

<!--REV
id: AP-04
role: R2 领域审稿人
level: 建议
kind: 运行时间缺参照
mark: -
quote: approximately runtime column: ~20 min / ~100 s / ~1 s
note: 运行时间跨了三个数量级，却没有说明测量所用的机器。读者无法判断自己那台机器上 20 分钟是不是变成 2 小时。
fix: 表下加一行脚注给出测量环境（CPU、核数、是否并行）。一行字，复现指南的可信度提升很多。
-->

## A.3 Reproduction commands

```bash
# from the project root (matching-experiments/)
# correctness anchors — 7 hand-verifiable test files, all pass:
for t in tests/test_*.py; do python3 "$t"; done

# regenerate the headline results (fast ones):
python3 scripts/run_unified_benchmark.py        # Table 4.1 (data)
python3 scripts/plot_unified_panels.py          # Table 4.1 (panel charts; needs the line above)
python3 scripts/run_order_vs_theory.py          # Fig 5.1
python3 scripts/run_real_predictor.py           # Fig 7.1
python3 scripts/run_realworld_robustness.py     # Fig 7.2
python3 scripts/run_impossibility_frontier.py   # Fig 6.4
python3 scripts/run_rank_vs_mse_mve.py          # Fig 8.1
python3 scripts/run_rank_when_it_matters.py     # M1 (§8.1)
python3 scripts/run_rank_real_trace.py          # Fig 8.2
python3 scripts/run_serving_slo_probe.py        # Fig 8.3
python3 scripts/run_consistency_robustness.py   # Fig 4.1 (needs run_unified_benchmark first)
python3 scripts/run_metric_check.py             # §3.1 and §3.5 methodology checks

# the long (max-flow / Hopcroft–Karp-bound) sweeps:
python3 scripts/run_er_full.py                  # Fig 3.1  (~20 min)
python3 scripts/run_left_regular.py             # Fig 3.2  (~10 min)
python3 scripts/run_choo_bem.py                 # Fig 6.1, 6.2 (~20 min)
```

All scripts hardcode seed `0` unless noted; re-running reproduces the reported numbers.

<!--REV
id: AP-05
role: R1 二审考官
level: 建议
kind: 复现顺序
mark: All scripts hardcode seed
quote: regenerate the headline results (fast ones) ... the long sweeps
note: 命令块按快慢分组很实用，但没有说明依赖关系：run_unified_benchmark 必须在 plot_unified_panels 之前（块里的顺序隐含了这一点），而 run_consistency_robustness 又说是 replots Table 4.1。读者若只跑其中一条会得到空图。
fix: 在需要前置步骤的命令后加行内注释标明依赖（requires run_unified_benchmark first），或者提供一个 make all 式的入口。
-->

## A.4 Full Phase-2 reproduction tables (deferred from §3.6)

Setup: $n=1000$, $m=n$, 100 trials per parameter value, seed 0. Target is *qualitative*
agreement with Borodin et al. (Python/NetworkX vs the paper's C++/Edmonds–Karp; absolute
differences $\le 0.02$ accepted).

**Erdős–Rényi, competitive ratio at selected $c$** (SG=SimpleGreedy, Rk=Ranking,
F/J = Feldman/Jaillet–Lu, -NG/-G = non-greedy/greedy):

| $c$ | SG | Rk | F-NG | F-G | J-NG | J-G |
|---:|---:|---:|---:|---:|---:|---:|
| 0.10 | 0.9995 | 0.9994 | 1.0000 | 1.0000 | 0.9991 | 1.0000 |
| 1.90 | 0.9362 | 0.9363 | 0.9039 | 0.9639 | 0.9199 | 0.9609 |
| **4.90** | **0.8640** | 0.8655 | 0.7638 | **0.8842** | 0.7955 | **0.8856** |
| 8.90 | 0.9094 | 0.9088 | 0.7304 | 0.9122 | 0.7651 | 0.9126 |
| 14.90 | 0.9487 | 0.9486 | 0.7301 | 0.9487 | 0.7601 | 0.9476 |

Per-algorithm minima (ER): SG 0.8640 @ $c$=4.9; Rk 0.8649 @ 4.7; F-NG 0.7278 @ 14.5;
F-G 0.8837 @ 5.3; J-NG 0.7586 @ 13.9; J-G 0.8836 @ 5.3.

<!--REV
id: AP-06
role: R3 英语文字编辑
level: 可选
kind: 有效数字
mark: -
quote: 0.9995 / 0.9994 / 1.0000 / 0.9991
note: 复现表给到四位小数，而正文同一批数字给三位（0.864 对 0.8640）。四位在这里没有信息量 - 与已发表结果的目标一致性容忍度是 0.02。
fix: 统一到三位小数，或在表头说明为什么这里需要四位。
-->

**Random left-regular, competitive ratio at selected $d$:**

| $d$ | SG | Rk | F-NG | F-G | J-NG | J-G |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1.0000 | 1.0000 | 0.9845 | 1.0000 | 0.9845 | 1.0000 |
| 2 | 0.9539 | 0.9537 | 0.8769 | 0.9679 | 0.8945 | 0.9659 |
| **5** | **0.8905** | 0.8900 | 0.7582 | 0.9002 | 0.7876 | 0.9008 |
| 10 | 0.9275 | 0.9278 | 0.7333 | 0.9278 | 0.7657 | 0.9284 |
| 30 | 0.9770 | 0.9767 | 0.7302 | 0.9759 | 0.7600 | 0.9755 |

**Paper-claim checklist (all verified ✓):** greedy minima near $c\approx4.9$ / $d=5$;
Ranking $\approx$ SimpleGreedy (max diff 0.0017 ER, 0.0013 LR — the paper omits Ranking's
curve for this reason); non-greedy variants degrade monotonically as $c,d$ grow; greedy
complex variants $\approx$ SimpleGreedy asymptotically; the $c$=14.9 non-greedy ordering
(J-NG 0.760 > F-NG 0.730) matches the paper's worst-case-bound ordering. Across families,
the non-greedy algorithms converge to the same asymptotic constants (0.730 Feldman, 0.760
Jaillet–Lu, within 0.001), above their worst-case bounds by +0.06 / +0.03; §3.6 reads that
observation.

<!--REV
id: AP-07
role: R4 体例校对
level: 必改
kind: 与正文重复
mark: A cross-family observation
quote: A cross-family observation: the non-greedy algorithms converge to the same asymptotic constants in both families
note: 这段与 3.6 末尾的 A cross-family observation 段落几乎逐字相同，包括同样的解读句。正文和附录各一份，读者核对时会白花时间。
fix: 附录只留数字，解读交给 3.6，并写 see 3.6。或者反过来。
-->

## A.5 Data provenance

Real data is stored locally under `data/` (large; excluded from version control).

- **Real graphs (Chapter 7, §3.6 validation):** six graphs from the Network Repository
  (`networkrepository.com`) — `socfb-Caltech36`, `socfb-Reed98`, `bio-CE-GN`, `bio-CE-PG`,
  `econ-beause`, `econ-mbeaflw` — downloaded as MatrixMarket `.mtx` / whitespace `.edges`,
  reduced to simple undirected graphs and converted to bipartite by random balanced
  partition (Borodin Table 3) or duplicating double-cover (Table 4).
- **Traces (Chapters 7, 8, 9):** Wikipedia "top articles per day" for four days, retrieved
  from the Wikimedia REST pageviews API (`data/trace/wiki/`, used as live day vs
  1/7/30-day-stale forecasts); the Azure LLM inference trace from Microsoft's public Azure
  dataset release (`data/trace/azure_llm/`, context/generated token counts with
  timestamps); and the Mooncake conversation trace released with [@mooncake2024]
  (`data/trace/mooncake/`, per-request `hash_ids` for prefix-cache blocks). The Wikipedia
  trace is a snapshot of a live source rather than a static benchmark, so exact reproduction
  needs the same snapshot, not merely the same API.

<!--REV
id: AP-08
role: R1 二审考官
level: 必改
kind: 数据不可获取
mark: Real data is stored locally under
quote: Real data is stored locally under data/ (large; excluded from version control).
note: 六个真实图和三条 trace 只给了名字，没有给来源链接、版本或下载方式。这直接影响第 7、8、9 章的可复现性，也是外审最常提的一条意见。
fix: 每个数据集补一行来源：Network Repository 的具体 URL 或引用、Wikipedia API 的取数日期、Azure 与 Mooncake trace 的发布仓库与提交号。这一条是本附录存在的意义所在。
-->

## A.6 Outlook verification snippets (§10.2)

Every quantity quoted in the outlook of §10.2 was checked numerically before being used.
There are three checks, each a short simulation of the rare-resource construction.

1. **Per-cell constants.** The per-cell optimum, the per-cell baseline, and the closed forms
   for the advantage and for $\ell_1$ agree with simulation to three decimals. For example,
   at contention $\theta=0.6$ and advice bias $0.3$ the simulated per-cell advantage is
   $\pm0.119$, against a predicted $\pm\theta\cdot0.3 = \pm0.12$.
2. **The conversion law.** The expected ratio when the advice is followed matches
   $\rho_{\mathrm{perfect}} - \tfrac12\ell_1(p,q)$, where $\rho_{\mathrm{perfect}}$ is the
   ratio under perfect advice — it falls off linearly in the advice's $\ell_1$ error — again
   to three decimals. In the language of §10.2 this is what makes the *stakes* $\delta$ a
   linear function of the advice error.
3. **The two budget–stakes ingredients.** The directional statistic's accuracy at a fixed
   prefix length does not degrade as $n$ grows, and the plug-in $\ell_1$ estimate becomes
   blind — indistinguishable between good and bad advice — once $k \ll r$. Both are produced
   by `scripts/verify_witness_gap.py` (§A.2).

These checks are what license the *reading* of §10.2; they are not a proof of it. The formal
development is separate work outside this thesis.

<!--REV
id: AP-09
role: R5 答辩提问者
level: 必改
kind: 支撑材料不可见
mark: The quantities behind the outlook
quote: checked to three decimals by short simulations documented in the project notes (docs/T1_W1_single_cell.md, T1_W2_W3a_closeout.md) ... verified by scripts/verify_witness_gap.py
note: 10.2 的展望是全文答辩风险最高的一节，而支撑它的数值验证全部指向读者拿不到的仓库文件。等于说这一节的证据不在论文里。
fix: 把这些验证摘成附录里的半页：验证了哪两个量、用什么参数、结果与公式差多少（例如已经写出的 0.119 对 0.12）。正文数字加附录证据，10.2 才站得住。
-->

<!--REV
id: AP-10
role: R3 英语文字编辑
level: 建议
kind: 术语与正文不一致
quote: the exact affine conversion law ... rho_perfect - L1/2
note: 附录这里出现了 rho_perfect、affine conversion law 等 10.2 正文没有用过的名字，读者无法把两处对上。
fix: 统一到 10.2 的措辞，或在此处加一句对照说明哪个量对应正文的哪个符号。
-->
