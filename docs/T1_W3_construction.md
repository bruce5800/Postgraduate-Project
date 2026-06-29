# W3 / Lemma 4 — the heterogeneous construction (attacked; reduced to a citation + one lemma)

**Status:** attacked, and **substantially closed** — W3 reduces to (i) the standard
**tolerant identity-testing** lower bound (Valiant–Valiant / Jiao–Han–Weissman, cited)
applied with q = the advice, plus (ii) one **conversion-monotonicity lemma** (numerically
validated below). Two honest findings came out of the attack: a low-dimensional version
is *too weak* (dimension is essential), and the reduction to testing is *cleaner than
the skeleton feared* because the prefix is literally i.i.d. samples from the type
distribution.

## Honest finding 1 — the dimension is essential (a low-dim attempt fails)

First I tried a **low-dimensional** two-scenario construction: all cells share one bias
parameter, and G/Bd differ by a single global bias ±ρ toward agreeing with the advice.
Computing it out: the upside is δ = Θ(ρθ), and the prefix can estimate the single bias ρ
to ±1/√(θk), so G and Bd are distinguishable once θk ≳ 1/ρ². Hence the *only* uncapturable
upsides are δ = O(√(θ/k)) — vanishing at sublinear k. **A single global bias is too easy
to estimate; this gives only a weak impossibility (ρ_base = 1−o(1)).** The strength must
come from **dimension**: spreading the advice error over r = Θ(n) independent cells, so
that estimating the aggregate L1 requires seeing the "unseen" mass — the regime where the
Valiant–Valiant Ω̃(r) barrier bites. This is exactly the numerical regime (r ≈ n,
count/type ≈ 1) where `run_impossibility_frontier.py` showed the collapse.

## The construction (high-dimensional)

m = Θ(n) independent rare-resource cells (W1), each a *distinct* type-pair (α_i, β_i), so
the support is r = Θ(n) specialist-types, each seen O(1) times in n arrivals. Cell i has
contention θ = Θ(1) and bias s_i with |s_i − ½| = Θ(1); the advice fixes a predicted
direction ŝ_i per cell (a histogram q over the r types). Following = Mimic = route each
flexible request to protect its cell's predicted-majority specialist.

By W1, **per cell** the advantage of following over the baseline is ±θ|s_i−½| (sign = is
the advice's direction correct?), and the per-cell L1 contribution is 2θ|s_i−ŝ_i|. The
cells are disjoint, so these **aggregate**:
- whole-instance ratio of following = ρ_base + (1/Z)·Σ_i (±θ|s_i−½|),
- L1(p, q) = (1/Z)·Σ_i 2θ|s_i−ŝ_i|,   Z = m(1+θ) = Θ(n).

> **Lemma W3a (conversion monotonicity; ✓ numerically validated).** As the fraction φ of
> cells whose advice direction is *wrong* increases from 0 to 1, the follow-ratio
> decreases monotonically through the baseline, crossing it at φ = ½, while L1(p,q)
> increases monotonically. Concretely (m=4000, θ=0.6, |s−½|=0.3): ρ_base = 0.812;
> φ=0.2 → L1 0.093, follow 0.878 (**gain +0.066**); φ=0.8 → L1 0.360, follow 0.745
> (**loss −0.067**); crossing at φ=½, L1*=0.223. So there exist constants a < b with
> b − a = Θ(1) such that L1(p,q) ≤ a ⟹ following gains δ = Θ(1) over baseline, and
> L1(p,q) ≥ b ⟹ following loses Δ = Θ(1).

*(a ≈ 0.09, b ≈ 0.36, δ ≈ Δ ≈ 0.066, b−a ≈ 0.27 in the validated example — all Θ(1).)*

## The reduction (cleaner than feared)

The prefix X_{1:k} is **literally k i.i.d. samples from the type distribution p** (known-
i.i.d. model). The advice fixes q. By Lemma 2 (algorithm ⟹ tester) + Lemma W3a, any A_k
that is (1−o(1))-consistent and (ρ_base−o(1))-robust must, from k samples of p, decide
whether L1(p, q) ≤ a or ≥ b — i.e. it solves **tolerant identity testing to the known
distribution q with gap [a,b]**.

> **Lemma 3 (tolerant identity testing — CITE).** Distinguishing ‖p−q‖₁ ≤ a from ≥ b for
> a known q over support [r], error ≤ ⅓, requires
>   **k = Ω( r / ((b−a)² · log r) )** samples
> (Valiant–Valiant 2011/2017, "estimating the unseen"; Jiao–Han–Weissman 2018 for the L1
> constants). The log r improvement is exactly the surprising part; the lower bound
> matches it.

With r = Θ(n) and b−a = Θ(1) (Lemma W3a): **k = Ω̃(n)**. Therefore any A_k with
k = o(n/log n) has γ_k = o(1) on the constructed (p_G, p_Bd) pair, and Lemma 1's master
inequality (1−η_c) ≤ η_r + γ_k forces η_c + η_r ≥ 1 − o(1): it cannot be both
near-consistent and near-robust. ∎ (sketch)

## Theorem T1 (assembled, honest form)

> For every test budget k = o(n/log n), there is a known-i.i.d. matching family with
> r = Θ(n) types, baseline strength ρ_base = 1 − Θ(1), on which no test-and-fallback
> algorithm A_k (any rule, not just empirical-L1 thresholding) is simultaneously
> (1−o(1))-consistent and (ρ_base − o(1))-robust. The achievable (consistency,
> robustness) region collapses to (ρ_base, ρ_base).

Combined with the strong-baseline side (small r ⟹ ρ_base→1 ⟹ upside δ→0, nothing to
capture), this is the full **scissors** of `results/impossibility_frontier.png`, now with
a proof route: *the upside lives only in the high-dimensional (r=Θ(n)) regime, and there
the tolerant-testing barrier makes it uncapturable at sublinear k.*

## Honest status — what closed, what remains

| Piece | Status |
|---|---|
| Low-dim attempt | **Ruled out** (too weak) — dimension is essential. A genuine finding. |
| Multi-cell aggregate conversion (Lemma W3a) | **Numerically validated** (monotone, crossing at φ=½, constants Θ(1)). Needs a clean analytic monotonicity proof (routine: each cell's contribution is independent and monotone). |
| Reduction prefix ⟹ i.i.d. samples ⟹ tolerant testing | **Clean** — the prefix *is* k i.i.d. samples; q is the fixed advice; tolerant *identity* testing applies directly. This is the step that makes it "any rule" and matches the prior-art's "unbuilt bridge". |
| Lemma 3 (testing lower bound) | **Cite** VV / JHW. **Confirm** the exact tolerant-identity statement (constants, log factors) gives Ω̃(r) at constant gap. |
| Assembling via Lemma 1 | Clean given the above (γ_k = o(1) from VV; o(1) bookkeeping). |

**Remaining real work (now small and well-defined):**
1. The analytic version of Lemma W3a (monotonicity of follow-ratio in φ / in L1) — each
   cell contributes independently, so this is a sum-of-independent-monotone-terms argument.
2. Confirm the exact **tolerant identity-testing** lower-bound statement and that it yields
   Ω̃(n) at r=Θ(n), constant gap (read VV 2017 / JHW carefully — the skeleton's biggest
   remaining citation risk W2).
3. Match the (p_G, p_Bd) pair from the VV lower-bound construction to cell directions so
   that L1(p_G,q) ≤ a and L1(p_Bd,q) ≥ b hold with the Θ(1) gap — the VV hard instance is a
   specific perturbation of q; verify it lands in the right φ-ranges of Lemma W3a.

**Verdict:** W3 is **not a dead end** — attacking it converted "invent a hard instance"
into "apply the standard tolerant-testing lower bound through a validated conversion." The
two genuine remaining tasks (analytic Lemma W3a + the exact VV statement + the instance
match) are the kind of thing a careful read + an advisor session closes. The honest scope:
T1 holds for r=Θ(n) strong-form; the all-regime scissors is T1 (this) + the trivial
strong-baseline side + the numerical frontier as the unifying picture.
