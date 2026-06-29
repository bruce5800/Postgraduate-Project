# Research Plan C — The Limits of Predictions for Average-Case Online Matching

**Thesis (one sentence).** The recurring empirical wall of this whole project —
*on average-case inputs the advice-free baseline is near-optimal, so predictions are
robustness insurance, not performance* (finding F3, reconfirmed by M1, M3, and the
serving SLO probe) — is not a tuning artifact but a **theorem**: on strong-baseline
online matching, **no test-and-fallback algorithm with a sublinear test can capture
the consistency upside while staying robust**, because the upside sits *below the
statistical resolution* of any sublinear test.

**Why this is the right elevation.** Directions A (learn-to-rank) and the serving
rescue both died because they fought F3 and lost. Direction C stops fighting it and
**proves it**, turning the project's most-reconfirmed empirical finding into its
central theoretical contribution. It needs no feature divergence, no new regime — it
formalises what we already know is true, using assets we already built. Target:
SODA / ESA / ITCS / the algorithms-with-predictions venues. It is a **theory pivot**
(higher risk, higher ceiling), de-risked by the project's experimental strength:
every theorem is validated numerically in the existing harness before/while proving.

---

## 1. The three theorems (the contribution)

**T1 — No-free-lunch lower bound (the headline).** Fix a family of known-i.i.d.
matching instances on which the advice-free baseline (Ranking) achieves expected
ratio ≥ 1−δ. For ANY test-and-fallback algorithm that observes a prefix of k = o(n)
arrivals before committing to follow-advice or fall back, the achievable
(consistency, robustness) region **collapses toward the trivial "always fall back"
point as δ→0 relative to k**: it cannot be simultaneously (1−o(δ))-consistent and
(ρ_base−o(δ))-robust. Informally: *when the baseline is within δ of optimal and the
test sees o(1/δ) of the right signal, no threshold can both accept advice good enough
to help and reject advice bad enough to hurt.*

**T2 — Matching upper bound (the algorithm).** The **recalibrated-threshold**
test-and-fallback (replace the worst-case β by the measured baseline β̂, as in
`run_recalibration.py`) achieves the consistency/robustness frontier that T1 proves
is optimal, up to constants. So the recalibration we found empirically is not just a
fix — it is the *optimal* test-and-fallback on strong-baseline instances, and T1
says even it must give up the (vanishing) upside.

**T3 — Structural lower bound (why test-then-commit).** Any *dynamic switching*
combiner on online (irrevocable) matching that switches experts s times incurs
Ω(s · g) extra loss for a gap parameter g — so test-once-then-commit (s = 1) is the
optimal switching schedule. This formalises the **irrevocability hybrid penalty**
observed in ★2 (the eager combiner scoring below both experts) and explains why the
caching-style dynamic combiner (Chłędowski) does not port to matching.

Together: **a tight characterisation of what predictions can and cannot buy on
average-case online matching, with a matching optimal algorithm.**

## 1b. Prior-art verdict (C-M0 (a) — DONE)

**Verdict: NOVEL / unoccupied** — no paper proves a sublinear-test-and-fallback
*impossibility* coupled to baseline strength; the testing-sample-complexity ⟺
online-advice-value bridge and the few-types ⟺ near-optimal-baseline identification
are both genuinely unbuilt. But there is **one risk to manage** (see below).

Closest prior work (cite / position against):
- **Choo et al., "Online bipartite matching with imperfect advice," ICML 2024,
  arXiv:2405.09784** — introduces TestAndMatch; their threshold τ = 2(n̂/n − β) − ε
  **already couples acceptance to the baseline ratio β, but CONSTRUCTIVELY**; their
  only lower bound (Thm 3.1) is the standard *adversarial* indistinguishability (no
  algo is 1-consistent and >½-robust), NOT a sublinear-test resolution bound. **#1
  differentiation target.** Their tester is a Jiao–Han–Weissman L1 estimator with
  s ∈ O(r·log(1/δ)/(ε² log r)) on a reduced domain — exactly the resolution floor we
  lower-bound against.
- **Burathep–Erlebach–Moses (BEM), SOFSEM 2026, arXiv:2511.23388** — Test-and-Match+;
  **no lower bounds**; the most current algorithmic foil.
- **Wei & Zhang, NeurIPS 2020, arXiv:2010.11443** — canonical consistency/robustness
  lower bounds, but *problem-intrinsic Pareto frontier*, not testability-gated — cite
  to show T1 is a **different genre**.
- **Yoshinaga & Kawase, arXiv:2601.06813 (2026)** — accuracy→competitive-ratio as a
  monotone/concave curve; closest "no-free-lunch-adjacent" but *positive* and
  ski-rental, no test.
- **Jiao–Han–Weissman testers + "Augmented Testing of Discrete Distributions"
  (OpenReview tAlMAcqK9s)** — the sample-complexity engine, *explicitly not connected
  to online advice value* → the bridge T1 builds.

**THE RISK to pre-empt (reviewer: "isn't this just reading off Choo's threshold?"):**
Choo *exposes* the β-coupling in their algorithm design. T1 must therefore be a
**two-sided, information-theoretic impossibility** — show the consistency upside on
strong-baseline i.i.d. instances is *provably below the ε-resolution achievable by
ANY o(n)-prefix test at the relevant support size*, not merely that their particular
threshold tightens. The numerical C-M0 (noise_floor ≫ L1* whenever upside exists) is
exactly this two-sided statement in empirical form — the proof must make it general.

*(Source caveat from the prior-art pass: the verbatim Choo τ / Thm 3.1 text came via
the arXiv HTML v3, not the PDF — eyeball the published version before quoting.)*

## 2. Model & definitions (§2 of the paper)

- Known-i.i.d. online bipartite matching; competitive ratio = E[ALG]/OPT.
- Advice object (type histogram ĉ, as in Choo/BEM) and the **test-and-fallback
  class**: observe arrivals 1..k, compute a statistic, decide follow vs a fixed
  robust baseline, commit for k+1..n.
- **Baseline strength** ρ_base = E[Ranking]/OPT; **consistency** = ratio under
  perfect advice; **robustness** = worst-case ratio under adversarial advice.
- **Test budget** k (sublinear: k = o(n), the papers use k ≈ √n·log r).

## 3. The T1 construction (concrete enough to start proving)

A two-point (Le Cam) argument. Build two instance distributions that are
**statistically indistinguishable from a length-k prefix** yet require opposite
follow/fallback decisions:

- **D_good:** advice is correct; following it reaches OPT, beating the baseline by
  δ·OPT.
- **D_bad:** advice is subtly wrong; following it loses Δ·OPT (Δ ≫ δ), while falling
  back keeps ρ_base.

Construct D_good, D_bad so the per-arrival distributions differ only on a measure-δ′
event (the "informative" arrivals that reveal whether the advice will help). A
length-k prefix sees an informative arrival with prob ≈ k·δ′; if **k·δ′ = o(1)** the
prefixes have total-variation distance o(1), so no prefix-k rule distinguishes them.
Choosing δ′ so the consistency upside δ is Θ(δ′) gives: any algorithm capturing the
δ upside on D_good must follow, hence also follows on the indistinguishable D_bad and
suffers Δ. ⇒ the (consistency, robustness) tradeoff is forced.

**Minimal gadget to prove first (C-M0):** the *rare-resource* unit — offline nodes
A (popular) and B (rare); type-1 ~ {A,B}, type-2 ~ {A}. Following good advice sends
type-1 to B and saves A for type-2 (gain δ); bad advice sends type-1 to A and strands
type-2 (loss Δ). Tune arrival probabilities so the prefix can't tell which regime it
is in. Prove T1 here by hand, then lift to the few-types family.

## 4. Plan / milestones (de-risk fastest first; numerics before proofs)

- **C-M0 — prior-art check + minimal theorem + numerical validation (the de-risk).**
  (a) Literature pass — IN PROGRESS (prior-art agent). (b) Prove T1 on the
  rare-resource gadget by hand — pending. (c) **Numerical validation — DONE & POSITIVE**
  (`scripts/run_impossibility_frontier.py`, `results/impossibility_frontier.png`).
  Sweeping the number of types r (= the count/type and ρ_base knob), the **scissors**
  is exactly as T1 predicts: the POTENTIAL upside (perfect advice − baseline) rises
  from 0 to +0.063 as ρ_base falls 1.00→0.937, while the sublinear-test-CAPTURABLE
  upside stays pinned at ≤0.002. The mechanism panel confirms why: the test's emp-L1
  **noise floor at k=√n** (0.59→1.85, rising with r) sits **far above the breakeven
  L1\*** (the margin good advice needs, 0.96→0.12, falling with r) at every point
  where upside exists — so the test cannot separate good from bad advice. Only the
  r=16 point is "testable" (noise floor < L1\*), and there ρ_base=1.00 (no upside).
  **Net: wherever you can test, you don't need to; wherever you'd need to, you can't.
  T1 is empirically real — proceed to the proof.**
- **C-M1 — generalise T1** to the few-types family; pin the exact δ-vs-k tradeoff
  (the form of "o(δ)" / the testability threshold).
- **C-M2 — T2 upper bound:** analyse the recalibrated threshold (concentration of β̂
  + the empirical-L1 estimator), show it attains the T1 frontier.
- **C-M3 — T3 structural bound:** adversarial construction for the s-switch dynamic
  combiner; show s = 1 optimal.
- **C-M4 — experimental validation of all three** (reuse the harness:
  `run_recalibration.py`, the combiner, the order-error machinery) + write-up.

## 5. Risks & mitigations (honest)

| Risk | Mitigation |
|---|---|
| **Theory may not close** (this is the real risk; proofs are hard and binary) | Start with the hand-provable gadget (C-M0); a special-case theorem + experimental validation of the general case is still a contribution. Numerics first means we never invest proof effort in a false statement. |
| **Prior art exists** (someone proved a similar bound) | C-M0 step (a) is a deep-research prior-art pass BEFORE proving — same discipline as the original literature review. |
| **Theory-skill ramp** (project has been experimental) | Le Cam two-point bounds are among the most accessible lower-bound tools; the gadget is tiny; lean on numerical verification at every step. |
| **T1 true but with ugly/loose constants** | A clean *qualitative* impossibility (region collapses as δ→0) is already the contribution; tight constants are a bonus. |
| **Scope creep across T1/T2/T3** | T1 alone (with experimental validation) is a paper. T2/T3 are bonus theorems that strengthen it; drop them if time-constrained. |

## 6. How the existing work folds in

- **Empirical seed of T1/T2:** `run_recalibration.py` already shows the resolution
  limit (recalibrated τ falls below the estimator noise floor → can't accept advice).
  That figure becomes the experimental validation of T1.
- **Empirical seed of T3:** the ★2 combiner hybrid penalty (`tests/test_combiner_small.py`,
  `docs/UNIFIED_BENCHMARK.md` §3).
- **The whole experimental paper (★1–★4 + M0–M3 + serving probe)** becomes the
  empirical companion / motivation: "we observed F3 everywhere; here we prove it."
- This is the **theory layer on top of** the existing experimental layer — they ship
  together (one strong paper) or as companion papers.

## 7. Immediate next action (C-M0)

Two things, both cheap and decisive, runnable now:
1. **Numerical impossibility frontier** — in the existing harness, directly measure
   the (consistency, robustness) tradeoff achievable by the best test-and-fallback as
   a function of baseline strength ρ_base and test budget k, and show the achievable
   region collapses to "always fall back" as ρ_base→1. This is the experimental
   statement of T1 and tells us the theorem is true before we prove it. *(I can build
   `scripts/run_impossibility_frontier.py` now.)*
2. **Prior-art pass** — a deep-research check that the baseline-strength-dependent
   test-and-fallback lower bound is unoccupied.

If the frontier collapses as predicted and the prior-art is clear, proceed to prove
T1 on the rare-resource gadget.
