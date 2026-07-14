<!-- 中文毕业论文 附录A 复现指南（对应 ../A_reproduction.md）。代码/脚本名/路径/数字保留，表头与说明译中文。 -->

# 复现指南

本文中每个定量结果都由单个脚本从固定种子重生成。本附录将每张图与表映射到其脚本，给出命令与运行时间，
列出第3章推迟至此的完整 Phase-2 复现表，并记录数据来源。

## 环境与原则

- **技术栈：** Python 3.12；NumPy 1.26+、SciPy 1.13、NetworkX 3.3、Matplotlib（仅绘图）。
- **确定性：** 所有随机性都经 NumPy 的 `default_rng(seed).spawn(k)` 从单一主种子（默认 `0`）派生，得到
  独立、可复现的流（图、实例、算法随机性、预测扰动）。结果在 NumPy 1.25 起的小版本间按位稳定
  （基于 BitGenerator 的 spawn）。
- **配对试验：** 在一次比较中，每个算法与误差水平复用同一图、到达序列、`OPT` 与平局种子，故差异可
  归因于预测本身。
- **置信区间：** 试验上的 95% 正态近似半宽。
- 每个脚本写出 `results/<name>.json`（原始均值/置信区间）与 `results/<name>.png`（图），并打印逐步进度。

## 图/表 → 脚本映射

| 论文对象 | 脚本 | 输出 | 约运行时间 |
|---|---|---|---|
| 图 3.1（ER U 曲线） | `scripts/run_er_full.py` | `results/er_full.{json,png}` | ~20 分钟 |
| 图 3.2（左正则） | `scripts/run_left_regular.py` | `results/left_regular.{json,png}` | ~10 分钟 |
| **表 4.1**（统一基准） | `scripts/run_unified_benchmark.py`，再 `plot_unified_panels.py` | `results/unified_benchmark.{json,png}`、`unified_benchmark_panel{A,B,C}.png`、`unified_benchmark_tables.md` | ~100 秒 |
| 图 4.1（一致性–鲁棒性平面） | `scripts/run_consistency_robustness.py` | `results/consistency_robustness.{json,png}` | ~1 秒 |
| 图 5.1（顺序误差 vs ACI） | `scripts/run_order_vs_theory.py` | `results/order_vs_theory.{json,png}` | ~30 秒 |
| 图 6.1（包络）、图 6.2（前缀扫描） | `scripts/run_choo_bem.py` | `results/choo_bem_{envelope,prefix}.png` | ~20 分钟 |
| 图 6.3、重校准（6.3 节） | `scripts/run_recalibration.py` | `results/recalibration_*.png` | ~1.5 分钟 |
| 图 7.1（真实预测器） | `scripts/run_real_predictor.py` | `results/real_predictor.{json,png}` | ~15 秒 |
| 图 7.2（六个真实图） | `scripts/run_realworld_robustness.py` | `results/realworld_robustness.{json,png}` | ~65 秒 |
| 图 8.1（M0 rank vs MSE） | `scripts/run_rank_vs_mse_mve.py` | `results/rank_vs_mse_mve.{json,png}` | ~10 秒 |
| M1 扫描（8.1 节，无图） | `scripts/run_rank_when_it_matters.py` | `results/rank_when_it_matters.{json,png}` | ~20 秒 |
| 图 8.2（M3 真实 trace 学习） | `scripts/run_rank_real_trace.py` | `results/rank_real_trace.{json,png}` | ~10 秒 |
| 图 8.3（服务 SLO 探针） | `scripts/run_serving_slo_probe.py` | `results/serving_slo_probe.{json,png}` | ~1 秒 |
| 图 9.1（不可能性边界） | `scripts/run_impossibility_frontier.py` | `results/impossibility_frontier.{json,png}` | ~6 秒 |
| 图 10.1–10.3、服务（第10章） | `scripts/run_serving*.py`、`run_prefix_cache.py` | `results/serving_*.png`、`prefix_cache_*.png` 等 | 不一 |
| 真实图 Borodin 表 3/4（验证） | `scripts/run_realworld.py` | `results/realworld.json` | ~数分钟 |

## 复现命令

```bash
# 从项目根目录（matching-experiments/）
# 正确性锚点——7 个可手工验证的测试文件，全部通过：
for t in tests/test_*.py; do python3 "$t"; done

# 重生成主要结果（快脚本）：
python3 scripts/run_unified_benchmark.py        # 表 4.1（数据）
python3 scripts/plot_unified_panels.py          # 表 4.1（面板小图）
python3 scripts/run_consistency_robustness.py   # 图 4.1（重绘表 4.1）
python3 scripts/run_order_vs_theory.py          # 图 5.1
python3 scripts/run_real_predictor.py           # 图 7.1
python3 scripts/run_realworld_robustness.py     # 图 7.2
python3 scripts/run_rank_real_trace.py          # 图 8.2
python3 scripts/run_serving_slo_probe.py        # 图 8.3
python3 scripts/run_impossibility_frontier.py   # 图 9.1

# 较长（受最大流 / Hopcroft–Karp 限制）的扫描：
python3 scripts/run_er_full.py                  # 图 3.1  (~20 分钟)
python3 scripts/run_left_regular.py             # 图 3.2  (~10 分钟)
python3 scripts/run_choo_bem.py                 # 图 6.1、6.2 (~20 分钟)
```

除特别说明外所有脚本硬编码种子 `0`；重跑即复现所报告的数字。

## 完整 Phase-2 复现表（自 3.6 节推迟）

设定：$n=1000$、$m=n$、每参数值 100 次试验、种子 0。目标是与 Borodin 等人**定性**一致（Python/NetworkX
对该文 C++/Edmonds–Karp；接受绝对差 $\le 0.02$）。

**Erdős–Rényi，选定 $c$ 处的竞争比**（SG=SimpleGreedy，Rk=Ranking，F/J=Feldman/Jaillet–Lu，
-NG/-G=非贪婪/贪婪）：

| $c$ | SG | Rk | F-NG | F-G | J-NG | J-G |
|---:|---:|---:|---:|---:|---:|---:|
| 0.10 | 0.9995 | 0.9994 | 1.0000 | 1.0000 | 0.9991 | 1.0000 |
| 1.90 | 0.9362 | 0.9363 | 0.9033 | 0.9637 | 0.9202 | 0.9602 |
| **4.90** | **0.8640** | 0.8655 | 0.7648 | **0.8845** | 0.7949 | **0.8854** |
| 8.90 | 0.9094 | 0.9088 | 0.7314 | 0.9123 | 0.7662 | 0.9120 |
| 14.90 | 0.9487 | 0.9486 | 0.7290 | 0.9488 | 0.7640 | 0.9483 |

各算法最小值（ER）：SG 0.8640 @ $c$=4.9；Rk 0.8649 @ 4.7；F-NG 0.7288 @ 13.5；F-G 0.8833 @ 5.3；
J-NG 0.7616 @ 14.1；J-G 0.8839 @ 5.3。

**随机左正则，选定 $d$ 处的竞争比：**

| $d$ | SG | Rk | F-NG | F-G | J-NG | J-G |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1.0000 | 1.0000 | 0.9845 | 1.0000 | 0.9845 | 1.0000 |
| 2 | 0.9539 | 0.9537 | 0.8769 | 0.9679 | 0.8945 | 0.9659 |
| **5** | **0.8905** | 0.8900 | 0.7595 | 0.9008 | 0.7909 | 0.9022 |
| 10 | 0.9275 | 0.9278 | 0.7317 | 0.9276 | 0.7677 | 0.9290 |
| 30 | 0.9770 | 0.9767 | 0.7308 | 0.9757 | 0.7633 | 0.9754 |

**论断核对清单（全部验证 $\checkmark$）：** 贪婪最小值在 $c\approx4.9$ / $d=5$ 附近；Ranking $\approx$
SimpleGreedy（ER 最大差 0.0017、LR 0.005——该文正因此省略 Ranking 曲线）；非贪婪变体随 $c,d$ 增大
单调退化；贪婪复杂变体渐近 $\approx$ SimpleGreedy；$c$=14.9 处非贪婪的排序（J-NG 0.764 > F-NG 0.729）
与该文最坏情况界的排序一致。一个跨族观察：非贪婪算法在两族中收敛到相同的渐近常数（Feldman 0.729、
Jaillet–Lu 0.764，相差在 0.002 内），高于其最坏情况界 +0.06 / +0.03——是平均情况比最坏情况温和的
一个早期实例。

## 数据来源

真实数据本地存放于 `data/` 下（体量大；不纳入版本控制）。

- **真实图（第7章、3.6 节验证）：** 六个 Network Repository 图——`socfb-Caltech36`、`socfb-Reed98`、
  `bio-CE-GN`、`bio-CE-PG`、`econ-beause`、`econ-mbeaflw`——为 MatrixMarket `.mtx` / 空白分隔 `.edges`，
  化简为简单无向图，并经随机平衡划分（Borodin 表 3）或复制双重覆盖（表 4）转为二部图。
- **Trace（第7、8、10章）：** 四天的 Wikipedia "每日热门文章" JSON（`data/trace/wiki/`，用作直播日 vs
  1/7/30 天陈旧的预测）；Azure LLM 推理 trace（`data/trace/azure_llm/`，带时间戳的上下文/生成 token
  计数）；Mooncake 会话 trace（`data/trace/mooncake/`，每请求的前缀缓存块 `hash_ids`）。

## 理论验证片段（第9章）

构造的单 cell 常数（每 cell 的 OPT、基线，以及优势/L1 公式，见 9.3 节支柱 3）与精确的仿射转换律
$\mathbb E[\text{follow-ratio}] = \rho_{\mathrm{perfect}} - \tfrac12\ell_1(p,q)$ 由记录于项目笔记
（`docs/T1_W1_single_cell.md`、`T1_W2_W3a_closeout.md`）的简短模拟数值验证到三位小数；例如在 $\theta=0.6$、
偏置 $|s-\tfrac12|=0.3$ 时，模拟得每 cell 优势 $\pm0.119$ 与公式 $\pm\theta|s-\tfrac12|=\pm0.12$ 吻合，
聚合 follow-ratio 在每个建议水平上与仿射律吻合。这些是对构造的合理性检验，而非形式证明（附录 B）的
一部分，其剩余步骤已在 9.5 节与 B.7 节标注。
