# 附录 A Reproduction Guide — 审读批注

共 10 条：🔴 必改 5 · 🟡 建议 4 · ⚪ 可选 1。

批注原件在 `en/A_reproduction.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

---
### AP-01 · 🔴 必改 · R1 二审考官 · 复现前提缺失

`en/A_reproduction.md:15`

> Every quantitative result in this thesis is regenerated from a fixed seed by a single script.

**问题** 开场断言每个结果都能一键复现，但 A.5 说真实数据不在版本库里（体积大、已排除）。读者按 A.3 的命令跑，凡是依赖 data/ 的脚本都会直接失败，而这包括第 7、8、9 章的大部分图。

**建议** 在这里就分类说清楚：哪些脚本是自足的（合成数据，开箱即跑），哪些需要先获取外部数据（附获取方式与预期目录结构）。并在 A.3 的命令块里给这两类加标记。


### AP-02 · 🟡 建议 · R2 领域审稿人 · 可证伪的断言

`en/A_reproduction.md:40`

> Results are bit-stable across NumPy minor versions from 1.25

**问题** 逐位稳定是一个很强且可被证伪的断言。如果只在一两个版本上试过，就不该这样写；而如果真的验证过多个版本，应该说明验证到哪个版本。

**建议** 改成实际验证过的范围：verified bit-stable on NumPy 1.26 and 2.x（填你真正跑过的），或降级为 deterministic under a fixed NumPy version。


### AP-03 · 🔴 必改 · R4 体例校对 · 表格顺序错乱

`en/A_reproduction.md:71`

> Fig 6.4 (testing-wall frontier) 这一行排在 Fig 8.3 之后

**问题** 映射表大体按章号排列，但 Fig 6.4 被排到了 Fig 8.3 后面，Figs 9.1 到 9.3 又排在它前面。读者按图号查表时会找不到。

**建议** 按图号重排整张表（3.1、3.2、4.1、5.1、6.1 到 6.4、7.1、7.2、8.1 到 8.3、9.1 到 9.3），最后再放校验类脚本。


### AP-04 · 🟡 建议 · R2 领域审稿人 · 运行时间缺参照

`en/A_reproduction.md:82`

> approximately runtime column: ~20 min / ~100 s / ~1 s

**问题** 运行时间跨了三个数量级，却没有说明测量所用的机器。读者无法判断自己那台机器上 20 分钟是不是变成 2 小时。

**建议** 表下加一行脚注给出测量环境（CPU、核数、是否并行）。一行字，复现指南的可信度提升很多。


### AP-05 · 🟡 建议 · R1 二审考官 · 复现顺序

`en/A_reproduction.md:121`

> regenerate the headline results (fast ones) ... the long sweeps

**问题** 命令块按快慢分组很实用，但没有说明依赖关系：run_unified_benchmark 必须在 plot_unified_panels 之前（块里的顺序隐含了这一点），而 run_consistency_robustness 又说是 replots Table 4.1。读者若只跑其中一条会得到空图。

**建议** 在需要前置步骤的命令后加行内注释标明依赖（requires run_unified_benchmark first），或者提供一个 make all 式的入口。


### AP-06 · ⚪ 可选 · R3 英语文字编辑 · 有效数字

`en/A_reproduction.md:152`

> 0.9995 / 0.9994 / 1.0000 / 0.9991

**问题** 复现表给到四位小数，而正文同一批数字给三位（0.864 对 0.8640）。四位在这里没有信息量 - 与已发表结果的目标一致性容忍度是 0.02。

**建议** 统一到三位小数，或在表头说明为什么这里需要四位。


### AP-07 · 🔴 必改 · R4 体例校对 · 与正文重复

`en/A_reproduction.md:182`

> A cross-family observation: the non-greedy algorithms converge to the same asymptotic constants in both families

**问题** 这段与 3.6 末尾的 A cross-family observation 段落几乎逐字相同，包括同样的解读句。正文和附录各一份，读者核对时会白花时间。

**建议** 附录只留数字，解读交给 3.6，并写 see 3.6。或者反过来。


### AP-08 · 🔴 必改 · R1 二审考官 · 数据不可获取

`en/A_reproduction.md:208`

> Real data is stored locally under data/ (large; excluded from version control).

**问题** 六个真实图和三条 trace 只给了名字，没有给来源链接、版本或下载方式。这直接影响第 7、8、9 章的可复现性，也是外审最常提的一条意见。

**建议** 每个数据集补一行来源：Network Repository 的具体 URL 或引用、Wikipedia API 的取数日期、Azure 与 Mooncake trace 的发布仓库与提交号。这一条是本附录存在的意义所在。


### AP-09 · 🔴 必改 · R5 答辩提问者 · 支撑材料不可见

`en/A_reproduction.md:234`

> checked to three decimals by short simulations documented in the project notes (docs/T1_W1_single_cell.md, T1_W2_W3a_closeout.md) ... verified by scripts/verify_witness_gap.py

**问题** 10.2 的展望是全文答辩风险最高的一节，而支撑它的数值验证全部指向读者拿不到的仓库文件。等于说这一节的证据不在论文里。

**建议** 把这些验证摘成附录里的半页：验证了哪两个量、用什么参数、结果与公式差多少（例如已经写出的 0.119 对 0.12）。正文数字加附录证据，10.2 才站得住。


### AP-10 · 🟡 建议 · R3 英语文字编辑 · 术语与正文不一致

`en/A_reproduction.md:245`

> the exact affine conversion law ... rho_perfect - L1/2

**问题** 附录这里出现了 rho_perfect、affine conversion law 等 10.2 正文没有用过的名字，读者无法把两处对上。

**建议** 统一到 10.2 的措辞，或在此处加一句对照说明哪个量对应正文的哪个符号。

