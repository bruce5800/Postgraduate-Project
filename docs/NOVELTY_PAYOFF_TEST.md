# Novelty pass — payoff-testing acceptance rules (2026-07-29)

**Question.** Has anyone, in the learning-augmented / algorithms-with-predictions
literature, proposed deciding whether to follow advice by testing the *payoff* of
following (rather than the prediction's distance to the truth) — in particular a
test-then-commit rule on a prefix?

**Verdict: NOT FOUND — the claim survives, with three positioning debts to pay.**
Confidence: good but not exhaustive (8 targeted searches, 4 deep reads, including the
foil group's own April-2026 survey talk of their line; a Scholar citation-trace of
Choo24 would be the completionist step).

## What the sweep found

1. **The nearest active line — "test-before-trust" (Choo, Gouleakis, et al.) — tests
   DISTANCE, not payoff.** Choo et al. ICML 2024 [choo2024imperfect] gate on empirical
   $\ell_1$; Bhattacharyya–Choo–John–Gouleakis, *Product distribution learning with
   imperfect advice*, NeurIPS 2025 (arXiv:2511.10366) gates on TV/$\ell_1$ closeness of
   mean vectors (no test-then-commit); Gouleakis's Apr-2026 talk ("Test Before You
   Trust", UC Irvine) frames the whole program as *statistical validation of the
   prediction* — distributional throughout. Our §7.7 ("the distance is the wrong
   statistic; the payoff is per-sample observable") is a direct, differentiated
   engagement with this line, not a duplication of it. **Risk note: the group is active
   in exactly this space as of April 2026 — arXiv sooner rather than later.**
2. **Switching/combining frameworks switch on prediction quality or regret, not on a
   committed payoff test.** Antoniadis–Shahheidar–Shahkarami–Soltani,
   *SemiTrust-and-Switch* for interval scheduling (arXiv:2511.16194): switching tied to
   prediction quality. The caching/MTS combiner genre (Chłędowski et al., Blum–Burch)
   switches dynamically on observed regret — payoff-flavored but *dynamic*, and §5.5
   shows dynamic switching breaks under matching's irrevocability; the commit-once
   payoff test is the structurally different object.
3. **Distributional-advice-of-unknown-quality (ski rental etc.) hedges, it does not
   test.** Cui–Dinitz (arXiv:2602.21104), Diakonikolas et al. ICML 2021: no prefix, no
   commit decision; adjacent access models, cite in the cluster.

## The three positioning debts (a referee will raise them; pre-empt)

- **Data-driven algorithm selection** (Gupta–Roughgarden ITCS'16/SICOMP'17; Balcan's
  survey chapter): choosing between algorithms from samples with $O(1/\mathrm{gap}^2)$
  uniform-convergence bounds. *Differentiation:* their samples are whole instances with
  directly observable per-instance performance; here one instance's k-arrival prefix
  must reveal a policy's *full-horizon* value, which is generally impossible — the
  payoff identity is precisely the structure that makes it possible on cell families
  (and §5.4's bootstrap handles the concave case). Cite and say this.
- **Sequential analysis** (Wald 1947): the $1/g^2$ budget flavor is classical; the
  contribution is not the statistics but the identity + the exact
  $\sigma^2 = 2(1-\rho_{\mathrm{base}})$ tie + the matching lower half + the refutation.
  Cite and say this.
- **Newest test-before-trust work**: cite arXiv:2511.10366 alongside Choo24 so the
  related-work is current to the foil group's output.

## Actions taken

References added (gupta2017pac, balcan2020datadriven, wald1947sequential,
bhattacharyya2025product, antoniadis2025switching, cui2026skirental); paper §7 intro and
§7.8 "literature pass in progress" placeholders resolved with the differentiated
positioning; §9 related work gains an "algorithm selection and sequential testing"
paragraph. This note is the record; searches run 2026-07-29.

---

## Second pass — adversarial, targeted at sequential analysis / BAI / OPE (2026-08-14)

Motivated by the review note ranking "classical statistics in new clothes" as the #1
kill risk, and by the first pass's known hole (best-arm identification uncovered).

**Searches:** passive-observation policy selection lower bounds; BAI × learning-augmented
acceptance rules; off-policy evaluation for two-policy comparison on logged/passive data.

**Findings:**
1. **BAI is uniformly an *active-pull* model** (Mannor–Tsitsiklis 2004 lower bound;
   Kaufmann–Cappé–Garivier 2016 canonical characterization; fixed-budget/confidence
   variants, restless, linear — all pull arms and observe the pulled arm's reward). No
   passive-stream variant found in which neither actions nor rewards are observed.
2. **OPE** consumes logged *actions with propensities* from a behavior policy (Dudík–
   Langford–Li 2011 and successors) — again not our observation model.
3. **New same-domain paper found and cited:** Choo–Jin–Shin, *Learning-Augmented Online
   Bipartite Fractional Matching*, NeurIPS 2025 (arXiv:2505.19252) — blending/Pareto
   design for the fractional relaxation, no testing; complementary, now cited in §9.
   (Second active front from the Choo group — reinforces the arXiv-urgency call.)

**Verdict unchanged, defense sharpened:** no prior work extracts a policy pair's value
gap from a *passive arrival stream* (no actions, no rewards) or proves a rule-independent
rate for it. The paper now says this in three places: abstract (deliberately-classical
pre-emption sentence), §7 intro (BAI clause with the active-vs-passive distinction), §9
(rewritten "Algorithm selection, best-arm identification, and sequential testing"
paragraph). New citations: MT04, KCG16, DLL11, CJS25.
