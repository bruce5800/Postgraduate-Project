# Lean 4 / Mathlib 侦察报告 — 预算–赌注定律形式化 (2026-08-14)

目的：在承诺形式化之前探明库存。结论先行：**可做，且推荐走"有限/PMF 自包含"路线**，
分六个阶段、每阶段有退出点；第 1 阶段（payoff 恒等式）是 go/no-go 探针。

## 库存清单

| 需求 | 状态 | 位置 / 备注 |
|---|---|---|
| 有限概率 / PMF / Finset 期望 | ✅ 成熟 | `Mathlib.Probability.ProbabilityMassFunction.*`，Finset 代数 |
| Hoeffding 不等式 | ✅ 在 Mathlib | `Mathlib.Probability.Moments.SubGaussian`：Hoeffding 引理 `hasSubgaussianMGF_of_mem_Icc_of_integral_eq_zero`；独立和 `measure_sum_ge_le_of_iIndepFun`；另有 Azuma |
| Bernstein 不等式（σ² 感知） | ❌ 未找到 | 需自证（经 sub-exponential MGF，约 2–3 周）或先用 Hoeffding 出弱版 (ii)（丢 σ² 精细化，即丢 θ 缩放）。自证版本身是有价值的 Mathlib PR |
| Hellinger / 张量化 / TV 比较 | ⚠️ 在外部项目 | Degenne–Luccioli **TestingLowerBounds**（Lean4/Mathlib 基座，1252 commits，活跃）：顶层 `SqHellinger.lean`、`Divergences/`、`FDiv/`、乘积机制 `CompProd.lean`/`MeasureCompProd.lean`、`Testing/`（假设检验风险下界——与我们 Lemma 1 的统计内核同源，值得深挖）。**未并入 Mathlib**（Mathlib 仅有 `InformationTheory.KullbackLeibler.Basic`）。注意仓库有 `Sorry/` 目录——依赖前必须确认所需引理 sorry-free |
| TV 距离 + 耦合刻画 | ⚠️ 部分 | Mathlib 有符号测度 totalVariation；我们需要的是**有限**情形（TV = ½Σ|p−q|；\|E_Pf−E_Qf\|≤TV, f∈[0,1]）——Finset 上手工证明约半天，比接通用测度机制便宜 |
| 本地工具链 | ❌ 未安装 | elan + lake + Mathlib 缓存，约 30–60 分钟 + 数 GB |

## 关键策略判断：走有限世界，不碰通用测度

我们的定理**本来就是有限离散的**（有限类型集、有限前缀、乘积多项分布）。两条路线：

- **A（推荐）自包含 PMF/Finset 路线**：Hellinger 张量化在有限情形 =
  Bhattacharyya 系数 Σ√(pq) 的乘积可乘性 = Finset 上的 Cauchy 乘积，约一周手工可证，
  **零外部依赖**、artifact 轻、审稿人可读。TV 耦合同理。唯一接 Mathlib 重机械的点是
  Hoeffding（Stage 4）。
- **B 依赖 TestingLowerBounds**：机制现成但要背研究仓库依赖（Mathlib 版本钉死、
  sorry 风险、artifact 变重）。仅当 Stage 5 手工张量化意外卡住时作为备选。

## 分阶段计划（每段可退出；与"试做、卡住往后排"匹配）

| 阶段 | 内容 | 预估 | 退出点价值 |
|---|---|---|---|
| 0 | elan/lake 安装 + `lake new` + Mathlib 缓存 + PMF hello-world | ½ 天 | — |
| 1 | **payoff 恒等式**（纯 Finset 代数，显式样本空间） | 1–3 天 | **go/no-go 探针**；单独即可写入 artifact |
| 2 | σ² = 2(1−ρ_base) + 仿射律 | 2–4 天 | "core identities machine-checked" |
| 3 | Lemma 1 非渐近版（有限空间；TV 耦合手工引理） | 1–2 周 | 主权衡不等式获证书 |
| 4 | Thm 1(ii) Hoeffding 版（接 Mathlib SubGaussian；弱常数） | 1–2 周 | 上半定律获证书（θ=Θ(1) 档） |
| 5 | Thm 1(i)：有限 Hellinger + 手工张量化 + [2t,4t] 不等式 + 接 Lemma 1 | 1–2 周 | **双侧定律完整证书** |
| 6 | （可选）Bernstein 自证 → σ²-锐利 (ii)；候选 Mathlib PR | 2–3 周 | 完整版 + 社区贡献 |

信任叙事在 Stage 2 即可启用（"核心恒等式经 Lean 4 内核检验"），Stage 5 后升级为
"定律双侧机器验证"。全程与投稿解耦：arXiv/投稿不等它，修稿回应用它。

## 已知风险

1. Stage 4 的 PMF↔测度框架桥接是最可能的"卡点"（Mathlib 的 SubGaussian 生活在
   一般测度世界）；备选：对有限 iid 直接手推 Chernoff（多项式 MGF，Finset 可证）。
2. `Real.sqrt` 不等式操作（Stage 5 的 [2t,4t]）繁琐但无深度。
3. 渐近语句一律重写为显式常数的非渐近版——论文 §7.5 的表述届时应同步收紧（好事）。

---

## 状态更新（2026-08-21）：Stage 0–5 + 7 完成，66 条定理、零 sorry

| 阶段 | 文件 | 定理数 | 结果 |
|---|---|---|---|
| 1 | `PayoffIdentity.lean` | 4 | payoff 恒等式、σ² 恒等式 |
| 2 | `AffineLaw.lean` | 7 | 仿射律 + 推论 |
| 3 | `MasterTradeoff.lean` | 8 | TV 耦合界；主权衡不等式（**精确、非渐近**） |
| 4 | `Chernoff.lean` | 9 | 有限 Chernoff `exp(−kμ²/4)`（Thm 1(ii) 弱常数版） |
| 5 | `Hellinger.lean` | 11 | BC 张量化、`TV ≤ √(2k(1−bc))`、`master_tradeoff_iid`（Thm 1(i) 抽象核心） |
| 7 | `RandomOrder.lean` | 27 | 方差 + Chebyshev；iid 前缀和方差精确值 `k·Var(c)` ⇒ **σ²-锐利标度（Chebyshev 级）**；iid 前缀的置换不变性（下界向 random-order 的 Yao 式转移）；**random-order 模型**：均匀置换、可交换性（仅用传递性、零计数）、有限总体方差 `≤ k·E_pop[c²]`、`Pr(∑≤0) ≤ E_pop[c²]/(kμ²)` |

实际用时远低于侦察估计：全部 6 个阶段约 1.5 个工作日；"有限世界路线"（自定义 `FinDist`，
`sum_prod_eq_pow` 一条恒等式承载全部独立性）是决定性选择。Stage 4 预想的"PMF↔测度桥接
卡点"根本没出现——因为根本没接 Mathlib 的 SubGaussian。

### T3 / T4 / T5 能否"用 Lean 试证"——诚实评估

前提要说清：**Lean 只能验证已有的证明，不能发现定理**；它对付的是"信任缺口"，不是"工具
初等"。"工具初等"是审稿人对*概念深度*的质疑，能正面回应它的只有（a）定理类的一般性、
（b）双侧紧性、（c）诚实的定位；形式化的作用是让 (a)(b) 的**每一条声明都不可辩驳**。

| 项 | 数学是否已有 | Lean 可行性 | 结论 |
|---|---|---|---|
| **T5 random-order** | 下界：Yao 式归约（iid 总体的随机次序前缀仍是 iid）——**已有**；上界：无放回前缀和的浓度 | 下界转移引理 + Chebyshev 级上界 **已形式化（Stage 7）**；指数尾需 Hoeffding 凸序定理/Serfling（Maclaurin 端点不等式 `e_k/C(n,k) ≤ (e_1/n)^k`），约 1–2 周、有风险 | ✅ 骨架已机器验证；指数尾列为可选 |
| **T3 gadget 类推广** | **没有**：常数大小 gadget 的期望 payoff 是到达分布的非线性泛函（含 Binomial 到达计数），方向统计量要从逐样本线性量换成 plug-in/U-统计量，方差分析待做 | 抽象框架（`Scenario`/`master_tradeoff`/`iid`/Chebyshev）已是 gadget-无关的，随时可接；但 **Lean 不能替代纸面上 2–4 周的数学** | ⏸ 先做数学，再形式化（1–2 周） |
| **T4 一般图** | 开放问题（研究级，2–6 个月、无保证） | 不是 Lean 的用武之地；至多在找到分离构造后形式化 | ✖ 不纳入 |

### 对投稿的直接含义
- 论文 Limitations (i)（"我们在 known-i.i.d. 模型"）可以升级为一个有形式化背书的 remark：
  定律的**标度**在 random-order 下成立（下界 Yao 归约，上界 Chebyshev 级）。
- 信任叙事最终形态："the budget–stakes law is machine-checked in Lean 4 on both sides at the
  abstract level, and its scaling is machine-checked under random order; 66 theorems, 0 sorries."
