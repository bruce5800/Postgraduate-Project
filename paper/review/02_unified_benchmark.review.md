# §3 Unified benchmark — 审读批注

共 4 条：🔴 必改 3 · 🟡 建议 1 · ⚪ 可选 0。

批注原件在 `02_unified_benchmark.md` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。

---
### 2-01 · 🔴 必改 · P4 体例校对 · 代码名进正文

`02_unified_benchmark.md:56`

> Panel A - clvb_zipf

**问题** clvb_zipf 是生成器标识符，带下划线出现在表里。审稿人不知道 clvb 是什么，也看不出这个面板测的是什么。

**建议** 改成可读名（heavy-tailed degrees (Zipf)），把脚本标识符放进复现附录。


### 2-02 · 🔴 必改 · P4 体例校对 · 三个 floor 不可比

`02_unified_benchmark.md:67`

> Ranking (floor) 0.948 / Greedy = Ranking (floor) 0.890 / Ranking (floor) 0.990

**问题** 三个面板的 floor 是三个不同的数，来自不同图族，表里没有任何提示；两族的质量列语义也不同却同名并排。审稿人第一反应是横向比较。

**建议** 表注加一句：floor 是 Ranking 在该面板自身图族上的比值，面板之间不可比；两族的质量列同样只在面板内部可比。


### 2-03 · 🔴 必改 · P2 领域审稿人 · 无条件断言

`02_unified_benchmark.md:99`

> A practitioner using either unguarded is strictly worse off than using no prediction at all.

**问题** strictly worse off 是无条件的，但同一张表里 MPD 在 perfect 与 noisy 两列都高于 floor。这句话能被自己的表格直接反驳。

**建议** 补条件：under adversarial or garbage advice。一个从句的事。


### 2-04 · 🟡 建议 · P5 审稿意见预演 · 自我表扬

`02_unified_benchmark.md:136`

> This pairing is visible only under a unified table.

**问题** visible only 是对自己方法论的表扬，且容易被反驳（分别做两组实验也能看到）。审稿意见里这类句子是免费靶子。

**建议** 去掉 only：a pairing that a unified table makes immediate。

