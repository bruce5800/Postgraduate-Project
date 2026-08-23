<!-- 中文毕业论文 附录A 复现指南（对应 ../A_reproduction.md）。代码/脚本名/路径/数字保留，表头与说明译中文。 -->

# 复现指南

本文中每个定量结果都由单个脚本从固定种子重生成。这些脚本须分为两类。多数是**自足的**：它们自行生成
合成实例，在一份干净的代码检出上开箱即跑。其余的——第7、8、9章的真实图与真实 trace 结果——需要先把外部
数据放到 `data/` 下；这些数据不随代码分发，A.5 节记录了每个数据集是什么、从哪里来。下面的映射表中以
匕首号（$\dagger$）标出第二类脚本。

本附录将每张图与表映射到其脚本，给出命令与运行时间，列出第3章推迟至此的完整 Phase-2 复现表，并记录
数据来源。

## 环境与原则

- **技术栈：** Python 3.12；NumPy 1.26+、SciPy 1.13、NetworkX 3.3、Matplotlib（仅绘图）。
- **确定性：** 所有随机性都经 NumPy 的 `default_rng(seed).spawn(k)` 从单一主种子（默认 `0`）派生，得到
  独立、可复现的流（图、实例、算法随机性、预测扰动）。结果在 NumPy 1.25 起的小版本间按位稳定
  （基于 BitGenerator 的 spawn）。
- **配对试验：** 在一次比较中，每个算法与误差水平复用同一图、到达序列、`OPT` 与平局种子，故差异可
  归因于预测本身。
- **置信区间：** 试验上的 95% 正态近似半宽。
- **流分解。** 有三处预处理——Feldman、Jaillet–Lu 与服务端的建议 $b$-匹配——取一个最大流并消费它的
  **分解**；与流的值不同，分解并不唯一。它们的网络用整数而非字符串标注节点，使 NetworkX 返回的分解在
  多次运行间稳定；用字符串标注时，它会随 Python 每进程的字符串哈希而变，由此派生的每个数字都会在同一
  个脚本的两次运行之间发生变化。
- 每个脚本写出 `results/<name>.json`（原始均值/置信区间）与 `results/<name>.png`（图），并打印逐步进度。

## 图/表 → 脚本映射

| 论文对象 | 脚本 | 输出 | 约运行时间 |
|---|---|---|---|
| 图 3.1（ER U 曲线） | `scripts/run_er_full.py` | `results/er_full.{json,png}` | ~20 分钟 |
| 图 3.2（左正则） | `scripts/run_left_regular.py` | `results/left_regular.{json,png}` | ~10 分钟 |
| 3.1 / 3.5 节方法学核对 | `scripts/run_metric_check.py` | `results/metric_check.json` | ~90 秒 |
| **表 4.1**（统一基准） | `scripts/run_unified_benchmark.py`，再 `plot_unified_panels.py` | `results/unified_benchmark.{json,png}`、`unified_benchmark_panel{A,B,C}.png`、`unified_benchmark_tables.md` | ~100 秒 |
| 图 4.1（一致性–鲁棒性平面） | `scripts/run_consistency_robustness.py` | `results/consistency_robustness.{json,png}` | ~1 秒 |
| 图 5.1（顺序误差 vs ACI） | `scripts/run_order_vs_theory.py` | `results/order_vs_theory.{json,png}` | ~30 秒 |
| 图 6.1（包络）、图 6.2（前缀扫描） | `scripts/run_choo_bem.py` | `results/choo_bem_{envelope,prefix}.png` | ~20 分钟 |
| 图 6.3、重校准（6.3 节） | `scripts/run_recalibration.py` | `results/recalibration_*.png` | ~1.5 分钟 |
| 图 6.4（检验之墙边界） | `scripts/run_impossibility_frontier.py` | `results/impossibility_frontier.{json,png}` | ~6 秒 |
| 图 7.1（真实预测器）$\dagger$ | `scripts/run_real_predictor.py` | `results/real_predictor.{json,png}` | ~15 秒 |
| 图 7.2（六个真实图）$\dagger$ | `scripts/run_realworld_robustness.py` | `results/realworld_robustness.{json,png}` | ~65 秒 |
| 图 8.1（M0 rank vs MSE） | `scripts/run_rank_vs_mse_mve.py` | `results/rank_vs_mse_mve.{json,png}` | ~10 秒 |
| M1 扫描（8.1 节，无图） | `scripts/run_rank_when_it_matters.py` | `results/rank_when_it_matters.{json,png}` | ~20 秒 |
| 图 8.2（M3 真实 trace 学习）$\dagger$ | `scripts/run_rank_real_trace.py` | `results/rank_real_trace.{json,png}` | ~10 秒 |
| 图 8.3（服务 SLO 探针） | `scripts/run_serving_slo_probe.py` | `results/serving_slo_probe.{json,png}` | ~1 秒 |
| 图 9.1–9.3、服务（第9章）$\dagger$ | `scripts/run_serving*.py`、`run_prefix_cache.py` | `results/serving_*.png`、`prefix_cache_*.png` 等 | 不一 |
| 10.2 节展望核对（A.6 节） | `scripts/verify_witness_gap.py` | 控制台输出 | 数秒 |
| 真实图 Borodin 表 3/4（验证）$\dagger$ | `scripts/run_realworld.py` | `results/realworld.json` | ~数分钟 |

运行时间为单机墙钟（Apple M4 Pro，12 核）；除 NumPy 自身的向量化外脚本为单线程，因此随单核速度伸缩。

**区间口径（自 3.5 节移来）。** `run_metric_check.py` 还把本文报告的按算法区间与同一批试验上的配对差
区间做了对比。逐实例比值正相关处，配对区间窄 $1.7$–$2.6$ 倍（相关系数 $0.67$ 与 $0.85$）；不正相关
处——垃圾建议下的盲目跟随对 Ranking，相关系数 $-0.15$——配对并不占便宜，按算法各自报告的区间才是
诚实的那个。本文余量最小的一处，Feldman(MPD) 的 $+0.0044$ 对 $\pm0.0023$，配对后收紧到 $\pm0.0009$。

## 复现命令

```bash
# 从项目根目录（matching-experiments/）
# 正确性锚点——7 个可手工验证的测试文件，全部通过：
for t in tests/test_*.py; do python3 "$t"; done

# 重生成主要结果（快脚本）：
python3 scripts/run_unified_benchmark.py        # 表 4.1（数据）
python3 scripts/plot_unified_panels.py          # 表 4.1（面板小图；需先跑上一行）
python3 scripts/run_consistency_robustness.py   # 图 4.1（需先跑 run_unified_benchmark）
python3 scripts/run_metric_check.py             # 3.1 与 3.5 节的方法学核对
python3 scripts/run_order_vs_theory.py          # 图 5.1
python3 scripts/run_real_predictor.py           # 图 7.1
python3 scripts/run_realworld_robustness.py     # 图 7.2
python3 scripts/run_rank_real_trace.py          # 图 8.2
python3 scripts/run_serving_slo_probe.py        # 图 8.3
python3 scripts/run_impossibility_frontier.py   # 图 6.4

# 较长（受最大流 / Hopcroft–Karp 限制）的扫描：
python3 scripts/run_er_full.py                  # 图 3.1  (~20 分钟)
python3 scripts/run_left_regular.py             # 图 3.2  (~10 分钟)
python3 scripts/run_choo_bem.py                 # 图 6.1、6.2 (~20 分钟)
```

除特别说明外所有脚本硬编码种子 `0`；重跑即复现所报告的数字。

## 完整 Phase-2 复现表（自 3.6 节推迟）

设定：$n=1000$、$m=n$、每参数值 100 次试验、种子 0。目标是与 Borodin 等人**定性**一致（Python/NetworkX
对该文 C++/Edmonds–Karp；接受绝对差 $\le 0.02$，故比值一律给到三位小数）。

**Erdős–Rényi，选定 $c$ 处的竞争比**（SG=SimpleGreedy，Rk=Ranking，F/J=Feldman/Jaillet–Lu，
-NG/-G=非贪婪/贪婪）：

| $c$ | SG | Rk | F-NG | F-G | J-NG | J-G |
|---:|---:|---:|---:|---:|---:|---:|
| 0.10 | 1.000 | 0.999 | 1.000 | 1.000 | 0.999 | 1.000 |
| 1.90 | 0.936 | 0.936 | 0.904 | 0.964 | 0.920 | 0.961 |
| **4.90** | **0.864** | 0.866 | 0.764 | **0.884** | 0.795 | **0.886** |
| 8.90 | 0.909 | 0.909 | 0.730 | 0.912 | 0.765 | 0.913 |
| 14.90 | 0.949 | 0.949 | 0.730 | 0.949 | 0.760 | 0.948 |

各算法最小值（ER）：SG 0.864 @ $c$=4.9；Rk 0.865 @ 4.7；F-NG 0.728 @ 14.5；F-G 0.884 @ 5.3；
J-NG 0.759 @ 13.9；J-G 0.884 @ 5.3。

**随机左正则，选定 $d$ 处的竞争比：**

| $d$ | SG | Rk | F-NG | F-G | J-NG | J-G |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1.000 | 1.000 | 0.985 | 1.000 | 0.985 | 1.000 |
| 2 | 0.954 | 0.954 | 0.877 | 0.968 | 0.895 | 0.966 |
| **5** | **0.890** | 0.890 | 0.758 | 0.900 | 0.788 | 0.901 |
| 10 | 0.928 | 0.928 | 0.733 | 0.928 | 0.766 | 0.928 |
| 30 | 0.977 | 0.977 | 0.730 | 0.976 | 0.760 | 0.976 |

**论断核对清单（全部验证 $\checkmark$）：** 贪婪最小值在 $c\approx4.9$ / $d=5$ 附近；Ranking $\approx$
SimpleGreedy（ER 最大差 0.0017、LR 0.0013——该文正因此省略 Ranking 曲线）；非贪婪变体随 $c,d$ 增大
单调退化；贪婪复杂变体渐近 $\approx$ SimpleGreedy；$c$=14.9 处非贪婪的排序（J-NG 0.760 > F-NG 0.730）
与该文最坏情况界的排序一致。跨族来看，非贪婪算法收敛到相同的渐近常数（Feldman 0.730、Jaillet–Lu
0.760，相差在 0.001 内），高于其最坏情况界 +0.06 / +0.03；3.6 节给出对这一观察的解读。

## 数据来源

真实数据本地存放于 `data/` 下（体量大；不纳入版本控制）。

- **真实图（第7章、3.6 节验证）：** 六个取自 Network Repository（`networkrepository.com`）的图——`socfb-Caltech36`、`socfb-Reed98`、
  `bio-CE-GN`、`bio-CE-PG`、`econ-beause`、`econ-mbeaflw`——为 MatrixMarket `.mtx` / 空白分隔 `.edges`，
  化简为简单无向图，并经随机平衡划分（Borodin 表 3）或复制双重覆盖（表 4）转为二部图。
- **Trace（第7、8、9章）：** 四天的 Wikipedia "每日热门文章"，取自 Wikimedia REST 页面浏览 API
  （`data/trace/wiki/`，用作直播日 vs 1/7/30 天陈旧的预测）；取自微软公开 Azure 数据集发布的 Azure LLM
  推理 trace（`data/trace/azure_llm/`，带时间戳的上下文/生成 token 计数）；以及随 [@mooncake2024] 发布
  的 Mooncake 会话 trace（`data/trace/mooncake/`，每请求的前缀缓存块 `hash_ids`）。Wikipedia trace 是
  一个活数据源的快照而非静态基准，因此精确复现需要同一份快照，而不仅仅是同一个 API。

## 展望验证片段（10.2 节）

10.2 节展望中引用的每一个量，在被使用之前都经过数值核对。共有三项核对，每项都是对稀缺资源构造的一次
简短模拟。

1. **单 cell 常数。** 每 cell 的最优、每 cell 的基线，以及优势与 $\ell_1$ 的闭式表达，与模拟吻合到三位
   小数。例如在争用率 $\theta=0.6$、建议偏置 $0.3$ 时，模拟得每 cell 优势为 $\pm0.119$，而预测值为
   $\pm\theta\cdot0.3=\pm0.12$。
2. **转换律。** 跟随建议时的期望比值与 $\rho_{\mathrm{perfect}} - \tfrac12\ell_1(p,q)$ 吻合（其中
   $\rho_{\mathrm{perfect}}$ 是完美建议下的比值）——即它随建议的 $\ell_1$ 误差线性下降——同样精确到
   三位小数。用 10.2 节的语言说，正是这一点使**赌注** $\delta$ 成为建议误差的线性函数。
3. **预算–赌注的两个成分。** 方向性统计量在固定前缀长度下的准确率不随 $n$ 增大而退化；而插入式
   $\ell_1$ 估计在 $k \ll r$ 时变得失明——即无法区分好建议与坏建议。二者都由
   `scripts/verify_witness_gap.py` 产生（A.2 节）。

这些核对使 10.2 节的**解读**成立，但它们不是对它的证明。形式化发展是本文之外的独立工作。
