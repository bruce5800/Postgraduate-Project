# Pass 0：投稿前批注裁决表（2026-08-24）

对象：`paper/*.md` 里的 37 个 REV 批注块（20 必改）+ 机械审计。
结论先行：**必改 20 条中 19 条已被后续修稿解决**（唯一残留是 5-01 的附录承诺问题）；
开放项 8 条全部是"建议"级；机械审计另发现 3 处小问题。Pass 1 通读时对照本表即可。

## 一、已解决（Pass 2 时可删块）——24 条

| id | 级别 | 判定依据（现文位置） |
|---|---|---|
| 0-01 | 必改 | 摘要与引言均已加"meet up to logarithms whenever…"条件从句并指向 §7.8 开放情形 |
| 0-02 | 必改 | 摘要只用 g；引言 cap 句已写成 $g \le 2\varepsilon_{\max}(1-\rho_{\mathrm{base}})$；§7.5 有 Symbols 段 |
| 0-04 | 建议 | 已改 "the square of the stakes" |
| 0-05 | 建议 | §9 已有 "Scope of our novelty claims" 段（库、关键词、2026-04 截止、未做 citation trace 均声明） |
| 1-01 | 必改 | 占位符已换成 Appendix A，且复现附录已存在 |
| 1-02 | 建议 | §2.5 已区分自足脚本与需外部数据的脚本，指向 A.4 |
| 2-01 | 必改 | Panel A 已写作 "heavy-tailed degrees (Zipf)" |
| 2-02 | 必改 | Table 1 题注已声明三个 floor 面板间不可比、两族质量列不可比 |
| 2-03 | 必改 | F1 已限定 "Under adversarial or garbage advice"，并补对照句 |
| 3-01 | 必改 | 已换成 $n-\mathrm{LIS}(w[\mu])$ 并注明与类型分布 p 无关 |
| 3-03 | 必改 | 已给 44 点合并 ρ_S=0.979、r=0.992、模型内 ≥0.973 |
| 4-01 | 必改 | "never" 已删，限定到本 sweep，全称交给 Theorem 1 |
| 4-02 | 必改 | 0.696 已补出处（随机到达序 Ranking 最坏比值 [MY11]、Choo 所用值、并辨析 1−1/e） |
| 4-04 | 必改 | 该段整体重写：实测方差 0.026→0.012、SNR 1.1、并诚实注明 k·Var 非常数 → 引用测量而非公式 |
| 4-05 | 必改 | 已标注 "single-instance mechanism check (n=600, r=6, one seed, no averaging)"，tests/ 路径移出正文 |
| 5-02 | 必改 | 已改 "by 0.06 (Reed98) to 0.10 (CE-PG)"，算术验算通过 |
| 5-03 | 必改 | 已改 "F3 holds on all six" |
| 6-01 | 必改 | §7 开头已带条件与 §7.8 指向 |
| 6-04 | 必改 | Theorem 1 前已有 Symbols 段统一 g 与 δ/Δ |
| 6-05 | 必改 | 附录 B 完整证明已写；正文注明 "in full in Appendix B" |
| 6-06 | 必改 | 推论已写条件继承与"(ii) 无条件"括注 |
| 6-07 | 建议 | "project archive" 已换成指向 §9 范围声明 |
| 7-02 | 建议 | 已限定 "among the works covered by the search above" |
| 7-03 | 建议 | Known-IID ≤ Random-Order 已展开成完整句（2026-08-21 随 random-order remark 改写） |
| 7-04 | 必改 | §10 已改口径 "that search is complete, but bounded by …, scoped rather than exhaustive" |

（表中 25 行含 7-03；即"已解决"共 25 条，其中必改 19。）

## 二、开放 / 部分解决——12 条（全部非阻塞，按性价比排序）

| id | 级别 | 现状 | 建议改法 | 工作量 |
|---|---|---|---|---|
| 2-04 | 建议 | "visible only under a unified table" 仍在 | 改 "a pairing that a unified table makes immediate" | 1 短语 |
| 5-04 | 建议 | "instructive rather than a failure" 仍在 | 删自评句，直接给稠密图解释 | 1 句 |
| 3-02 | 建议 | 16×–75× 无口径 | 补 "ratio of the bound to the realized loss at each model's strongest corruption level" | 1 从句 |
| 3-04 | 建议 | τ∈[0,1] 已在 §2.3，端点含义未说 | §2.3 加 "0 = 预测序完全正确，1 = 完全反序" | 1 从句 |
| 4-03 | 建议 | 噪声底 0.05–0.13 未定义 | 补 "完美建议下长度 k 前缀经验分布与真直方图的 ℓ₁ 距离（纯采样噪声，随 k 下降）" | 1 句 |
| 6-02 | 建议 | "写成平方"的理由已给（方差界）；σ 本身与 §7.6 未指 | 定义处补 "its square root σ is the resolution unit of §7.6" | 1 从句 |
| 5-01 | **必改残留** | 正文三处改指 Appendix A，但附录 A 只有脚本映射，**没有**承诺的 per-staleness 数字、per-graph 表、训练配置清单 | 二选一：(a) 弱化正文措辞为 "scripts mapped in Appendix A; full tables ship with the artifact (`realworld_robustness_tables.md` 等)"；(b) 附录 A 增设 A.5 三张小表。推荐 (b)，Empirical Track 审稿人会核对 | (a) 3 处措辞 / (b) 半页 |
| 5-05 | 建议 | 配置清单既不在正文也不在附录 | 按原 fix 把一句配置写进 §6.3（150 类型 / 500 个度 8 副本 / 40 窗口 / 3 滞后特征 / 60-40 划分），与 5-01(b) 合并处理 | 1 句 |
| 0-03 | 建议 | 摘要实测 **439 词**（改后不降反升） | 压到 ~250 词：问题+发现两句、定律+代价两句、金句一句；公式只留 σ²/g²。TALG 是期刊、无硬限，但首因效应真实 | 半小时+你定稿 |
| 0-06 | 建议 | C1–C5 仍近一页（C5 因 Lean 从句更长） | 每条压 2–3 行，C4/C5 细节下沉到 §5.4/§7 | 半小时+你定稿 |
| 6-03 | 建议 | cell 常数推导仍缺（Lean 把它当模型定义，帮不上） | 附录 B 前加半页 "B.0 The cell constants"：OPT=1+θ、baseline=1+θ/2、follow=±θ|s−½| 的两行推导。**我可以起草** | 半页 |
| 7-01 | 建议 | §8 两次"case study"声明；第二次现已承接 SLO 探针结论，可辩护 | 可保留；若改：首段合并为一句并写明本节正面价值（验证抽象落地 + §6.3 负结果的实验场） | 可选 |

## 三、机械审计新发现——3 处小问题 + 4 项通过

**要修：**
- **N-1** `06_theory.md:284`："Numerically (§`verify_witness_gap.py`, …)" 的 **§ 是笔误**，PDF 里渲染成 "§verify_witness_gap.py"。删 §。
- **N-2** `05_external_validity.md:100`："(beause: 0.939 vs …)" —— beause 是 econ 图名，但**读者必然当成 because 的拼写错误**。改 "(on econ-beause: …)"。
- **N-3** `07:74`：Diakonikolas et al. 点名无引用。建议补 bib：Diakonikolas–Kontonis–Tzamos–Vakilian–Zarifis, *Learning Online Algorithms with Distributional Advice*, ICML 2021（**作者名单待核**，Pass 2 时联网确认）；或删人名改说法。

**通过：**
- 论文引用的全部 12 个 Lean 定理名与 `budgetstakes/` 代码逐一核对，**拼写全部一致**。
- 图号 1–9 与出现顺序一致，无遗留 "Figure 10"；12 个图片文件 = 9 个编号图 + Table 1 的 3 个 panel；arXiv Comments "31 pages, 9 figures" 正确。
- 正文可见文本已无 docs/*.md 指向（仅存于会被剥除的注释头）。
- 根 README 的 "20 pp" 已改 "31 pp"（本次顺手修）。

## Pass 1 → Pass 2 交接
你通读时：开放项 12 条对照现文核实取舍即可（尤其 0-03/0-06 要你定稿口味）；
Pass 2 我按你的标注一次性改稿 + 删除第一节 25 个已解决块 + N-1/N-2/N-3 + 重建 + arXiv 包。
