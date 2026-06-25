# Research Plan A — Learning to *Rank* for Online Matching with Predictions

**Thesis (one sentence).** For MinPredictedDegree-type online matching, the
prediction problem is fundamentally a **learning-to-rank** problem, not a
regression problem: because the algorithm consumes the predictor only through the
induced *order*, training the predictor with an order-aware loss (a) provably
upper-bounds the matching regret via the Kendall-τ bound, and (b) empirically
dominates the standard regression-trained ("predict-then-optimize") predictor at
equal model capacity and far below the cost of end-to-end decision-focused
training — across synthetic and real workloads.

**Why this is the elevation.** The existing study (★1–★4) *confirms and
characterises* existing algorithms — an experimental contribution (ALENEX/JEA
ceiling). This plan adds a genuinely **new method** (a decision-aligned way to
*learn* the predictor) with a **theorem** justifying it, targeting an ML venue
(NeurIPS/ICML/AISTATS). The whole existing study becomes its empirical backbone and
motivation; ★1 becomes the linchpin of the theory.

**Novelty check (what makes it publishable).** Learning-to-rank is a large field but
has never been applied to *online-matching predictions*; decision-focused learning
(SPO+, perturbed optimizers) has been applied to shortest-path/ranking but **not to
online bipartite matching with predictions**; and algorithms-with-predictions work
almost always *assumes* the predictor is given rather than *learning it with a
decision-aligned objective*. The intersection is open.

---

## 1. Problem formulation

- Offline nodes r ∈ [N], each with a **feature vector** x_r ∈ R^d (what a real
  system actually has: historical counts over past windows, day-of-week, trend,
  co-occurrence stats, etc.).
- **Predictor** f_θ : R^d → R, score s_r = f_θ(x_r). MPD matches the *lowest-score*
  (rarest) available offline node first, so only the **order** of s matters.
- **True target order** is the one induced by the true/expected degree μ*_r.
- **Matching ratio** R(π) = E[ MPD-with-order-π ] / OPT, the downstream objective.

The learner sees a training set of instances (or past windows) with features and
realised outcomes; it must output θ that makes f_θ's order yield high R on unseen
instances.

## 2. The loss zoo (the core experimental axis)

| Loss | Definition | Differentiable? | Cost | Role |
|---|---|---|---|---|
| **Regression** (status quo) | L_reg = (1/N)Σ_r (s_r − μ*_r)² | yes | cheap | the predict-then-optimize **baseline to beat** |
| **Pairwise rank** (proposed) | L_rank = mean over pairs (i,j), μ*_i<μ*_j, of log(1+e^{-(s_j−s_i)/T}) | yes (closed-form grad for linear f) | cheap | the **proposed surrogate** — RankNet/logistic |
| **Listwise** (proposed, alt) | ListMLE / Plackett–Luce NLL of the true order under softmax(s) | yes | cheap | a stronger order surrogate |
| **Soft-rank / soft-τ** | differentiable sort (Blondel et al. fast soft-sort) → smooth Kendall-τ to μ* | yes | medium | directly optimises the τ the theory bounds |
| **Decision-focused** (gold std) | L_dec = R(π(μ*)) − R(π(s)); smoothed via perturbed optimizer (Berthet 2020) | via smoothing | **expensive** | the **upper-quality reference** rank-loss should approach |

**Punchline to establish:** L_rank (cheap, off-the-shelf) ≈ L_dec (expensive,
bespoke) ≫ L_reg (status quo) on matching ratio — because the structure (order-only
dependence) makes the rank loss decision-aligned *for free*.

## 3. Theory (Direction B as the backbone)

We need only a **one-sided** bound (far easier than a tight two-sided one):

> **(B) Order-regret bound.** On the CLV-B / Zipf graph class (ACI's own setting),
> the MPD matching loss of an order π versus the true order is ≤ C · τ(π, π*), where
> τ is the (unnormalised) Kendall-τ distance and C depends on the degree
> distribution.

Given (B), the **surrogate chain** is mostly textbook:

```
 L_dec(θ)  =  R(π*) − R(π_s)
           ≤  C · τ(π_s, π*)                         ... (B) — the one new lemma
           =  C · (# discordant pairs of s vs μ*)     ... Kendall-τ IS pairwise disagreement
           ≤  C' · L_rank(θ)                          ... logistic upper-bounds the 0/1 pairwise loss (standard)
```

⇒ **minimising the convex pairwise rank loss minimises an upper bound on the
matching regret.** That is the theoretical justification for "train to rank."

- The middle identity (τ = pairwise disagreement) and the surrogate calibration
  (logistic ≥ 0/1) are standard learning-to-rank results — cite, don't re-prove.
- Only (B) is new, and ★1 already shows it holds *empirically* (loss collapses onto
  τ, the n−LIS bound is loose). The job is to prove the one-sided version on CLV-B,
  where MPD is analysable. Even a bound with a loose constant C suffices — we are
  justifying a surrogate, not computing a rate.
- **Fallback if (B) resists a full proof:** prove it for a tractable sub-case
  (e.g. two-value degree distributions, or the well-separated-degrees regime), and
  present the general case as an empirically-validated conjecture (★1 is the
  evidence). The method contribution stands on the experiments regardless.

## 4. Experimental design

### 4.1 The central dissociation (the money figure)
Construct features where **magnitude accuracy and order accuracy diverge** (e.g.
x_r = monotone-but-nonlinear transform of μ*_r + multi-source noise; or two features
whose linear combo predicts order well but magnitude poorly). Then:
- L_reg achieves **low MSE but poor matching ratio**;
- L_rank achieves **higher MSE but high matching ratio**.

Plot (MSE, ratio) and (τ, ratio) scatter for both objectives → rank-training
**dominates on the decision metric despite worse regression error**. This is the
visual that says "regression is the wrong objective."

### 4.2 When does rank-training matter? (characterisation = a contribution)
Sweep the **order–magnitude divergence** of the features (from co-linear → strongly
divergent) and the **graph hardness** (Zipf exponent; floor-to-OPT gap from ★2).
Hypothesis: rank-training's advantage grows with divergence and with hardness, and
**vanishes on easy instances** (F3 — no gap to win). Honestly mapping this regime is
itself a finding, and it tells practitioners *when* to bother.

### 4.3 Rank vs decision-focused (the cost-quality Pareto)
Add the perturbed-optimizer decision-focused predictor. Show L_rank reaches
≈ its matching ratio at a fraction of the training cost (no differentiation through
the matching, no per-step OPT). Pareto frontier: ratio vs training cost.

### 4.4 Real workloads (external validity — reuse ★3 infrastructure)
Wikipedia / Azure-LLM / Mooncake traces. Features = per-node statistics over past
windows; target order = next window. Compare: learned-rank vs learned-MSE vs the
fixed historical-count predictor (★3) vs oracle vs Ranking floor. Claim: the learned
rank predictor beats both the MSE-trained one and the non-learned historical count,
at the same (negligible) inference cost.

### 4.5 Generality across algorithms
Repeat the headline on the **(MPD)-augmentations** (Feldman/JailletLu(MPD)) and on
**Choo/BEM** (where the "order" object is the type histogram) — does train-to-rank
help wherever an algorithm consumes a *ranked/sorted* prediction? Ties back to the
unified benchmark.

### Figures
| # | Content |
|---|---|
| A | the dissociation: (MSE↔ratio) and (τ↔ratio), rank vs MSE training |
| B | rank-advantage vs feature divergence × graph hardness (heatmap) |
| C | cost–quality Pareto: rank vs decision-focused vs MSE |
| D | real traces: learned-rank vs learned-MSE vs historical-count vs oracle |
| E | theory: empirical L_dec vs the C·τ surrogate-chain bound |

## 5. Milestones (de-risk fastest first)

- **M0 — MVE (days, pure numpy/scipy).** Linear f_θ; L_reg vs L_rank (pairwise
  logistic, closed-form gradient via `scipy.optimize`); synthetic divergent features
  on a Zipf type graph; reuse `graphs/`, `optimal.py`, `mpd`. **Success = rank-trained
  ratio > MSE-trained ratio with rank-trained MSE *worse*.** Kills/confirms the whole
  direction in one plot. *(No torch needed.)*
- **M1.** Regime sweep §4.2 (divergence × hardness) — characterise where it matters.
- **M2.** Decision-focused baseline (perturbed optimizer) — introduce torch/jax for
  the MLP + smoothing; cost–quality Pareto §4.3.
- **M3.** Real traces §4.4 (temporal features) — external validity.
- **M4.** Theory (B): prove the one-sided CLV-B bound; assemble the surrogate chain.
- **M5.** Generality §4.5 + write-up.

## 6. Risks & mitigations

| Risk | Mitigation |
|---|---|
| On easy instances there's no gap (F3) | Target the hard/structured regime (Zipf, social/bio real graphs, floor 0.88–0.91) — ★2 already mapped where the gap lives |
| Rank ≈ MSE when features make order & magnitude co-linear | That's the *characterisation* (4.2): show rank wins *iff* features induce order–magnitude divergence; multi-source noisy features are the realistic divergent case |
| (B) hard to prove generally | One-sided bound, CLV-B only, loose constant; ★1 is the empirical backstop; fall back to a tractable sub-case + conjecture |
| Decision-focused training unstable/expensive | It is only a *reference*; the thesis is precisely that you don't need it — rank loss suffices |
| "Just learning-to-rank applied to X" dismissal | The novelty is the *decision-alignment theorem* (B-chain) specific to matching, the *when-it-matters* characterisation, and the real-workload result — not the LTR machinery itself |

## 7. Positioning / relation to the existing study

- §1–§2 of the paper = the existing unified benchmark + order-error finding, now
  reframed as **motivation**: "predictions are robustness insurance, and *order* is
  what matters — so how should we *learn* the predictor?"
- The method (this plan) is the new core (§3–§5 of the new paper).
- Target: NeurIPS/ICML/AISTATS (method + theory + experiments). The ALENEX/JEA
  benchmark paper can still be split out as a companion/short version if desired.

## 8. Immediate next action

Run **M0** — the minimal viable experiment — to test the central hypothesis
(*rank-training beats MSE-training on matching ratio despite worse MSE*) in the
existing numpy/scipy stack. If M0 is positive, the direction is real and worth the
M1–M5 build-out; if not, we learn that cheaply and pivot. Script:
`scripts/run_rank_vs_mse_mve.py` (to be written): Zipf type graph, divergent
synthetic features, linear predictor, two losses, compare matching ratio + MSE + τ.
