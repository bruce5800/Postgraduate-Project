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
