# W1 — the single-cell lemma (theory "M0" for T1)

**Status:** DONE. The single rare-resource cell is computed in closed form and
**verified numerically to 3 decimals** (sim in the commit message of this work; all
five identities match). This is the smallest hand-checkable piece of the T1
construction: it gives the exact conversion between *advice quality* and
*matching advantage*, which is what lets the distribution-testing lower bound
(Lemma 3) transfer to the matching problem. The dimension-based hardness still lives
in the aggregation (W3 / Lemma 4 — flagged at the end); W1 supplies the per-cell
constants it needs.

## The cell

Two offline resources {a, b}. Arrivals, in order:
1. a **flexible** request F (neighbourhood {a, b}) — *always* arrives, routed *before*
   the specialist is seen;
2. one **specialist**: type α (neighbourhood {a}) w.p. θs, type β (neighbourhood {b})
   w.p. θ(1−s), or *none* w.p. 1−θ.

Parameters: θ ∈ (0,1] the **contention rate**, s ∈ [0,1] the **bias** (which specialist
is more likely). The advice is a predicted bias ŝ; "following" it (Mimic) routes F to
*protect the predicted-majority specialist*: ŝ > ½ ⟹ route F→b (save a for the likely
α); ŝ < ½ ⟹ route F→a. (This is exactly what build_advice_matching does on the cell's
advice graph.)

## Lemma W1 (closed form; ✓ numerically verified)

Per cell, in expectation:

| quantity | value |
|---|---|
| **OPT** | 1 + θ |
| **Baseline** (Ranking: route F uniformly) | 1 + θ/2 |
| **Mimic, advice in the RIGHT direction** (sign(ŝ−½)=sign(s−½)) | 1 + θ·max(s, 1−s) |
| **Mimic, advice in the WRONG direction** | 1 + θ·min(s, 1−s) |

Hence the **per-cell advantage of Mimic over the baseline**:

> **Mimic − Baseline = + θ·|s − ½|  (right direction)   /   − θ·|s − ½|  (wrong direction).**

And the **L1 distance** between the cell's realised specialist distribution
p = (θs, θ(1−s), 1−θ) and the advice q = (θŝ, θ(1−ŝ), 1−θ):

> **L1(p, q) = 2θ·|s − ŝ|.**

*Derivation.* Routing F→a yields E[matches] = 1 + θ(1−s) (F always matched; the
specialist matched unless it is α, which wants the now-taken a): = θs·1 + θ(1−s)·2 +
(1−θ)·1 = 1 + θ(1−s). Symmetrically F→b yields 1 + θs. Baseline averages the two →
1 + θ/2. The better route is F→b iff s > ½ (protect the likely α), giving
1 + θ·max(s,1−s); the wrong route gives 1 + θ·min(s,1−s). OPT = 2 when a specialist
comes (prob θ) else 1 → 1 + θ. The L1 is a 3-term computation with the (1−θ) "none"
coordinate cancelling. ∎

**Numerical check (T=4·10⁵ trials/cell):** e.g. θ=0.6, s=0.7 → OPT 1.600, Baseline
1.301 (formula 1.300), Mimic+ 1.419 (1.420), Mimic− 1.180 (1.180), advantage ±0.119
(formula ±0.120). The s=½ row gives advantage 0.000 — *advice is worthless exactly
when the truth carries no signal*, as it must.

## Reading W1 (what it says)

Two things separate cleanly, which is the whole point:
- the **magnitude** of the advantage, θ·|s−½|, depends only on the **truth's signal**
  |s−½| (how contested the cell is), NOT on the advice;
- the **sign** (gain vs loss) depends only on whether the **advice has the right
  direction** (same side of ½).

So "is the advice net-helpful?" = "does it get the cells' *directions* right?", and
the value at stake per cell is θ|s−½|. The test must therefore recover the per-cell
direction sign(s−½) — a Bernoulli(s) discrimination that needs ≈ 1/|s−½|² samples
*of that cell* to resolve. This is the hook the testing lower bound pulls on.

## Corollary (homogeneous cells → the coupling in miniature)

Take m independent identical cells, contention θ, signal |s−½| = ε. Cells are disjoint,
so the whole-instance ratio is the per-cell average:

- baseline strength **ρ_base = (1+θ/2)/(1+θ) = 1 − Θ(θ)** → contention θ sets the
  baseline slack;
- right-direction advice everywhere → ratio = ρ_base + **δ**, with **δ = θε/(1+θ) =
  Θ(θε)**; wrong-direction → ratio = ρ_base − **Δ**, Δ = Θ(θε);
- so **δ = Θ(ε · (1−ρ_base))**: the consistency upside is an **ε-fraction of the
  baseline slack**, and it vanishes as either contention θ→0 (strong baseline) or
  signal ε→0 (advice/truth near-symmetric) — *and ε→0 is exactly when the per-cell
  direction is hardest to test* (needs 1/ε² samples). The upside and the testability
  shrink together — the T1 coupling, already visible in one homogeneous family.

(The homogeneous family is the EASY case — pooling m identical cells estimates the
shared direction from O(1/ε²) total samples. The HARD case makes the cells
*heterogeneous*, so the advice is right on some and wrong on others and the test must
resolve Θ(m) separate directions — that is the Valiant–Valiant tolerant-testing
instance, and it is where γ_k = o(1) coexists with δ = Θ(1). W1 supplies the per-cell
gain↔L1 constants; the dimension argument is W3 / Lemma 4.)

## What W1 closes, and what remains

- **Closed (W1):** the matching-advantage ↔ L1 conversion, exactly, with the
  baseline/OPT constants. The reduction (Lemma 2) needs precisely "advantage =
  ±θ|s−½| with L1 = 2θ|s−ŝ|", which W1 delivers and numerics confirm.
- **Remaining (W3 / Lemma 4):** choose the heterogeneous bias profile {s_i} and the
  advice {ŝ_i} so that (i) the good/bad scenarios have net advantage ±Θ(1) [aggregate
  the per-cell ±θ|s_i−½|], and (ii) their length-k prefixes are TV-close, γ_k = o(1),
  for k = o(n) — this is a direct instantiation of the VV tolerant-testing hard
  instance with W1's constants. This is the next theory step.

**Verdict:** the theory "M0" closes — the single cell behaves exactly as the
construction needs, with no surprises. Proceed to assemble the heterogeneous family
(W3) on top of these constants.
