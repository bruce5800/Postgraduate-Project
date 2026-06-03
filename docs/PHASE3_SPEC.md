# Phase 3 Specification — Learning-Augmented Online Bipartite Matching

**Status:** awaiting sign-off before coding.
**Scope of first increment (agreed):** prediction generator + 4 error models +
MinPredictedDegree (which subsumes the "blind trust" extreme — see §4.3).
Choo (TestAndMatch) and Burathep adaptive-fallback frameworks are **deferred**
to a later increment; this doc nonetheless specifies them so the prediction
infrastructure is designed to accommodate them.

**Sources (read in full):**
- ACI — Aamand, Chen, Indyk, "(Optimal) Online Bipartite Matching with Degree Information", NeurIPS 2022, arXiv:2110.11439. `papers/aamand-chen-indyk-2022.pdf`
- Choo — Choo, Gouleakis, Ling, Bhattacharyya, "Online bipartite matching with imperfect advice", ICML 2024, arXiv:2405.09784. `papers/choo-2024-imperfect-advice.pdf`
- BEM — Burathep, Erlebach, Moses Jr., "Learning-Augmented Online Bipartite Matching in the Random Arrival Order Model", SOFSEM 2026, arXiv:2511.23388. `papers/burathep-erlebach-moses-2026.pdf`

---

## 1. The orientation reconciliation (critical — read first)

The three Phase 3 papers use the **opposite vertex-naming convention** from
Borodin / our Phase 2 code. Getting this wrong corrupts every prediction.

| Concept | Phase 3 papers (ACI / Choo / BEM) | Borodin / our Phase 2 code |
|---|---|---|
| **Offline** (known in advance) | U | **R** (right), indices `0..n_right-1` |
| **Online** (arrives sequentially) | V | **L** (left), iterated over `instance_adj` |
| Adjacency stored as | — | `type_adj[l]` = R-neighbors of type `l` |

**Consequence:** every Phase 3 statement about "offline vertices U" maps to our
**R-side**, and "online vertices V / their types" maps to our **L-side**.

- **MPD predicts the degrees of offline (U = our R) nodes.**
- **Choo/BEM predict the types of online (V = our L) nodes**, where a "type" =
  the subset of offline neighbors = exactly our `type_adj[l]`.

Our Phase 2 type-graph representation already encodes both: the offline degree
of R-node `r` is `|{l : r ∈ type_adj[l]}|`, and an online type is a row
`type_adj[l]`.

---

## 2. The three models (and how each maps to our harness)

The difficulty hierarchy (Choo §2): **Adversarial ≤ Random-Order ≤ Unknown-IID
≤ Known-IID**. Our Phase 2 harness is **Known-IID** — the easiest. Methods
proven for a harder model also apply to ours, so we can run all three algorithms
inside the existing i.i.d. sampler.

| Algorithm | Native model | Predicted object | Runs in our Known-IID harness? |
|---|---|---|---|
| **MinPredictedDegree** | CLV-B random graph (⊇ symmetric ⊇ ER) | scalar predicted degree per **offline (R)** node | Yes — symmetric CLV-B *is* a special case of Known-IID (ACI §2) |
| **TestAndMatch (Choo)** | Random-Order | distribution / histogram over **online (L)** types | Yes — Known-IID ≤ Random-Order, so its guarantees carry |
| **BEM** | Random-Order | count `ĉ(t)` per online type (= histogram) | Yes — same reason |

So **no new arrival model is strictly required** for correctness; we keep the
i.i.d. sampler. (We may *optionally* add a random-order sampler later to study
arrival order as an independent variable per the proposal §6.2, but it is not
needed to run these algorithms.)

---

## 3. Algorithm specs

### 3.1 MinPredictedDegree (MPD) — implement now

**Algorithm (ACI Algorithm 1):** maintain matching M. When online node `v`
(our L-node) arrives, let `N(v)` = its unmatched offline (R) neighbors. If
nonempty, match `v` to `u = argmin_{u ∈ N(v)} μ(u)`, where `μ: R → ℝ≥0` is the
degree predictor. Ties broken consistently (e.g. by R-index).

**Predictor variants (ACI §7):**

| Name | Predictor μ(r) | Role |
|---|---|---|
| **MinDegree** | true degree of `r` in the *realized instance graph* | perfect oracle → **consistency ceiling** |
| **MPD** | *expected* degree of `r` = its degree in the **type graph** = `|{l : r ∈ type_adj[l]}|` (for uniform i.i.d. with m=\|L\|) | the natural predictor we perturb |
| **(Ranking)** | a uniformly random value per `r` | **MPD with random μ ≡ Ranking** (ACI §4) → **robustness floor** |

**The key structural fact (and a free spectrum):** because MPD only uses μ to
take an `argmin`, it depends on μ **only through the order it induces on R**.
Therefore:

```
MPD(perfect order)  ≡  MinDegree   (best)
MPD(random order)   ≡  Ranking     (worst, = advice-free baseline)
MPD(perturbed order)                (interpolates between the two)
```

MPD *automatically* gives a consistency→robustness interpolation **without any
engineered fallback** — its graceful degradation is a property of the argmin,
not of a test-and-switch mechanism. (The engineered robustness is what Choo/BEM
add, §3.2–3.3.) This is exactly the consistency/robustness object the proposal's
RQ2 wants to trace, and we get it from one algorithm.

**Methodological corollary (a real finding to design around):** since only the
*order* matters, **any order-preserving (monotone) prediction error is a no-op
for MPD.** A purely systematic multiplicative/additive bias on degrees does not
change the argmin and cannot hurt MPD at all. This directly demonstrates the
proposal §5 thesis — "error *structure*, not just magnitude, determines impact"
— in its sharpest form. Our error models must therefore be designed to vary in
how much they disturb the *order*, not just the magnitude.

**Where MPD shows signal:** on graphs where offline (R) degrees are
**non-uniform**.
- **ER** (Phase 2): all R-degrees ≈ equal ⇒ MPD ≈ Ranking (degenerate, ACI
  proves ≈0.831 with no predictor help). *ER will not show MPD's advantage.*
- **Left-Regular** (Phase 2): L-degrees fixed = d, but **R-degrees vary**
  (Binomial) ⇒ MPD has signal.
- **Power-law / Zipf offline degrees** (new, ACI §7): strongest signal; ACI uses
  symmetric CLV-B with Zipf R-degrees, n=m=1000. **We need to add this
  generator** (§5).

### 3.2 TestAndMatch (Choo) — deferred, specified for interface design

**Model:** Random-Order. **Advice:** a histogram `q` over online (L) types — a
forecast of the type distribution. **Algorithm:** (i) from `q`, build a
*predicted graph* and compute a suggested matching; (ii) use a sublinear prefix
of arrivals as samples to estimate `L1(p, q)` between true and predicted type
distributions via a distribution-testing L1 estimator; (iii) if the advice
passes the test, **mimic the predicted matching**; else **revert to Ranking**
(the β-competitive advice-free baseline, β≈0.696 in random-order). Guarantees
1-consistency, β-robustness, smooth degradation in `L1(p,q)`.

**Practical caveat (Choo's own footnote):** the Jiao et al. L1 estimator needs
heavy hyperparameter tuning and has *no off-the-shelf implementation*. Our
eventual implementation will use a **practical surrogate test** (e.g. empirical
L1 on the prefix with a tunable threshold), documented as a deviation.

### 3.3 BEM (Burathep–Erlebach–Moses) — deferred, specified for interface design

**Model:** Random-Order. **Prediction:** `ĉ(t)` = predicted count of online (L)
vertices of each type `t`; equivalently distribution `q`, with `Σ ĉ(t) = n`.
The prediction induces a predicted graph `Ĝ`; `n̂` = optimal matching size in
`Ĝ`. **Generalization over Choo:** drops the assumption `n* = n`; only requires
predicted matching size `≥ αn` for a constant `α ∈ (0,1]`. **Guarantee:**
(1−o(1))-consistency, (β−o(1))-robustness, and an explicit smoothness bound:
competitive ratio `≥ 1 − 2·L1(p,q) / (2α + L1(p,q)) − o(1)`.

**Error metric for both Choo & BEM:** `L1(c*, ĉ) = Σ_t |c*(t) − ĉ(t)|`
(= `n · L1(p,q)`). This is the natural x-axis for their performance-vs-error
curves and must be what our error models report for the type-distribution
prediction object.

---

## 4. Prediction objects and the four error models

Two distinct prediction objects, perturbed by the same four error-model
*families* (proposal §5) but realized differently per object.

### 4.1 Prediction object A — offline degree vector (for MPD)
`μ ∈ ℝ≥0^{n_right}`. Ground truth = type-graph R-degrees. MPD cares only about
**induced order**.

### 4.2 Prediction object B — online type histogram (for Choo/BEM, deferred)
`ĉ: types → ℤ≥0` (or distribution `q`). Ground truth = true type counts; in
uniform i.i.d. with m=\|L\|, every realized type has count ~1. Error measured by
`L1(c*, ĉ)`.

### 4.3 "Blind trust" baseline — resolved
The proposal's "盲目信任预测" extreme is **not a separate algorithm in the degree
setting**: MPD already blindly follows its degree predictor (no fallback). So
for object A, the blind-trust extreme *is* MPD, and its two anchors are
MinDegree (perfect) and Ranking (random). A distinct "FollowPredictedMatching"
blind-trust algorithm only becomes meaningful for object B (follow `Ĝ`'s optimal
matching with no test) — that lands with the Choo/BEM increment.

### 4.4 The four error models — concrete definitions

For **object A (degree vector μ)**, with a scalar strength `η ∈ [0,1]`:

| Model | Definition on μ | Effect on MPD's *order* |
|---|---|---|
| **Random flip** | independently, w.p. `η` replace `μ(r)` with a uniform random value in `[min,max]` | partially randomizes order; η=0 → MinDegree-order, η=1 → Ranking |
| **Systematic bias** | monotone map, e.g. `μ(r) ← μ(r)·(1+η)` or `+η·scale` | **order-invariant ⇒ no effect on MPD** (the headline finding) |
| **Adversarial** | reverse the induced order on an `η`-fraction of nodes (swap high/low predicted degree) — the most order-damaging perturbation at fixed magnitude | maximal order damage per unit magnitude |
| **Distribution drift** | μ computed from a *different* type graph (e.g. a re-sampled / time-shifted graph), drift amount scaled by `η` | structured, realistic order error |

For **object B (type histogram)**, the same four families act on counts `ĉ(t)`
and are scored by `L1(c*, ĉ)` (deferred increment).

**Design requirement:** every error model returns both the perturbed prediction
**and a scalar error measure** so the x-axis of RQ2 curves is well-defined. For
MPD we report two x-axes: (i) raw magnitude `‖μ−μ*‖`, and (ii) an **order-error**
measure (e.g. `n − LIS(μ*[order_by_μ])`, the ACI Appendix-D quantity, or
Kendall-τ distance). Showing the *same* magnitude gives *different* performance
under different models — and that systematic-bias sits at zero order-error — is
the §5 methodological result.

---

## 5. New graph generator needed

To exhibit MPD signal we add one generator to `graphs/synthetic.py`:

- **`clvb_zipf_bipartite(n, exponent, C, rng)`** — symmetric CLV-B with offline
  (R) expected degrees following Zipf: `d_i = C · i^{-exponent}`, edge
  `{l, r_i}` present w.p. `d_i / m`. (ACI §7: n=m=1000, C=m/2, exponent swept
  0.2–2.0.) This is the cleanest graph for the MPD error-spectrum experiment.

Optionally later: Molloy–Reed power-law and Preferential-Attachment (proposal §6,
ACI §7 known-i.i.d. experiments). Not needed for the first increment.

---

## 6. Baselines and the algorithm roster for the MPD increment

| Algorithm | Status | Role |
|---|---|---|
| Ranking | ✅ Phase 2 | robustness floor (≡ MPD with random μ) |
| SimpleGreedy | ✅ Phase 2 | greedy reference |
| **MinDegree** | new | perfect-oracle ceiling (MPD with true realized degree) |
| **MPD** | new | the algorithm under study (MPD with type-graph degree) |
| **MPD(error-model, η)** | new | the consistency→robustness spectrum |
| FeldmanEtAl(MPD), JailletLu(MPD) | optional | ACI §7 "(MPD)-augmented" variants — break ties / fill skips using predicted degrees instead of arbitrary; a natural bridge to our Phase 2 algorithms |

The `(MPD)`-augmentation (ACI §7) is the analogue of our Phase 2 `(g)`
augmentation: where a non-greedy known-i.i.d. algorithm would skip, apply the
MPD min-predicted-degree rule. Cheap to add given Phase 2 code; strong extension
story.

---

## 7. Evaluation

- **Primary metric:** empirical competitive ratio = `|ALG| / |OPT|`, OPT via
  existing Hopcroft–Karp. Unchanged from Phase 2.
- **RQ2 main curves:** competitive ratio vs prediction-error strength `η`, one
  curve per error model, per graph family — anchored at MinDegree (η=0) and
  Ranking (η=1).
- **Consistency/robustness read-off:** consistency = ratio at η=0; robustness =
  ratio at η=1; the curve in between is the empirical smoothness profile (the
  thing theory only bounds).
- **Methodological figure:** ratio vs *magnitude* error, overlaying all four
  models, to show same magnitude → different impact (systematic-bias flat).

---

## 8. Module plan (foundation-first increment)

```
predictions/
├── __init__.py
├── degree_truth.py      # type-graph R-degree (MPD predictor); realized-instance R-degree (MinDegree oracle)
└── error_models.py      # random_flip, systematic_bias, adversarial, distribution_drift
                          #   each: (mu*, eta, rng) -> (mu_perturbed, error_scalars)
algorithms/
└── min_predicted_degree.py   # mpd(instance_adj, types, n_right, mu) ; reuses greedy_with_permutation
graphs/
└── synthetic.py         # + clvb_zipf_bipartite(...)
tests/
└── test_mpd_small.py    # MPD≡Ranking when mu uniform; MPD≡MinDegree when mu=truth;
                          #   systematic-bias invariance; argmin tie-break determinism
scripts/
└── run_mpd_error_spectrum.py   # ratio vs eta, 4 models, on clvb_zipf + left_regular
```

**Reuses unchanged from Phase 2:** `optimal.py`, `iid_sampler.py`, the ER &
Left-Regular generators, `algorithms/_common.greedy_with_permutation` (MPD is
literally `greedy_with_permutation` with `rank = argsort(μ)`), the runner +
4-stream RNG pattern (one extra stream for prediction perturbation).

**Implementation note:** MPD = `greedy_with_permutation(instance_adj, rank)`
where `rank = rank-of-μ`. This means MPD costs *zero* new online-stage code — it
is the Phase 2 primitive with a degree-derived permutation instead of identity
(SimpleGreedy) or random (Ranking). The three algorithms are one primitive with
three rank sources. This unifies the whole Phase-2+3 greedy family.

---

## 9. Open questions for sign-off

1. **Graph for the headline MPD experiment:** CLV-B/Zipf (ACI's own, strongest
   signal) — agreed as the new generator? Or prioritize Left-Regular (already
   built, weaker but zero new code)? Plan: build CLV-B/Zipf, run both.
2. **Error-model strength axis:** report against *order-error* (Kendall-τ /
   ACI's `n−LIS`) in addition to raw magnitude, to make the systematic-bias
   invariance legible? (Recommended.)
3. **`(MPD)`-augmented Feldman/JailletLu:** include in first increment as the
   bridge to Phase 2, or defer with Choo/BEM? (Lightweight; lean include.)
4. **Proposal citation fix:** correct [3] title to "Online bipartite matching
   with imperfect advice" in the v2 docx now, or batch with the Phase 3 proposal
   update later?
```
