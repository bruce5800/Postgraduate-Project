/-
Copyright (c) 2026 Zhuolun Li. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Zhuolun Li
-/
import Budgetstakes.Hellinger

/-!
# Stage 7: second moments, Chebyshev, and the random-order arrival model (T5)

Two things happen here, both with the same elementary engine — the variance.

**(a) The `σ²`-sharp achievability at Chebyshev grade, i.i.d. model.**
Stage 4's Chernoff bound `exp(−kμ²/4)` has variance proxy `1`. Here the exact
second-moment computation `Var(∑ c(xᵢ)) = k·Var(c)` under the product law gives
`P^k(∑ c ≤ 0) ≤ Var(c)/(k μ²) ≤ E[c²]/(k μ²)`; for the cell score `c ∈ {−1,0,1}`
one has `E[c²] = σ²` (the specialist mass), so the **budget–stakes scaling
`k ≍ σ²/g²` is attained with constant 1** — the price is a `1/δ` instead of a
`log(1/δ)` failure-probability dependence (Bernstein, Stage 6, is the polish).

**(b) The random-order arrival model.**
A fixed population `M : Fin n → Ω` is presented in a uniformly random order and
the algorithm sees the first `k` arrivals — a sample *without* replacement.

* Lower bound (impossibility) transfers for free: the random-order prefix of an
  i.i.d.-drawn population is itself i.i.d. (`iid_expect_comp_perm`,
  `shuffled_iid_expect`), so a Yao-style randomized adversary reproduces exactly
  the product laws of Stage 5, and `Scenario.master_tradeoff_iid` applies
  verbatim. (Paper-level caveat: instance-dependent stakes contribute an `o(1)`
  through concentration of the empirical profile — the same `o(1)` the paper
  already carries.)
* Upper bound (achievability): exchangeability of the uniform permutation law
  gives the exact first and second moments of the prefix sum without any
  counting argument — only the *transitivity* of `Perm (Fin n)` on points and on
  ordered pairs (`uniformPerm_expect_apply`, `uniformPerm_expect_pair`). The
  finite-population variance is at most `k · E_pop[c²]`
  (`roSum_variance_le`), and Chebyshev gives `Pr(∑ ≤ 0) ≤ E_pop[c²]/(k μ²)`
  (`ro_prob_sum_nonpos_le`): **the same budget–stakes scaling under random
  order.** Exponential tails (Hoeffding's convex-order theorem / Serfling) are
  classical and deliberately left out of the formal development.
-/

namespace BudgetStakes

open scoped Classical

/-- Products of per-coordinate observables factorize over the function space:
`∑ x : Fin k → Ω, ∏ i, g i (x i) = ∏ i, ∑ ω, g i ω`. Generalizes
`sum_prod_eq_pow` to coordinate-dependent factors. -/
lemma sum_prod_eq_prod_sum {Ω : Type*} [Fintype Ω] (k : ℕ) (g : Fin k → Ω → ℝ) :
    (∑ x : Fin k → Ω, ∏ i, g i (x i)) = ∏ i, ∑ ω, g i ω := by
  calc (∑ x : Fin k → Ω, ∏ i, g i (x i))
      = ∑ x ∈ Fintype.piFinset (fun _ : Fin k => (Finset.univ : Finset Ω)),
          ∏ i, g i (x i) := by rw [Fintype.piFinset_univ]
    _ = ∏ i : Fin k, ∑ ω, g i ω :=
        (Finset.prod_univ_sum (fun _ : Fin k => (Finset.univ : Finset Ω))
          (fun i ω => g i ω)).symm

/-- A product over a finite type with exactly two designated factors. -/
lemma prod_ite_pair {ι : Type*} [Fintype ι] [DecidableEq ι] (i j : ι) (hij : i ≠ j)
    (f g : ι → ℝ) :
    (∏ l, (if l = i then f l else if l = j then g l else 1)) = f i * g j := by
  rw [← Finset.mul_prod_erase Finset.univ _ (Finset.mem_univ i), if_pos rfl]
  have hj : j ∈ Finset.univ.erase i := Finset.mem_erase.mpr ⟨hij.symm, Finset.mem_univ j⟩
  rw [← Finset.mul_prod_erase _ _ hj, if_neg hij.symm, if_pos rfl]
  have hrest : ∏ l ∈ (Finset.univ.erase i).erase j,
      (if l = i then f l else if l = j then g l else 1) = 1 := by
    apply Finset.prod_eq_one
    intro l hl
    have h1 : l ≠ j := (Finset.mem_erase.mp hl).1
    have h2 : l ≠ i := (Finset.mem_erase.mp (Finset.mem_erase.mp hl).2).1
    rw [if_neg h2, if_neg h1]
  rw [hrest, mul_one]

/-- Any two ordered pairs of distinct points are conjugate under `Perm`. -/
lemma exists_perm_pair {n : ℕ} (i j i' j' : Fin n) (hij : i ≠ j) (hij' : i' ≠ j') :
    ∃ π : Equiv.Perm (Fin n), π i = i' ∧ π j = j' := by
  refine ⟨Equiv.swap (Equiv.swap i i' j) j' * Equiv.swap i i', ?_, ?_⟩
  · rw [Equiv.Perm.mul_apply, Equiv.swap_apply_left]
    apply Equiv.swap_apply_of_ne_of_ne
    · intro h
      have h2 : Equiv.swap i i' i = Equiv.swap i i' j := by
        rw [Equiv.swap_apply_left]; exact h
      exact hij ((Equiv.swap i i').injective h2)
    · exact hij'
  · rw [Equiv.Perm.mul_apply, Equiv.swap_apply_left]

namespace FinDist

noncomputable section

variable {Ω : Type*} [Fintype Ω] (P : FinDist Ω)

/-! ### Linearity facts and the variance -/

lemma expect_add (f g : Ω → ℝ) :
    P.expect (fun ω => f ω + g ω) = P.expect f + P.expect g := by
  unfold expect
  simp_rw [mul_add]
  exact Finset.sum_add_distrib

lemma expect_const (a : ℝ) : P.expect (fun _ => a) = a := by
  unfold expect
  rw [← Finset.sum_mul, P.sum_one, one_mul]

lemma expect_sum {ι : Type*} [Fintype ι] (g : ι → Ω → ℝ) :
    P.expect (fun ω => ∑ i, g i ω) = ∑ i, P.expect (g i) := by
  unfold expect
  simp_rw [Finset.mul_sum]
  exact Finset.sum_comm

lemma prob_mono {φ ψ : Ω → Prop} (h : ∀ ω, φ ω → ψ ω) : P.prob φ ≤ P.prob ψ := by
  unfold prob
  apply Finset.sum_le_sum
  intro ω _
  by_cases hφ : φ ω
  · rw [if_pos hφ, if_pos (h ω hφ)]
  · rw [if_neg hφ]
    split_ifs
    · exact P.nonneg ω
    · exact le_refl _

/-- Variance of an observable. -/
def variance (f : Ω → ℝ) : ℝ := P.expect (fun ω => (f ω - P.expect f) ^ 2)

lemma variance_eq (f : Ω → ℝ) :
    P.variance f = P.expect (fun ω => f ω ^ 2) - (P.expect f) ^ 2 := by
  unfold variance expect
  have h : ∀ ω : Ω, P.p ω * (f ω - ∑ ω', P.p ω' * f ω') ^ 2
      = P.p ω * f ω ^ 2 - (2 * ∑ ω', P.p ω' * f ω') * (P.p ω * f ω)
        + (∑ ω', P.p ω' * f ω') ^ 2 * P.p ω := by
    intro ω
    ring
  simp_rw [h]
  rw [Finset.sum_add_distrib, Finset.sum_sub_distrib, ← Finset.mul_sum, ← Finset.mul_sum,
    P.sum_one]
  ring

lemma variance_nonneg (f : Ω → ℝ) : 0 ≤ P.variance f :=
  P.expect_nonneg fun _ => sq_nonneg _

lemma variance_le_expect_sq (f : Ω → ℝ) : P.variance f ≤ P.expect (fun ω => f ω ^ 2) := by
  rw [variance_eq]
  linarith [sq_nonneg (P.expect f)]

/-- **Chebyshev**, finite form. -/
theorem chebyshev (f : Ω → ℝ) (a : ℝ) (ha : 0 < a) :
    P.prob (fun ω => a ≤ |f ω - P.expect f|) ≤ P.variance f / a ^ 2 := by
  have hpt : ∀ ω : Ω, (if a ≤ |f ω - P.expect f| then P.p ω else 0)
      ≤ P.p ω * ((f ω - P.expect f) ^ 2 / a ^ 2) := by
    intro ω
    split_ifs with h
    · have h1 : a ^ 2 ≤ (f ω - P.expect f) ^ 2 := by
        calc a ^ 2 ≤ |f ω - P.expect f| ^ 2 := by gcongr
          _ = (f ω - P.expect f) ^ 2 := sq_abs _
      have h2 : (1 : ℝ) ≤ (f ω - P.expect f) ^ 2 / a ^ 2 := by
        rw [le_div_iff₀ (by positivity)]
        linarith
      calc P.p ω = P.p ω * 1 := (mul_one _).symm
        _ ≤ _ := mul_le_mul_of_nonneg_left h2 (P.nonneg ω)
    · exact mul_nonneg (P.nonneg ω) (by positivity)
  calc P.prob (fun ω => a ≤ |f ω - P.expect f|)
      ≤ ∑ ω, P.p ω * ((f ω - P.expect f) ^ 2 / a ^ 2) :=
        Finset.sum_le_sum fun ω _ => hpt ω
    _ = P.variance f / a ^ 2 := by
        unfold variance expect
        rw [Finset.sum_div]
        exact Finset.sum_congr rfl fun ω _ => by ring

/-- Chebyshev for the event "the statistic fails to be positive". -/
theorem prob_nonpos_le_variance_div (f : Ω → ℝ) (hμ : 0 < P.expect f) :
    P.prob (fun ω => f ω ≤ 0) ≤ P.variance f / (P.expect f) ^ 2 := by
  refine le_trans (P.prob_mono ?_) (P.chebyshev f (P.expect f) hμ)
  intro ω h
  rw [abs_sub_comm]
  calc P.expect f ≤ P.expect f - f ω := by linarith
    _ ≤ |P.expect f - f ω| := le_abs_self _

/-! ### Moments under the product law -/

lemma iid_expect_prod (k : ℕ) (f : Fin k → Ω → ℝ) :
    (P.iid k).expect (fun x => ∏ i, f i (x i)) = ∏ i, P.expect (f i) := by
  unfold expect iid
  dsimp only
  have h : ∀ x : Fin k → Ω,
      (∏ i, P.p (x i)) * ∏ i, f i (x i) = ∏ i, (P.p (x i) * f i (x i)) := fun x =>
    (Finset.prod_mul_distrib).symm
  simp_rw [h]
  exact sum_prod_eq_prod_sum k (fun i ω => P.p ω * f i ω)

lemma iid_expect_coord (k : ℕ) (c : Ω → ℝ) (i : Fin k) :
    (P.iid k).expect (fun x => c (x i)) = P.expect c := by
  have h := P.iid_expect_prod k (fun l ω => if l = i then c ω else 1)
  have hL : ∀ x : Fin k → Ω,
      (∏ l, (if l = i then c (x l) else 1)) = c (x i) := by
    intro x
    rw [Fintype.prod_ite_eq']
  have hR : ∀ l : Fin k,
      P.expect (fun ω => if l = i then c ω else 1) = if l = i then P.expect c else 1 := by
    intro l
    by_cases hl : l = i
    · simp [hl]
    · simp [hl, P.expect_const]
  simp_rw [hL, hR, Fintype.prod_ite_eq'] at h
  exact h

lemma iid_expect_coord_mul (k : ℕ) (c : Ω → ℝ) (i j : Fin k) (hij : i ≠ j) :
    (P.iid k).expect (fun x => c (x i) * c (x j)) = (P.expect c) * (P.expect c) := by
  have h := P.iid_expect_prod k (fun l ω => if l = i then c ω else if l = j then c ω else 1)
  have hL : ∀ x : Fin k → Ω,
      (∏ l, (if l = i then c (x l) else if l = j then c (x l) else 1)) = c (x i) * c (x j) := by
    intro x
    exact prod_ite_pair i j hij (fun l => c (x l)) (fun l => c (x l))
  have hR : ∀ l : Fin k,
      P.expect (fun ω => if l = i then c ω else if l = j then c ω else 1)
        = if l = i then P.expect c else if l = j then P.expect c else 1 := by
    intro l
    by_cases hl : l = i
    · simp [hl]
    · by_cases hl' : l = j
      · simp [hl']
      · simp [hl, hl', P.expect_const]
  simp_rw [hL, hR] at h
  rw [prod_ite_pair i j hij (fun _ => P.expect c) (fun _ => P.expect c)] at h
  exact h

lemma iid_expect_sum (k : ℕ) (c : Ω → ℝ) :
    (P.iid k).expect (fun x => ∑ i, c (x i)) = (k : ℝ) * P.expect c := by
  rw [expect_sum]
  simp_rw [P.iid_expect_coord]
  rw [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]

/-- **Exact variance of the prefix sum under the product law**: `k · Var(c)`. -/
theorem iid_variance_sum (k : ℕ) (c : Ω → ℝ) :
    (P.iid k).variance (fun x => ∑ i, c (x i)) = (k : ℝ) * P.variance c := by
  rw [variance_eq, variance_eq, iid_expect_sum]
  set A := P.expect (fun ω => c ω ^ 2) with hA
  set B := (P.expect c) ^ 2 with hB
  have hsq : ∀ x : Fin k → Ω, (∑ i, c (x i)) ^ 2 = ∑ i, ∑ j, c (x i) * c (x j) := by
    intro x
    rw [sq, Finset.sum_mul_sum]
  simp_rw [hsq]
  rw [expect_sum]
  simp_rw [expect_sum]
  have hpair : ∀ i j : Fin k,
      (P.iid k).expect (fun x => c (x i) * c (x j)) = if i = j then A else B := by
    intro i j
    split_ifs with h
    · subst h
      have h2 := P.iid_expect_coord k (fun ω => c ω ^ 2) i
      have h3 : ∀ x : Fin k → Ω, c (x i) * c (x i) = c (x i) ^ 2 := fun x => (sq _).symm
      simp_rw [h3]
      exact h2
    · rw [P.iid_expect_coord_mul k c i j h, hB, sq]
  simp_rw [hpair]
  have hrow : ∀ i : Fin k, (∑ j : Fin k, if i = j then A else B) = (k : ℝ) * B + (A - B) := by
    intro i
    have h1 : ∀ j : Fin k, (if i = j then A else B) = B + (if i = j then A - B else 0) := by
      intro j
      split_ifs <;> ring
    simp_rw [h1]
    rw [Finset.sum_add_distrib, Finset.sum_const, Finset.card_univ, Fintype.card_fin,
      nsmul_eq_mul, Finset.sum_ite_eq, if_pos (Finset.mem_univ i)]
  simp_rw [hrow]
  rw [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
  ring

/-- **The `σ²`-sharp budget–stakes scaling at Chebyshev grade (i.i.d. model)**:
`P^k(∑ c ≤ 0) ≤ Var(c)/(k μ²)`. For the cell score `Var(c) ≤ E[c²] = σ²`. -/
theorem iid_prob_sum_nonpos_le_cheb (c : Ω → ℝ) (hμ : 0 < P.expect c) (k : ℕ) (hk : 0 < k) :
    (P.iid k).prob (fun x => (∑ i, c (x i)) ≤ 0)
      ≤ P.variance c / ((k : ℝ) * (P.expect c) ^ 2) := by
  have hμk : 0 < (P.iid k).expect (fun x => ∑ i, c (x i)) := by
    rw [iid_expect_sum]
    have : (0 : ℝ) < k := by exact_mod_cast hk
    positivity
  have h := (P.iid k).prob_nonpos_le_variance_div (fun x => ∑ i, c (x i)) hμk
  rw [iid_variance_sum, iid_expect_sum] at h
  have hk' : (k : ℝ) ≠ 0 := by exact_mod_cast hk.ne'
  have hμ' : P.expect c ≠ 0 := hμ.ne'
  calc _ ≤ _ := h
    _ = P.variance c / ((k : ℝ) * (P.expect c) ^ 2) := by
        field_simp

/-! ### Shuffling an i.i.d. prefix leaves its law invariant -/

/-- The product law is exchangeable: composing the sample with a fixed
permutation of the coordinates does not change expectations. -/
theorem iid_expect_comp_perm (k : ℕ) (f : (Fin k → Ω) → ℝ) (π : Equiv.Perm (Fin k)) :
    (P.iid k).expect (fun x => f (x ∘ π)) = (P.iid k).expect f := by
  unfold expect iid
  dsimp only
  refine Fintype.sum_equiv (Equiv.arrowCongr π.symm (Equiv.refl Ω)) _ _ (fun x => ?_)
  simp only [Equiv.arrowCongr_apply, Equiv.symm_symm, Equiv.coe_refl, Function.id_comp]
  congr 1
  exact (Equiv.prod_comp π (fun i => P.p (x i))).symm

/-- **Random order of an i.i.d. population is i.i.d.**: averaging the shuffled
sample over a uniformly random permutation gives back the product law. This is
the formal content of the Yao-style transfer of the lower bound to the
random-order model. -/
theorem shuffled_iid_expect (k : ℕ) (f : (Fin k → Ω) → ℝ) (U : FinDist (Equiv.Perm (Fin k))) :
    U.expect (fun σ => (P.iid k).expect (fun x => f (x ∘ σ))) = (P.iid k).expect f := by
  simp_rw [P.iid_expect_comp_perm k f]
  exact U.expect_const _

end

end FinDist

/-! ### The random-order model: uniform permutations of a fixed population -/

namespace RandomOrder

open FinDist

noncomputable section

/-- The uniform distribution on permutations of `Fin n`. -/
def uniformPerm (n : ℕ) : FinDist (Equiv.Perm (Fin n)) where
  p := fun _ => 1 / (Fintype.card (Equiv.Perm (Fin n)) : ℝ)
  nonneg := fun _ => by positivity
  sum_one := by
    rw [Finset.sum_const, Finset.card_univ, nsmul_eq_mul]
    have h : (0 : ℝ) < Fintype.card (Equiv.Perm (Fin n)) := by exact_mod_cast Fintype.card_pos
    field_simp

/-- Right-multiplication invariance of the uniform law. -/
lemma uniformPerm_expect_mul_right (n : ℕ) (f : Equiv.Perm (Fin n) → ℝ)
    (π : Equiv.Perm (Fin n)) :
    (uniformPerm n).expect (fun σ => f (σ * π)) = (uniformPerm n).expect f := by
  unfold expect uniformPerm
  dsimp only
  exact Fintype.sum_equiv (Equiv.mulRight π) _ _ (fun σ => rfl)

/-- **Exchangeability at one position**: the image of any fixed index under a
uniform permutation is uniform on `Fin n`. No counting — only transitivity. -/
theorem uniformPerm_expect_apply (n : ℕ) (g : Fin n → ℝ) (i : Fin n) :
    (uniformPerm n).expect (fun σ => g (σ i)) = (∑ a, g a) / n := by
  have hsym : ∀ i' : Fin n,
      (uniformPerm n).expect (fun σ => g (σ i')) = (uniformPerm n).expect (fun σ => g (σ i)) := by
    intro i'
    have h := uniformPerm_expect_mul_right n (fun σ => g (σ i)) (Equiv.swap i i')
    simp only [Equiv.Perm.mul_apply, Equiv.swap_apply_left] at h
    exact h
  have hsum : ∑ i' : Fin n, (uniformPerm n).expect (fun σ => g (σ i')) = ∑ a, g a := by
    have h1 : ∑ i' : Fin n, (uniformPerm n).expect (fun σ => g (σ i'))
        = (uniformPerm n).expect (fun σ => ∑ i', g (σ i')) := ((uniformPerm n).expect_sum _).symm
    rw [h1]
    have h2 : ∀ σ : Equiv.Perm (Fin n), (∑ i', g (σ i')) = ∑ a, g a := fun σ =>
      Equiv.sum_comp σ g
    simp_rw [h2]
    exact (uniformPerm n).expect_const _
  simp_rw [hsym] at hsum
  rw [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul] at hsum
  have hn : (n : ℝ) ≠ 0 := by
    have := i.pos
    positivity
  rw [eq_div_iff hn]
  linarith [hsum]

/-- **Exchangeability at two positions**: the images of two distinct indices are
uniform on ordered pairs of distinct points. -/
theorem uniformPerm_expect_pair (n : ℕ) (g h : Fin n → ℝ) (i j : Fin n) (hij : i ≠ j) :
    (uniformPerm n).expect (fun σ => g (σ i) * h (σ j))
      = (∑ a, ∑ b, if a = b then 0 else g a * h b) / ((n : ℝ) * (n - 1)) := by
  set E₀ := (uniformPerm n).expect (fun σ => g (σ i) * h (σ j)) with hE₀
  have hsym : ∀ i' j' : Fin n, i' ≠ j' →
      (uniformPerm n).expect (fun σ => g (σ i') * h (σ j')) = E₀ := by
    intro i' j' hij'
    obtain ⟨π, hπi, hπj⟩ := exists_perm_pair i j i' j' hij hij'
    have hh := uniformPerm_expect_mul_right n (fun σ => g (σ i) * h (σ j)) π
    simp only [Equiv.Perm.mul_apply, hπi, hπj] at hh
    exact hh
  -- the double sum over distinct index pairs, two ways
  have hcount : ∑ i' : Fin n, ∑ j' : Fin n,
      (if i' = j' then (0 : ℝ) else (uniformPerm n).expect (fun σ => g (σ i') * h (σ j')))
        = (n : ℝ) * (n - 1) * E₀ := by
    have h1 : ∀ i' j' : Fin n,
        (if i' = j' then (0 : ℝ) else (uniformPerm n).expect (fun σ => g (σ i') * h (σ j')))
          = E₀ - (if i' = j' then E₀ else 0) := by
      intro i' j'
      by_cases hh : i' = j'
      · simp [hh]
      · rw [if_neg hh, if_neg hh, hsym i' j' hh]
        ring
    simp_rw [h1]
    simp only [Finset.sum_sub_distrib, Finset.sum_const, Finset.card_univ, Fintype.card_fin,
      nsmul_eq_mul, Finset.sum_ite_eq, Finset.mem_univ, if_true]
    ring
  have hsum : ∑ i' : Fin n, ∑ j' : Fin n,
      (if i' = j' then (0 : ℝ) else (uniformPerm n).expect (fun σ => g (σ i') * h (σ j')))
        = ∑ a, ∑ b, if a = b then 0 else g a * h b := by
    have h1 : ∀ i' j' : Fin n,
        (if i' = j' then (0 : ℝ) else (uniformPerm n).expect (fun σ => g (σ i') * h (σ j')))
          = (uniformPerm n).expect (fun σ => if i' = j' then 0 else g (σ i') * h (σ j')) := by
      intro i' j'
      by_cases hh : i' = j'
      · simp [hh, (uniformPerm n).expect_const]
      · simp [hh]
    simp_rw [h1]
    have h2 : ∑ i' : Fin n, ∑ j' : Fin n,
        (uniformPerm n).expect (fun σ => if i' = j' then (0 : ℝ) else g (σ i') * h (σ j'))
          = (uniformPerm n).expect
              (fun σ => ∑ i' : Fin n, ∑ j' : Fin n,
                if i' = j' then (0 : ℝ) else g (σ i') * h (σ j')) := by
      rw [expect_sum]
      exact Finset.sum_congr rfl fun i' _ => ((uniformPerm n).expect_sum _).symm
    rw [h2]
    have h3 : ∀ σ : Equiv.Perm (Fin n),
        (∑ i' : Fin n, ∑ j' : Fin n, if i' = j' then (0 : ℝ) else g (σ i') * h (σ j'))
          = ∑ a, ∑ b, if a = b then 0 else g a * h b := by
      intro σ
      have h4 : ∀ i' j' : Fin n, (if i' = j' then (0 : ℝ) else g (σ i') * h (σ j'))
          = (if σ i' = σ j' then 0 else g (σ i') * h (σ j')) := by
        intro i' j'
        simp only [σ.injective.eq_iff]
      simp_rw [h4]
      calc (∑ i' : Fin n, ∑ j' : Fin n, if σ i' = σ j' then (0 : ℝ) else g (σ i') * h (σ j'))
          = ∑ a, ∑ j' : Fin n, (if a = σ j' then (0 : ℝ) else g a * h (σ j')) :=
            Equiv.sum_comp σ (fun a => ∑ j' : Fin n, if a = σ j' then (0 : ℝ) else g a * h (σ j'))
        _ = ∑ a, ∑ b, if a = b then 0 else g a * h b :=
            Finset.sum_congr rfl fun a _ =>
              Equiv.sum_comp σ (fun b => if a = b then (0 : ℝ) else g a * h b)
    simp_rw [h3]
    exact (uniformPerm n).expect_const _
  have hn2 : (2 : ℝ) ≤ n := by
    have : 2 ≤ n := by
      by_contra hlt
      exact hij (Fin.ext (by have := i.isLt; have := j.isLt; omega))
    exact_mod_cast this
  have hden : (n : ℝ) * (n - 1) ≠ 0 := by
    apply mul_ne_zero <;> linarith
  rw [eq_div_iff hden]
  linarith [hcount, hsum]

variable {Ω : Type*}

/-- Population mean of a score over `M`. -/
def popMean {n : ℕ} (M : Fin n → Ω) (c : Ω → ℝ) : ℝ := (∑ a, c (M a)) / n

/-- Population second moment of a score over `M`. -/
def popSq {n : ℕ} (M : Fin n → Ω) (c : Ω → ℝ) : ℝ := (∑ a, c (M a) ^ 2) / n

/-- The directional statistic on the first `k` arrivals of the order `σ`. -/
def roSum {n : ℕ} (M : Fin n → Ω) (c : Ω → ℝ) (k : ℕ) (hk : k ≤ n)
    (σ : Equiv.Perm (Fin n)) : ℝ :=
  ∑ i : Fin k, c (M (σ (Fin.castLE hk i)))

lemma roSum_expect {n : ℕ} (M : Fin n → Ω) (c : Ω → ℝ) (k : ℕ) (hk : k ≤ n) :
    (uniformPerm n).expect (roSum M c k hk) = (k : ℝ) * popMean M c := by
  unfold roSum popMean
  rw [expect_sum]
  have h : ∀ i : Fin k,
      (uniformPerm n).expect (fun σ => c (M (σ (Fin.castLE hk i)))) = (∑ a, c (M a)) / n :=
    fun i => uniformPerm_expect_apply n (fun a => c (M a)) (Fin.castLE hk i)
  simp_rw [h]
  rw [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]

/-- Sum over ordered pairs of distinct indices, in closed form. -/
lemma sum_offdiag_eq {n : ℕ} (v : Fin n → ℝ) :
    (∑ a, ∑ b, if a = b then (0 : ℝ) else v a * v b) = (∑ a, v a) ^ 2 - ∑ a, v a ^ 2 := by
  have h : ∀ a b : Fin n, (if a = b then (0 : ℝ) else v a * v b)
      = v a * v b - (if a = b then v a * v b else 0) := by
    intro a b
    split_ifs <;> ring
  simp_rw [h]
  simp only [Finset.sum_sub_distrib, Finset.sum_ite_eq, Finset.mem_univ, if_true]
  rw [sq, Finset.sum_mul_sum]
  congr 1
  exact Finset.sum_congr rfl fun a _ => (sq _).symm

/-- **Finite-population variance bound**: `Var(∑_{i<k} c(M(σ i))) ≤ k · E_pop[c²]`
(the exact value is `k · Var_pop(c) · (n−k)/(n−1)`). -/
theorem roSum_variance_le {n : ℕ} (M : Fin n → Ω) (c : Ω → ℝ) (k : ℕ) (hk : k ≤ n)
    (hn : 2 ≤ n) :
    (uniformPerm n).variance (roSum M c k hk) ≤ (k : ℝ) * popSq M c := by
  rw [variance_eq, roSum_expect]
  set μ := popMean M c with hμ
  set q := popSq M c with hq
  set X := (∑ a, ∑ b, if a = b then (0 : ℝ) else c (M a) * c (M b)) / ((n : ℝ) * (n - 1))
    with hX
  -- second moment of the prefix sum
  have hsq : ∀ σ : Equiv.Perm (Fin n), roSum M c k hk σ ^ 2
      = ∑ i : Fin k, ∑ j : Fin k, c (M (σ (Fin.castLE hk i))) * c (M (σ (Fin.castLE hk j))) := by
    intro σ
    unfold roSum
    rw [sq, Finset.sum_mul_sum]
  simp_rw [hsq]
  rw [expect_sum]
  simp_rw [expect_sum]
  have hpair : ∀ i j : Fin k,
      (uniformPerm n).expect (fun σ => c (M (σ (Fin.castLE hk i))) * c (M (σ (Fin.castLE hk j))))
        = if i = j then q else X := by
    intro i j
    split_ifs with h
    · subst h
      have h2 := uniformPerm_expect_apply n (fun a => c (M a) ^ 2) (Fin.castLE hk i)
      have h3 : ∀ σ : Equiv.Perm (Fin n),
          c (M (σ (Fin.castLE hk i))) * c (M (σ (Fin.castLE hk i)))
            = c (M (σ (Fin.castLE hk i))) ^ 2 := fun σ => (sq _).symm
      simp_rw [h3]
      exact h2
    · have hij : Fin.castLE hk i ≠ Fin.castLE hk j := fun heq => h (Fin.castLE_injective hk heq)
      exact uniformPerm_expect_pair n (fun a => c (M a)) (fun a => c (M a)) _ _ hij
  simp_rw [hpair]
  have hrow : ∀ i : Fin k, (∑ j : Fin k, if i = j then q else X) = (k : ℝ) * X + (q - X) := by
    intro i
    have h1 : ∀ j : Fin k, (if i = j then q else X) = X + (if i = j then q - X else 0) := by
      intro j
      split_ifs <;> ring
    simp_rw [h1]
    rw [Finset.sum_add_distrib, Finset.sum_const, Finset.card_univ, Fintype.card_fin,
      nsmul_eq_mul, Finset.sum_ite_eq, if_pos (Finset.mem_univ i)]
  simp_rw [hrow]
  rw [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
  -- now: k * (k * X + (q - X)) - (k * μ)^2 ≤ k * q
  have hnR : (2 : ℝ) ≤ n := by exact_mod_cast hn
  have hkR : (k : ℝ) ≤ n := by exact_mod_cast hk
  have hk0 : (0 : ℝ) ≤ k := by positivity
  have hq0 : 0 ≤ q := by
    rw [hq]
    unfold popSq
    apply div_nonneg (Finset.sum_nonneg fun a _ => sq_nonneg _) (by positivity)
  have hXval : X * ((n : ℝ) * (n - 1)) = (n * μ) ^ 2 - n * q := by
    rw [hX, div_mul_cancel₀ _ (by apply mul_ne_zero <;> linarith), sum_offdiag_eq]
    rw [hμ, hq]
    unfold popMean popSq
    have hn0 : (n : ℝ) ≠ 0 := by linarith
    field_simp
  -- reduce to a polynomial inequality
  have key : (k : ℝ) * (k - 1) * X ≤ (k : ℝ) ^ 2 * μ ^ 2 := by
    have hden : (0 : ℝ) < (n : ℝ) * (n - 1) := by
      apply mul_pos <;> linarith
    apply le_of_mul_le_mul_right _ hden
    have hlhs : (k : ℝ) * (k - 1) * X * ((n : ℝ) * (n - 1))
        = (k : ℝ) * (k - 1) * ((n * μ) ^ 2 - n * q) := by
      rw [mul_assoc, hXval]
    rw [hlhs]
    have h1 : 0 ≤ (k : ℝ) * n * μ ^ 2 * (n - k) := by
      apply mul_nonneg
      · apply mul_nonneg (mul_nonneg hk0 (by linarith)) (sq_nonneg _)
      · linarith
    have h2 : 0 ≤ (k : ℝ) * (k - 1) * n * q := by
      rcases Nat.eq_zero_or_pos k with hk0' | hkpos
      · subst hk0'
        simp
      · have : (1 : ℝ) ≤ k := by exact_mod_cast hkpos
        apply mul_nonneg (mul_nonneg (mul_nonneg hk0 (by linarith)) (by linarith)) hq0
    nlinarith [h1, h2]
  nlinarith [key]

/-- **The budget–stakes scaling under random order, Chebyshev grade**: if the
population mean of the score is `μ > 0`, then the probability that the
directional statistic on a uniformly random `k`-prefix fails to be positive is
at most `E_pop[c²] / (k μ²)`. -/
theorem ro_prob_sum_nonpos_le {n : ℕ} (M : Fin n → Ω) (c : Ω → ℝ) (k : ℕ) (hk : k ≤ n)
    (hn : 2 ≤ n) (hk0 : 0 < k) (hμ : 0 < popMean M c) :
    (uniformPerm n).prob (fun σ => roSum M c k hk σ ≤ 0)
      ≤ popSq M c / ((k : ℝ) * (popMean M c) ^ 2) := by
  have hμk : 0 < (uniformPerm n).expect (roSum M c k hk) := by
    rw [roSum_expect]
    have : (0 : ℝ) < k := by exact_mod_cast hk0
    positivity
  have h := (uniformPerm n).prob_nonpos_le_variance_div (roSum M c k hk) hμk
  have hvar := roSum_variance_le M c k hk hn
  rw [roSum_expect] at h
  have hk' : (k : ℝ) ≠ 0 := by exact_mod_cast hk0.ne'
  have hμ' : popMean M c ≠ 0 := hμ.ne'
  calc (uniformPerm n).prob (fun σ => roSum M c k hk σ ≤ 0)
      ≤ (uniformPerm n).variance (roSum M c k hk) / ((k : ℝ) * popMean M c) ^ 2 := h
    _ ≤ ((k : ℝ) * popSq M c) / ((k : ℝ) * popMean M c) ^ 2 := by
        gcongr
    _ = popSq M c / ((k : ℝ) * (popMean M c) ^ 2) := by
        field_simp

end

end RandomOrder

end BudgetStakes
