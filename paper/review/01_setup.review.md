# §2 Setup — 审读批注

共 2 条：🔴 必改 1 · 🟡 建议 1 · ⚪ 可选 0。

批注原件在 `01_setup.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

---
### 1-01 · 🔴 必改 · P7 复现审稿人 · 未解析的交叉引用

`01_setup.md:112`

> listed with its output in Appendix [REPRO]

**问题** 这是一个没被替换掉的占位符，它已经原样印进 talg_main.pdf 的正文（第 3 页）。而且论文里并没有复现附录——学位论文有，这篇没有。审稿人看到 Appendix [REPRO] 会立刻怀疑稿件的成熟度。

**建议** 两件事：把占位符换成真正的指向；并补一个简短的复现附录（图表→脚本映射、种子、外部数据获取方式）。学位论文附录 A 可以直接压缩移植。


### 1-02 · 🟡 建议 · P7 复现审稿人 · 外部数据前提

`01_setup.md:122`

> every figure and table in this paper is regenerated from a fixed seed by a single script

**问题** 第 6、8 节的真实图与 trace 结果需要先获取外部数据，而这句话让审稿人以为克隆代码即可复现全部。artifact evaluation 会当场卡住。

**建议** 补半句区分自足脚本与需要外部数据的脚本，并给出后者的获取方式（与新增的复现附录合并）。

