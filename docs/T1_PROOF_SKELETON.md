# T1 — Proof Skeleton (no-free-lunch for sublinear test-and-fallback)

**Status:** skeleton. Lemma 1 (the master tradeoff) is self-contained and rigorous.
Lemmas 2–4 reduce T1 to a *tolerant distribution-testing* lower bound (Valiant–
Valiant / Jiao–Han–Weissman) — the strategy is sound and addresses the prior-art
differentiation risk (it is information-theoretic, holding for ANY function of the
prefix, not just Choo's specific threshold), but the construction constants and the
reduction details are the **real work**, flagged W1–W4. Everything here is the
empirical statement validated in `run_impossibility_frontier.py`, lifted to a proof.

The differentiation target (from the prior-art pass): Choo et al. already put the
baseline ratio β into their *acceptance threshold* τ = 2(n̂/n − β) − ε
*constructively*. T1 must therefore be a **two-sided, information-theoretic
impossibility**: no o(n)-prefix algorithm — by any rule, not just thresholding the
empirical L1 — can capture the consistency upside while staying robust on
strong-baseline instances. The reduction to a *sample-complexity* lower bound
(Lemma 3) is exactly what makes it "any rule".

---

## 1. Model and definitions

- **Instances.** Known-i.i.d. online bipartite matching: a type graph H over r online
  types and offline resources; n arrivals drawn i.i.d. from a type distribution p
  over [r]. OPT(I) = max matching of the realised instance I.
- **Advice** σ: a type-histogram q ∈ Δ([r]) (Choo/BEM object). "Following" σ = Mimic:
  build a max matching on the advice graph and route each arrival accordingly.
- **Baseline** B: advice-free (Ranking). E[B]/OPT = ρ_base on the family.
- **Test-and-fallback class A_k.** Observe the prefix X_{1:k} (first k arrivals) and σ;
  output a (possibly randomised) decision D ∈ {F, R}; then on arrivals k+1..n play
  Mimic(σ) if D=F, else B. (More generally D may be any measurable, possibly
  randomised function of (X_{1:k}, σ); the bound covers all such.)
- **Consistency / robustness.** For an instance distribution 𝒟 with advice σ, write
  R(𝒟) = E[ALG]/E[OPT]. Consistency = R under *good* advice; robustness = R under
  *bad* advice.

**Sublinearity assumption (A0).** k = o(n). Consequence: the prefix's own
contribution to the matching is ≤ k = o(n), so it shifts the ratio by O(k/n) = o(1);
we absorb this into the o(1) terms throughout.

---

## 2. Lemma 1 — the master tradeoff inequality (RIGOROUS)

> **Lemma 1.** Let G, Bd be two instance distributions sharing the *same* advice σ,
> with prefix laws ℒ_G, ℒ_Bd on X_{1:k}, and let γ_k := TV(ℒ_G, ℒ_Bd). Suppose
> following σ gains δ under G and loses Δ under Bd relative to the baseline:
>   E_G[Mimic]/OPT ≥ ρ_base + δ,   E_Bd[Mimic]/OPT ≤ ρ_base − Δ,
> while B gives ρ_base ± o(1) under both. Parameterise an A_k by η_c := the *fraction
> of the upside it forgoes* under G (captured upside = (1−η_c)·δ) and η_r := its
> *robustness loss as a fraction of Δ* under Bd (loss = η_r·Δ). Then
>
>   **(1 − η_c) ≤ η_r + γ_k + o(1).**     (★)

*Proof.* Conditioning on the decision D under G:
E_G[ALG]/OPT = P_G(F)·(E_G[Mimic]/OPT) + P_G(R)·ρ_base ± o(1) ≥ ρ_base + δ·P_G(F) − o(1).
The captured upside (E_G[ALG]/OPT − ρ_base) = (1−η_c)δ, so **P_G(F) ≥ 1 − η_c − o(1)**.
Symmetrically under Bd, E_Bd[ALG]/OPT = ρ_base − Δ·P_Bd(F) ± o(1), so the robustness
loss η_r·Δ = Δ·P_Bd(F) ± o(1), giving **P_Bd(F) = η_r + o(1)**. Finally D is a function
of (X_{1:k}, σ) and σ is identical across G, Bd, so by the coupling characterisation of
total variation |P_G(F) − P_Bd(F)| ≤ TV(ℒ_G, ℒ_Bd) = γ_k. Chaining:
1 − η_c − o(1) ≤ P_G(F) ≤ P_Bd(F) + γ_k = η_r + γ_k + o(1) ⟹ (★). ∎

*(Clean restatement of (★): you cannot simultaneously have near-full consistency
(η_c→0) and small robustness loss (η_r→0) unless the prefix is distinguishable
(γ_k = Ω(1)). The whole game is now: on strong-baseline instances, is γ_k small while
δ,Δ stay meaningful? Lemmas 2–4 say yes — and that this is forced.)*

**Note (why two-point is not enough by itself).** A single pair G,Bd has
δ,Δ ≤ O(TV(ℒ_G,ℒ_Bd)) ≤ O(γ_k) when the per-arrival laws differ by their TV — so a
bare two-point bound caps δ,Δ at γ_k and gives only δ ≲ γ_k. To get δ,Δ = Θ(1−ρ_base)
with γ_k = o(1) we need the difference **spread across Θ(r) types**, each perturbed
below the per-type sampling resolution — i.e. the *tolerant-testing* construction, not
a single two-point. Hence Lemmas 2–4.

---

## 3. Reduction to tolerant L1 testing (the route to "any rule")

> **Lemma 2 (algorithm ⟹ tester).** Fix the advice q. Suppose a family of instances
> realises: following q gains ≥ δ over the baseline whenever L1(p, q) ≤ a, and loses
> ≥ Δ whenever L1(p, q) ≥ b (a < b). Then any A_k that is (1−η_c)-consistent and
> η_r-robust on this family yields, from its k prefix samples X_{1:k} ~ p, a test that
> distinguishes {L1(p,q) ≤ a} from {L1(p,q) ≥ b} with error ≤ η_c + η_r/Δ·Δ + o(1).

*Proof sketch.* Consistency forces D=F w.h.p. when L1 ≤ a (else it forgoes the gain);
robustness forces D=R w.h.p. when L1 ≥ b (else it eats the loss). So D itself is the
tester. ∎  *(This is the step that makes the bound information-theoretic: D is an
arbitrary function of the k samples, so the lower bound below applies to ANY rule, not
just empirical-L1 thresholding — pre-empting the "isn't this just Choo's threshold?"
objection.)*

> **Lemma 3 (tolerant identity-testing lower bound — CITE).** Distinguishing
> L1(p, q) ≤ a from L1(p, q) ≥ b for a known q over support [r], with error ≤ 1/3,
> requires
>   k = Ω( r / ((b − a)² · log r) )  samples
> (Valiant–Valiant 2011/2017; Jiao–Han–Weissman 2018 for the L1/closeness constants).

This is the established engine Choo/BEM *use* for their upper bound; we invoke its
**lower** side. (W2: confirm the exact tolerant-testing statement and constants apply
to identity-to-known-q with the [a,b] gap as stated.)

---

## 4. The coupling (the crux — ties a, b, r to ρ_base)

> **Lemma 4 (baseline strength ⟹ small gap, large support).** On the rare-resource
> few-types family (below), as ρ_base → 1:
>   (i) the break-even advice error a = a(ρ_base) → 0 and the gap b − a = Θ(1 − ρ_base);
>   (ii) achieving baseline strength ρ_base needs support r = Θ̃(1/(1 − ρ_base)) within
>        each independent block, and Θ(n·(1−ρ_base)) contested blocks, so the effective
>        testing support is r_eff = Θ(n) in the regime where 1−ρ_base = Θ(1).

**The construction (rare-resource cells).** n/2 independent cells. Cell j has resources
{a_j, b_j} and online types: a *flexible* type (nbhd {a_j,b_j}) that always arrives,
and — with probability θ — one *specialist* (nbhd {a_j} or {b_j}). The optimal action
for the flexible arrival depends on which specialist will come (a future event);
Ranking guesses ⟹ ρ_base = 1 − Θ(θ); good advice (right guess everywhere) gains
δ = Θ(θ); bad advice (wrong guess) loses Δ = Θ(θ). **To make the advice error
*undetectable* at budget k, spread the wrong-guess cells across Θ(r) cell-types each
perturbed by O(1/r)** (the Valiant–Valiant hard instance), so no individual cell-type
is sampled enough in a length-k prefix to reveal whether its advice is right — this is
what forces r_eff = Θ(n) and γ_k = o(1) simultaneously with δ,Δ = Θ(θ).

*(W1: prove the L1↔Mimic-ratio relation — that following q gains/loses Θ(δ) exactly in
the L1 ≤ a / ≥ b regimes — for this construction. W3: prove the r ↔ ρ_base scaling in
(ii). These two are the genuine construction work.)*

---

## 5. Assembling T1

Combine Lemmas 2–4: a (1−o(1))-consistent, (ρ_base − o(δ))-robust A_k would solve the
tolerant test, hence needs
  **k = Ω( r_eff / ((b−a)² log r_eff) ) = Ω̃( n / (1−ρ_base)² )**   samples.
- If 1−ρ_base = Θ(1) (a meaningfully weak baseline — the only regime with an upside to
  capture), this is Ω̃(n) = ω(n^α) for every α<1: **no sublinear test suffices.**
- If 1−ρ_base = o(1) (strong baseline), the upside δ = Θ(1−ρ_base) = o(1) is itself
  vanishing — there is essentially nothing to capture, and the required k only grows.

> **Theorem T1 (target form).** For every sublinear budget k = o(n) and every ε>0,
> there is a known-i.i.d. matching family with baseline strength ρ_base on which no
> test-and-fallback algorithm A_k is simultaneously (1−ε)-consistent and
> (ρ_base − ε·(1−ρ_base))-robust. Equivalently: the achievable (consistency,
> robustness) region collapses to the single point (ρ_base, ρ_base) as the family is
> driven toward the strong-baseline / high-support regime — *wherever the prefix test
> is feasible (Lemma 3 satisfiable at sublinear k), the baseline is already
> near-optimal (Lemma 4), so there is no upside to test for.*

This is exactly the **scissors** of `results/impossibility_frontier.png`: potential
upside (green) > 0 only where the test resolution (red noise floor) ≫ the margin
(green L1*).

---

## 6. Honest status — what is solid vs the real work

| Piece | Status |
|---|---|
| **Lemma 1** (master tradeoff (★)) | **Rigorous, self-contained.** The clean two-sided core. |
| **Lemma 2** (algorithm ⟹ tester) | Sketch solid; routine to finish. This is the "any rule" step that beats the Choo-threshold objection. |
| **Lemma 3** (tolerant-testing lower bound) | **Cite** VV / Jiao–Han–Weissman. **W2:** confirm the exact statement (identity-to-known-q, [a,b] gap, constants/log factors) transfers. |
| **W1** (L1 ↔ Mimic-ratio on the construction) | **DONE** (`docs/T1_W1_single_cell.md`, closed-form + verified numerically): per cell, advantage = ±θ\|s−½\|, L1 = 2θ\|s−ŝ\|, ρ_base = 1−Θ(θ), δ = Θ(ε·(1−ρ_base)). The upside↔testability coupling already appears in the homogeneous corollary. |
| **W3** (heterogeneous construction, Lemma 4) | **Substantially closed** (`docs/T1_W3_construction.md`): reduced to the standard tolerant-identity-testing lower bound (q = advice, r=Θ(n), constant gap ⟹ Ω̃(n)) via a numerically-validated conversion (Lemma W3a, monotone crossing at φ=½). Found the low-dim version too weak (dimension essential). Remaining: analytic Lemma W3a + exact VV statement + instance match. |
| **W4** (decision uses full prefix, not just histogram) | **Handled in principle** by Lemma 3 being information-theoretic (any function of k samples). Verify no side-information (e.g. the realised partial matching) leaks more than the samples — it doesn't, since it's a function of X_{1:k}. |

**Biggest mathematical risk:** W1 + W3 — pinning the construction so that (a) the
advice-quality↔ratio relation is clean and (b) the support genuinely must scale with
baseline strength. If the general construction resists, the **fallback contribution**
is T1 on the explicit rare-resource family for a *fixed* (ρ_base, k) pair (Lemma 1 +
an explicit γ_k bound via the per-cell coupling), plus the numerical frontier as the
general evidence — still a publishable impossibility, just less general.

**Next concrete step:** prove **W1** on a single cell (the L1↔ratio relation), which is
small and hand-checkable, then chain over independent cells (tensorisation of TV for
γ_k). That is the analogue of "M0" for the theory — the smallest piece that, if it
closes, says the whole construction will.
