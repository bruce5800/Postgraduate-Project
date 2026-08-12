# §5 Test-and-fallback — 审读批注

共 5 条：🔴 必改 4 · 🟡 建议 1 · ⚪ 可选 0。

批注原件在 `04_test_and_fallback.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

---
### 4-01 · 🔴 必改 · P2 领域审稿人 · 全称断言

`04_test_and_fallback.md:37`

> its prefix test rejects it and it falls back to Ranking, never crashing

**问题** never 是全称量词，证据是一条误差 sweep、一个图族、40 次重复。

**建议** 限定到证据范围：it does not fall below the advice-free floor at any point of this sweep。真正的全称结论交给 §7 的定理承担。


### 4-02 · 🔴 必改 · P1 领域外审稿人 · 常数无出处

`04_test_and_fallback.md:73`

> calibrated to the worst-case baseline $\beta\approx0.696$

**问题** 0.696 凭空出现。领域外审稿人会问它是哪来的、为什么不是 1-1/e。它是本节机制解释的支点。

**建议** 补半句出处：随机到达序下 Ranking 的最坏情况比值，也是 Choo 等人给阈值取的值，并引 [Choo24]。


### 4-03 · 🟡 建议 · P2 领域审稿人 · 估计量缺说明

`04_test_and_fallback.md:101`

> smaller than the empirical-l1 estimator's own noise floor (approximately 0.05-0.13 at this prefix and support)

**问题** 噪声底给了区间但没说怎么估的、随什么变化。它是 §5.3 到 §7 的桥。

**建议** 补一句定义：完美建议下长度 k 前缀的类型频率与真实直方图的 l1 距离，即纯采样噪声，随 k 增大而下降。


### 4-04 · 🔴 必改 · P2 领域审稿人 · 把 sigma^2 悄悄设成 1

`04_test_and_fallback.md:163`

> with this family's payoff estimator carrying per-sample variance of order one, resolving stakes of 0.02 takes k approx 1/0.02^2 = 2500

**问题** §7 的预算是 sigma^2/g^2，这里直接写成 1/g^2，等于把 sigma^2 取成 1 而只用一个从句带过。审稿人会问：benchmark 家族的 sigma^2 到底是多少？这是把定理用到自己算法上的唯一一处，不能含糊。

**建议** 把 sigma^2 的取值（或它在该家族上的量级估计）写出来，公式写成 k approx sigma^2/g^2 并代入具体数字。


### 4-05 · 🔴 必改 · P7 复现审稿人 · 用单元测试当证据

`04_test_and_fallback.md:205`

> eager switching scores 0.927 - below both the pure follower (1.000) and the pure baseline (0.958; verified in tests/test_combiner_small.py)

**问题** 论文正文的数字引用了一个单元测试文件。实际规模是 n=600、r=6、单个种子、不做平均——全节其他数字都有实验设置，只有这一处没有，且它支撑的是」为何必须 test-then-commit」这一结论。

**建议** 写明它的地位与规模：a single-instance mechanism check (n=600, r=6, one seed, no averaging)，或升级为一次带置信区间的正式实验。脚本路径移到复现附录。

