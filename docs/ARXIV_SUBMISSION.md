# arXiv 提交流程（为本论文定制，2026-08-14）

投稿包已生成并本地验证：`paper/latex/arxiv/arxiv_submission.tar.gz`（31 页、12 图、
0 未解析引用、1.1MB；`build_arxiv.sh` 随时可重新生成）。以下按顺序走。

## 0. 提交前的四件小事（约 20 分钟）

- [ ] **补作者信息**：`paper/latex/talg_main.tex` 第 21/26 行 —— 确认注册姓名拼写、
      把 `zhuolun66@gmail.com` 换成 Bristol 邮箱（arXiv 与期刊都以此为准）。改完重跑
      `./build_arxiv.sh`。
- [x] **LLM 使用披露已加入** `talg_main.tex`（`\begin{acks}` 块，位于附录与参考文献之间，
      2026-08-21）。**措辞以你本人口吻陈述，提交前请审改**；当前文本：

      Large language model assistance (Anthropic's Claude) was used throughout this
      project — for code, drafting, analysis, and the Lean proof scripts. All results
      were independently verified by the author: the experiments through the released
      seeded artifact, the theory line by line, and the statistical chain of Section 7
      additionally by the Lean 4 kernel (Appendix C; 66 theorems and lemmas, no sorry).
      Any remaining errors are the author's own.

- [ ] **Lean 声明要属实**：(a) 把 `budgetstakes/` 推到 GitHub 主分支（CI 会自动跑
      `lake build`）；(b) 附录 A 现在写明 artifact 含 `budgetstakes/`——现有 release tag
      `talg-submission-2026-08` 是 Lean 之前切的，**需重新打包 `talg-artifact.zip`（含
      `budgetstakes/`，不含 `.lake/`）并更新/新建 release tag**，再核对附录 A 的 URL。
- [ ] 最后重跑一次 `./build_arxiv.sh`，目检 `arxiv/arxiv_main.pdf` 首页。

## 1. 账号与背书（首次投稿者最大的坑，可能需要数天提前量）

1. 到 arxiv.org 注册账号 —— **务必用 Bristol 邮箱**（机构域名大幅提高自动获得
   投稿资格的概率）。
2. 选定主分类 **cs.DS** 后，系统可能提示需要 **endorsement**（新投稿人机制）。
   若被要求：需要一位在 cs.DS 发表过的研究者输入你的背书码。候选人：导师（注意——
   背书只确认"此人是正规研究者"，**不是**为论文内容背书，与其拒绝共同署名不冲突，
   邮件里说明这一点）；或系里任何发过 cs.DS/cs.LG 的老师。**这一步可能等几天，
   建议今天就注册触发流程。**

## 2. 上传与编译

1. Start New Submission → License：选默认的
   **arXiv.org perpetual, non-exclusive license**（最保守，与日后 ACM/TALG 版权
   流程无冲突；不要选 CC-BY，除非你明确想要）。
2. 上传 `arxiv_submission.tar.gz`。包内已含 `.bbl`（arXiv 不跑 bibtex）、重写为
   `figs/` 的图片路径、且不含本地 hyperxmp 桩（arXiv 的 TeX Live 有真包）。
3. arXiv 在线编译 → 查看生成的 PDF。若报错，对照日志修（最常见是包版本差异；
   我们已本地用同构方式验证过，预期一次通过）。

## 3. 元数据

- **Title**: The Limits of Predictions for Online Bipartite Matching: A Unified
  Experimental Study and a Budget–Stakes Law
- **Authors**: Zhuolun Li
- **Abstract**: 直接用 `paper/latex/arxiv/abstract.txt`（已转纯文本；粘贴后检查
  一遍引号/破折号；数学可保留 `$...$`）。
- **Primary category**: `cs.DS`；**Cross-list**: `cs.LG`（learning-augmented 读者
  群在那边——Choo24 一脉都是 ICML/NeurIPS）。
- **Comments 栏**（可选但建议）: "31 pages, 9 figures. Code and seeded artifact:
  https://github.com/bruce5800/Postgraduate-Project"
- MSC/ACM class：可留空。

## 4. 提交与公告节奏

- 工作日 **14:00 ET（北京时间约凌晨 2 点）** 前完成提交 → 次个工作日 20:00 ET 公告。
- 提交后处于可撤回状态；公告后**不可删除**，只能出新版本（v2、v3…）——所以第 0 节
  的检查要在按键前做完。
- 少数首投会进入人工审核（on hold），几天属正常，不要重复提交。

## 5. 公告后（拿到 arXiv ID 当天）

- [ ] README 的论文行加 arXiv 链接；`docs/paper/00` 头注记录 ID。
- [ ] GitHub release 说明里回填 arXiv 链接（引用闭环）。
- [ ] **随即启动 TALG Empirical Track 投稿**（ACM 投稿系统），cover letter 三句
      定位已备好素材：JEA 谱系（Borodin et al. 即发表于 JEA）、artifact 先行、
      "experimental analysis of algorithmic behavior in the JEA tradition"。
- [ ] 若 Gouleakis 组后续有新作，arXiv 时间戳自此起效。

## 常见故障排查

| 症状 | 处置 |
|---|---|
| 编译失败：找不到图 | 确认 tar 内 `figs/` 与 `ch/*.tex` 的路径一致（重跑 build_arxiv.sh 重新打包） |
| 参考文献变问号 | `.bbl` 未进包或文件名与主 tex 不一致（须为 `arxiv_main.bbl`） |
| acmart 版式异常 | arXiv 的 acmart 版本差异；对照本地 `arxiv/arxiv_main.pdf`，通常无实质影响 |
| 被要求 endorsement | 见第 1 节；这是流程性门槛，找任何 cs.DS 发表者即可 |
