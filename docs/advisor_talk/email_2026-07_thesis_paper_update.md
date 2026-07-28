# Advisor email — thesis + paper update (drafted 2026-07-28)

Attachments to include: `thesis/latex_school/thesis.pdf`, `docs/paper/latex/itcs_main.pdf`,
`docs/T1_WITNESS_GAP.md` (as-is or exported to PDF).

---

**Subject:** Updated thesis & paper draft — an important theory correction, and an ITCS 2027 plan

Dear [Advisor's name],

I hope you are well. I'm attaching the updated thesis and the current paper draft. There have been substantial developments since our last discussion — including one important correction — so I'd like to summarise them briefly before we next meet.

**1. The impossibility theorem was false as stated — I found a counter-example while completing the proof.**
While writing out what we believed was the last routine step (exhibiting the witness pair for the tolerant-testing reduction), I discovered the step cannot be completed. On our cell construction, the payoff of following the advice equals exactly half the expectation of a simple per-arrival statistic (+1 for an advice-favoured specialist, −1 for a disfavoured one, 0 for a flexible request). Consequently, a trivial rule — *follow iff this statistic is positive on the prefix* — is simultaneously consistent and robust with a prefix of only O(log n), contradicting the claimed impossibility for all k = o(n/log n). I verified this numerically: the rule's total error is ≈0.007 at k = 200 and stays flat as n grows from 3,200 to 320,000. The flaw is that our reduction produced a *promise-restricted* tester, while the tolerant-testing hard instances lie outside the promise. The full analysis, including exactly which lemmas survive, is in the attached note (T1_WITNESS_GAP).

**2. What survives is, I believe, a cleaner and more defensible result.**
The master trade-off inequality and the cell/affine-law lemmas are untouched. The correct statement is a sharp, two-sided **budget–stakes law**: the follow/fallback decision costs a prefix of k\* = Θ̃(θ/δ²) — below this budget *no* rule is both consistent and robust (a short Hellinger argument through the master inequality), and at this budget the directional statistic above achieves it. The corollary recovers the wall where it matters: stakes are capped by the baseline slack, so on strong-baseline instances any upside below ≈ √((1−ρ_base)/n) is uncapturable at *any* feasible prefix — which matches the Chapter 6 measurements quantitatively. Both halves use only elementary tools.

**3. The thesis: I have moved the theory out of it.**
With the defence and the September deadline in mind, I removed the theory chapter from the thesis and kept a one-page outlook in the conclusion (§10.2), which claims nothing beyond the proved trade-off inequality plus a quantitative reading of our own experiments. The thesis is retitled accordingly ("… A Unified Experimental Study"; 68 pages in the university template, attached). I hope this scoping seems right to you — I'm happy to revisit it if you'd prefer the theory to stay in.

**4. The paper: reframed around the budget–stakes law, and I'd like to target ITCS 2027.**
The attached 20-page draft is in LIPIcs format under the new title ("… and a Budget–Stakes Law"). ITCS 2027 has a single deadline of **4 September 2026** (double-blind), which would let us submit before I graduate, while ITCS's emphasis on conceptual contributions suits both the law and the honest refutation story. The realistic alternatives are AISTATS (8 October) and ICML (late January).

What I would most value from you:
(a) a pass over **Section 7** of the paper — the law and its two short proofs;
(b) your view on **ITCS vs. a later venue**;
(c) whether we should post to **arXiv** once you are satisfied with Section 7.

Could we find 30–45 minutes this week or next? If you read one thing beforehand, I'd suggest the witness-gap note — it is short and contains the whole story.

Thank you, as always, for your guidance.

Best regards,
Zhuolun
