# Direction C — Advisor Talk (theory: the limits of predictions for online matching)

Audience: your advisor — technical, but seeing this for the first time. Goal: they
leave understanding (1) what the theorem claims, (2) why it's true, (3) what is
*proven* vs *sketched*, (4) whether it's worth pushing to a theory venue. ~15–18 min.
*Italics* = stage directions / what to put on the board, not lines to read.

Reference docs to have open: `docs/RESEARCH_PLAN_C.md`, `T1_PROOF_SKELETON.md`,
`T1_W1_single_cell.md`, `T1_W3_construction.md`, and the figure
`results/impossibility_frontier.png`.

---

## 0. The one-sentence pitch (30 sec)

"Across all my experiments, predictions for online matching turned out to be
*robustness insurance, not a performance lever* — the advice-free baseline is already
near-optimal on average-case inputs. I now think that's not a coincidence but a
**theorem**: for the test-and-fallback algorithms in the recent papers, on
strong-baseline instances **no sublinear-test algorithm can be both consistent and
robust** — *wherever you can test the advice, you don't need it; wherever you'd need
it, you can't test it.* I have a proof skeleton with the core lemma rigorous and the
rest reduced to a standard distribution-testing lower bound. I want your read on the
last gap and on whether to push it to a theory venue."

---

## 1. Where this comes from — the empirical wall (2 min)

*One line of context, don't belabour — they know the experimental project.*

"My experimental study kept hitting the same wall, which I call F3: on average-case
i.i.d. matching, KVV Ranking already gets ≈0.95–0.99 of OPT, so the *consistency*
upside of any predictor is tiny; the value of predictions is preventing the
*downside* of trusting bad advice. I confirmed this on synthetic graphs, six real
graphs, real request traces, and an SLO/tail serving objective — four different ways,
same wall. So instead of fighting it, I want to **prove** it."

*Pause.* "The clean place to prove it is the **test-and-fallback** family — Choo et al.
ICML 2024 and Burathep–Erlebach–Moses SOFSEM 2026. These observe a sublinear prefix of
arrivals, run a distribution test on the advice, then either follow it (Mimic) or fall
back to Ranking."

---

## 2. The claim and the picture (2 min)

*Board: draw the two axes — x = baseline strength ρ_base, y = consistency upside.*

"Define **consistency** = ratio under good advice, **robustness** = ratio under bad
advice, **ρ_base** = Ranking's ratio (the baseline strength), and the **test budget**
k = o(n) (sublinear — the papers use ≈√n)."

*Show `results/impossibility_frontier.png`.* "Here's the empirical statement. The
**green** curve is the *potential* upside — how much perfect advice beats the baseline;
it rises as the baseline weakens. The **red** curve is what a sublinear test can
*actually, safely* capture — it stays pinned at zero. That gap is the impossibility:
the upside exists but is uncapturable."

*Point at the second panel.* "And here's *why*, in one measurement: the test's
resolution — the empirical-L1 noise floor at k=√n — sits far above the margin it would
need to resolve (the breakeven advice error). The only regime where the test *can*
resolve (left edge) is where the baseline is already perfect, so there's nothing to
capture. **Wherever you can test, you don't need to.**"

---

## 3. The structural reason — say it before the math (1 min)

"The intuition is a coupling. The test is a *distribution test* on the type histogram.
For it to work on a sublinear prefix, you need **few types, each arriving many times** —
otherwise the histogram is unestimable. But few high-count types is *exactly* the
near-perfect-matchable regime where Ranking is already optimal. So the precondition for
the test to be feasible is the precondition for the baseline to be near-optimal. The
two are the same structural knob — that's the theorem in one sentence."

---

## 4. The proof, in three pieces (6–7 min — the core)

### Piece 1 — the master inequality (rigorous). *Board.*

"Take two instance distributions G (advice good) and Bd (advice bad) with the **same
advice** σ. Following σ gains δ under G, loses Δ under Bd, vs the baseline. Let γ_k =
total-variation distance between the two distributions *of the length-k prefix*. Then
for any test-and-fallback algorithm:"

*Write:*  **(1 − η_c) ≤ η_r + γ_k + o(1)**

"where η_c = the fraction of the upside it gives up, η_r = its robustness loss as a
fraction of Δ. The proof is two lines: the decision F/R is a function of the prefix and
σ; since σ is identical and the prefixes are γ_k-close in TV, the follow-probability
differs by ≤ γ_k between G and Bd; plug into the definitions of consistency and
robustness. **So if the prefix can't distinguish G from Bd (γ_k → 0), you can't be both
consistent (η_c→0) and robust (η_r→0).** This part is airtight."

*Anticipate:* "This is a Le Cam two-point argument — standard machinery, but the
*two-sided* framing for test-and-fallback is the point."

### Piece 2 — the reduction to a known lower bound (the key move). *Board.*

"Now I make it about **any algorithm**, not just the specific test. The prefix is
*literally k i.i.d. samples from the type distribution p*. A consistent-and-robust
algorithm must, from those k samples, decide whether following the advice helps or
hurts — and I show (Lemma W3a) that 'helps' ⟺ L1(p, q) ≤ a and 'hurts' ⟺ L1(p, q) ≥ b
for the advice q. So **the algorithm solves tolerant identity testing**: distinguish
‖p−q‖₁ ≤ a from ≥ b, q known."

"That problem has a known sample-complexity **lower** bound — Valiant–Valiant,
Jiao–Han–Weissman:"

*Write:*  **k = Ω( r / ((b−a)² · log r) )**

"This is the same estimator the papers *use* for their upper bound; I'm invoking its
lower side. The reduction is what makes the impossibility information-theoretic — it
rules out *any* decision rule on the k samples, not just thresholding the empirical L1."

### Piece 3 — the construction makes r = Θ(n) (verified). *Board: draw one cell.*

"To use that bound I need a family where r is large and the L1-gap maps to a real
matching gap. The gadget is a **rare-resource cell**: a flexible request that must be
routed before a specialist arrives; route it to save the scarce resource and you match
both, guess wrong and you strand the specialist."

*Write the W1 numbers:* "Per cell I computed in closed form, and **verified
numerically to three decimals**:
- OPT = 1+θ, Baseline = 1+θ/2,
- advantage of following = **±θ·|s−½|** (sign = is the advice's direction right?),
- L1 between truth and advice = **2θ·|s−ŝ|**.
So per cell, ρ_base = 1−Θ(θ), and the upside δ = Θ(ε·(1−ρ_base)) where ε=|s−½|."

"Now take **m = Θ(n) independent cells, each a distinct type** → support r = Θ(n), each
type seen O(1) times. The advantages and L1s add up; I verified the aggregate
**follow-ratio decreases monotonically through the baseline, crossing at the point
where half the advice directions are wrong** — so there are constants a<b with gap Θ(1)
giving a Θ(1) consistency gap. Plug r=Θ(n), b−a=Θ(1) into the testing bound: **k = Ω̃(n)**
samples are needed. A sublinear k = o(n/log n) can't — done."

*This is the assembled theorem:* "For any sublinear k, there's a known-i.i.d. matching
family with r=Θ(n), ρ_base = 1−Θ(1), on which no test-and-fallback algorithm is both
(1−o(1))-consistent and (ρ_base−o(1))-robust."

---

## 5. Novelty — and the one risk I must defend (2 min)

"I ran a prior-art pass. Verdict: **novel**. Nobody proves a sublinear-test
impossibility coupled to baseline strength; the bridge from *distribution-testing
sample complexity* to *the value of advice in an online algorithm* is genuinely
unbuilt, and the 'few-types ⟺ near-optimal-baseline' identification is new."

"**The one risk to pre-empt:** Choo et al.'s acceptance threshold is τ = 2(n̂/n − β) − ε
— the baseline ratio β is *already in their threshold*, constructively. A referee will
ask 'isn't this just reading off their threshold?' My answer is Piece 2: the bound is
**information-theoretic**, ruling out *any* function of the k samples, not just their
particular threshold. That's the whole reason I route through the testing lower bound
rather than analysing their τ."

*Closest related work to name-drop:* Choo 2024 (the algorithm I invert), BEM 2026 (no
lower bounds), Wei–Zhang 2020 (consistency/robustness lower bounds, but a different
genre — problem-intrinsic, not testability-gated), Yoshinaga–Kawase 2026 (accuracy→ratio
as a positive curve, not an impossibility).

---

## 6. Honest status — what's proven vs what remains (2 min)

*Be straight here — this is what you want their judgment on.*

| Piece | Status |
|---|---|
| Master inequality (Lemma 1) | **Rigorous, self-contained.** |
| Reduction to tolerant testing (Lemma 2) | Clean — the prefix *is* i.i.d. samples. |
| Single-cell constants (W1) | **Closed-form + numerically verified.** |
| Aggregate conversion (Lemma W3a) | **Numerically verified**; needs the analytic monotonicity write-up (routine — sum of independent monotone terms). |
| Testing lower bound (Lemma 3 / W2) | **CONFIRMED** — Canonne–Jain–Kamath–Li (COLT 2022): tolerant identity testing is Θ̃(n/log n) at constant tolerance (vs √n non-tolerant); our good side is a Θ(1) ball (a>0) so we're provably in the tolerant regime. |
| Conversion law (W3a) | **PROVEN as an exact affine law** E[follow-ratio] = ρ_perfect − ½·L1(p,q) (derived + verified to 3 decimals); it also guarantees a>0. |
| Final assembly | Closed to one routine step: name two witness distributions at L1=a, b (the affine law makes any such pair work; VV gives one that's prefix-indistinguishable). |

"So: the core is rigorous, the construction is verified, the tolerant-testing bound is
confirmed on the theorem-preserving side, and the conversion is an exact affine law —
**no step needs new mathematics to be invented, and the one external dependency (the
tolerant-testing lower bound) is a cited, exact, modern result.** The honest scope is
that the strong form holds for r=Θ(n); the all-regime 'scissors' is that plus the trivial
strong-baseline side plus the numerical figure as the unifying picture."

---

## 7. What I'd like your input on (1 min)

1. **Is the reduction airtight to you?** I've confirmed the tolerant identity-testing
   bound (Canonne et al. 2022 give Θ̃(n/log n) at constant tolerance, and our good side
   is a Θ(1) ball so we're in that regime). The one thing I'd like you to sanity-check is
   the *instance match*: naming the two witness distributions (p_G at L1=a, p_Bd at L1=b)
   from the VV hard instance so they're prefix-indistinguishable — any subtleties
   (Poissonization, the exact VV construction) I should worry about?
2. **Is the r=Θ(n) restriction acceptable**, or should I aim for a bound that bites at
   constant r too? (My read: r=Θ(n) is the only regime with upside, so it's the right
   regime — but I want your view on how a referee sees it.)
3. **Venue / scope:** is this a standalone theory paper (SODA/ESA/ITCS track), or does
   it ride as the theory section of the experimental paper? The experimental study
   (benchmark + order-error + real-graph universality) is the empirical companion either
   way.

---

## Cheat-sheet (numbers / facts you might be asked)

| Question | Answer |
|---|---|
| Master inequality | (1−η_c) ≤ η_r + γ_k + o(1); η_c=upside forgone, η_r=robustness loss / Δ |
| Per-cell advantage / L1 | ±θ|s−½|  /  2θ|s−ŝ|  (closed form, verified) |
| Baseline / upside coupling | ρ_base = 1−Θ(θ),  δ = Θ(ε·(1−ρ_base)) |
| Aggregate law (W3a) | **exact affine:** E[follow-ratio] = ρ_perfect − ½·L1(p,q); breakeven L1* = 2(ρ_perfect−ρ_base) ≈ 0.22 (verified) |
| Testing lower bound (confirmed) | tolerant identity testing = Θ̃(n/log n) at constant tolerance (Canonne–Jain–Kamath–Li 2022); non-tolerant would be √n — we're tolerant (a>0) |
| Why "any rule" not just Choo's τ | the prefix is i.i.d. samples ⟹ information-theoretic testing bound |
| Numerical evidence | `results/impossibility_frontier.png` — the scissors + the resolution-vs-margin panel |
| Remaining work | one routine step — name the two witness distributions at L1=a, b (affine law makes any pair work) |
