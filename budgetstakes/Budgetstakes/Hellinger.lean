/-
Copyright (c) 2026 Zhuolun Li. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Zhuolun Li
-/
import Budgetstakes.Chernoff

/-!
# Stage 5: the Hellinger route to the lower bound (Theorem 1(i), abstract core)

The impossibility half of the budget–stakes law, on finite spaces:

* `bc` — the Bhattacharyya coefficient `∑ √(p·q)`; the normalized squared
  Hellinger distance is `1 − bc`.
* `bc_iid` — **tensorization**: `bc(P^k, Q^k) = bc(P,Q)^k`, one more application
  of `sum_prod_eq_pow`.
* `tvDist_sq_le_two_sub_two_bc` — the Cauchy–Schwarz comparison
  `TV² ≤ 2(1 − bc)`.
* `one_sub_pow_le` — Bernoulli: `1 − b^k ≤ k(1 − b)`.
* `tvDist_iid_le` — the chain: `TV(P^k, Q^k) ≤ √(2k(1 − bc(P,Q)))`.
* `Scenario.master_tradeoff_iid` — combined with Stage 3:
  `(1 − η_c) ≤ η_r + √(2k(1 − bc))` for **any** decision rule on the prefix.

With the cell-family computation `1 − bc = (1/N)·∑_{i ∈ W} θᵢ(1 − √(1−4eᵢ²))`
(Stage 5b) this is exactly the paper's Theorem 1(i): below `k ≍ 1/(ε_W·g)` the
two worlds are indistinguishable and the two losses must sum to ≈ 1.
-/

namespace BudgetStakes

/-- Square roots distribute over finite products of nonnegatives. -/
lemma sqrt_prod {ι : Type*} [Fintype ι] (f : ι → ℝ) (hf : ∀ i, 0 ≤ f i) :
    Real.sqrt (∏ i, f i) = ∏ i, Real.sqrt (f i) := by
  have h1 : (∏ i, Real.sqrt (f i)) ^ 2 = ∏ i, f i := by
    rw [← Finset.prod_pow]
    exact Finset.prod_congr rfl fun i _ => Real.sq_sqrt (hf i)
  have h2 : 0 ≤ ∏ i, Real.sqrt (f i) :=
    Finset.prod_nonneg fun i _ => Real.sqrt_nonneg _
  rw [← h1, Real.sqrt_sq h2]

/-- Bernoulli: `1 − b^k ≤ k (1 − b)` for `b ≥ 0`. -/
lemma one_sub_pow_le (b : ℝ) (hb0 : 0 ≤ b) (k : ℕ) :
    1 - b ^ k ≤ (k : ℝ) * (1 - b) := by
  have h := one_add_mul_le_pow (a := b - 1) (by linarith : (-2 : ℝ) ≤ b - 1) k
  have hb : (1 + (b - 1)) = b := by ring
  rw [hb] at h
  linarith

namespace FinDist

noncomputable section

variable {Ω : Type*} [Fintype Ω] (P Q : FinDist Ω)

/-- The Bhattacharyya coefficient `∑ √(p q)`; `1 − bc` is the normalized
squared Hellinger distance. -/
def bc : ℝ := ∑ ω, Real.sqrt (P.p ω * Q.p ω)

lemma bc_nonneg : 0 ≤ P.bc Q :=
  Finset.sum_nonneg fun _ _ => Real.sqrt_nonneg _

lemma bc_le_one : P.bc Q ≤ 1 := by
  have hpt : ∀ ω : Ω,
      Real.sqrt (P.p ω * Q.p ω) ≤ (P.p ω + Q.p ω) / 2 := by
    intro ω
    have ha := Real.sq_sqrt (P.nonneg ω)
    have hb := Real.sq_sqrt (Q.nonneg ω)
    rw [Real.sqrt_mul (P.nonneg ω)]
    nlinarith [sq_nonneg (Real.sqrt (P.p ω) - Real.sqrt (Q.p ω))]
  calc P.bc Q ≤ ∑ ω, (P.p ω + Q.p ω) / 2 :=
        Finset.sum_le_sum fun ω _ => hpt ω
    _ = 1 := by
        rw [← Finset.sum_div, Finset.sum_add_distrib, P.sum_one, Q.sum_one]
        norm_num

/-- **Tensorization**: the Bhattacharyya coefficient of i.i.d. products is the
`k`-th power of the per-arrival coefficient. -/
lemma bc_iid (k : ℕ) : (P.iid k).bc (Q.iid k) = (P.bc Q) ^ k := by
  unfold bc iid
  dsimp only
  have hpt : ∀ x : Fin k → Ω,
      Real.sqrt ((∏ i, P.p (x i)) * ∏ i, Q.p (x i))
        = ∏ i, Real.sqrt (P.p (x i) * Q.p (x i)) := by
    intro x
    rw [← Finset.prod_mul_distrib]
    exact sqrt_prod _ fun i => mul_nonneg (P.nonneg _) (Q.nonneg _)
  simp_rw [hpt]
  exact sum_prod_eq_pow (fun ω => Real.sqrt (P.p ω * Q.p ω)) k

lemma sum_sq_sqrt_sub : ∑ ω, (Real.sqrt (P.p ω) - Real.sqrt (Q.p ω)) ^ 2
    = 2 - 2 * P.bc Q := by
  have hpt : ∀ ω : Ω, (Real.sqrt (P.p ω) - Real.sqrt (Q.p ω)) ^ 2
      = P.p ω + Q.p ω - 2 * Real.sqrt (P.p ω * Q.p ω) := by
    intro ω
    have ha := Real.sq_sqrt (P.nonneg ω)
    have hb := Real.sq_sqrt (Q.nonneg ω)
    rw [Real.sqrt_mul (P.nonneg ω)]
    nlinarith [ha, hb]
  simp_rw [hpt]
  unfold bc
  rw [Finset.sum_sub_distrib, Finset.sum_add_distrib, P.sum_one, Q.sum_one,
    ← Finset.mul_sum]
  ring

lemma sum_sq_sqrt_add : ∑ ω, (Real.sqrt (P.p ω) + Real.sqrt (Q.p ω)) ^ 2
    = 2 + 2 * P.bc Q := by
  have hpt : ∀ ω : Ω, (Real.sqrt (P.p ω) + Real.sqrt (Q.p ω)) ^ 2
      = P.p ω + Q.p ω + 2 * Real.sqrt (P.p ω * Q.p ω) := by
    intro ω
    have ha := Real.sq_sqrt (P.nonneg ω)
    have hb := Real.sq_sqrt (Q.nonneg ω)
    rw [Real.sqrt_mul (P.nonneg ω)]
    nlinarith [ha, hb]
  simp_rw [hpt]
  unfold bc
  rw [Finset.sum_add_distrib, Finset.sum_add_distrib, P.sum_one, Q.sum_one,
    ← Finset.mul_sum]
  ring

/-- **The Cauchy–Schwarz comparison**: `TV² ≤ 2 (1 − bc)`. -/
theorem tvDist_sq_le_two_sub_two_bc :
    (P.tvDist Q) ^ 2 ≤ 2 * (1 - P.bc Q) := by
  have hpt : ∀ ω : Ω, |P.p ω - Q.p ω|
      = |Real.sqrt (P.p ω) - Real.sqrt (Q.p ω)|
          * (Real.sqrt (P.p ω) + Real.sqrt (Q.p ω)) := by
    intro ω
    have ha := Real.sq_sqrt (P.nonneg ω)
    have hb := Real.sq_sqrt (Q.nonneg ω)
    have hfac : P.p ω - Q.p ω
        = (Real.sqrt (P.p ω) - Real.sqrt (Q.p ω))
            * (Real.sqrt (P.p ω) + Real.sqrt (Q.p ω)) := by
      nlinarith [ha, hb]
    rw [hfac, abs_mul,
      abs_of_nonneg (add_nonneg (Real.sqrt_nonneg _) (Real.sqrt_nonneg _))]
  have hcs := Finset.sum_mul_sq_le_sq_mul_sq Finset.univ
      (fun ω => |Real.sqrt (P.p ω) - Real.sqrt (Q.p ω)|)
      (fun ω => Real.sqrt (P.p ω) + Real.sqrt (Q.p ω))
  have hsq : ∀ ω : Ω, |Real.sqrt (P.p ω) - Real.sqrt (Q.p ω)| ^ 2
      = (Real.sqrt (P.p ω) - Real.sqrt (Q.p ω)) ^ 2 := fun ω => sq_abs _
  rw [show (∑ ω, |Real.sqrt (P.p ω) - Real.sqrt (Q.p ω)| ^ 2)
      = ∑ ω, (Real.sqrt (P.p ω) - Real.sqrt (Q.p ω)) ^ 2 from
      Finset.sum_congr rfl fun ω _ => hsq ω] at hcs
  rw [P.sum_sq_sqrt_sub Q, P.sum_sq_sqrt_add Q] at hcs
  have htv : ∑ ω, |P.p ω - Q.p ω|
      = ∑ ω, |Real.sqrt (P.p ω) - Real.sqrt (Q.p ω)|
          * (Real.sqrt (P.p ω) + Real.sqrt (Q.p ω)) :=
    Finset.sum_congr rfl fun ω _ => hpt ω
  have hbc1 := P.bc_le_one Q
  have hbc0 := P.bc_nonneg Q
  unfold tvDist
  rw [div_pow]
  have h2tv : (∑ ω, |P.p ω - Q.p ω|) ^ 2
      ≤ (2 - 2 * P.bc Q) * (2 + 2 * P.bc Q) := by
    rw [htv]
    exact hcs
  nlinarith [h2tv, hbc0, hbc1]

/-- The chained bound: `TV(P^k, Q^k)² ≤ 2k(1 − bc(P,Q))`. -/
theorem tvDist_iid_sq_le (k : ℕ) :
    ((P.iid k).tvDist (Q.iid k)) ^ 2 ≤ 2 * (k : ℝ) * (1 - P.bc Q) := by
  have h1 := (P.iid k).tvDist_sq_le_two_sub_two_bc (Q.iid k)
  rw [P.bc_iid Q k] at h1
  have h2 := one_sub_pow_le (P.bc Q) (P.bc_nonneg Q) k
  linarith

/-- **The prefix indistinguishability bound** (the statistics of Theorem 1(i)):
`TV(P^k, Q^k) ≤ √(2k(1 − bc(P,Q)))`. -/
theorem tvDist_iid_le (k : ℕ) :
    (P.iid k).tvDist (Q.iid k) ≤ Real.sqrt (2 * (k : ℝ) * (1 - P.bc Q)) := by
  have h := P.tvDist_iid_sq_le Q k
  have h0 := (P.iid k).tvDist_nonneg (Q.iid k)
  have hx : 0 ≤ 2 * (k : ℝ) * (1 - P.bc Q) := by
    have h1 := P.bc_le_one Q
    have h2 : (0 : ℝ) ≤ (k : ℝ) := Nat.cast_nonneg k
    nlinarith
  exact (Real.le_sqrt h0 hx).mpr h

end

end FinDist

namespace Scenario

noncomputable section

/-- **Theorem 1(i), abstract core**: for the scenario whose two worlds are
`k`-i.i.d. prefixes of per-arrival laws `Pa, Qa`, every decision rule
`D : prefix → [0,1]` obeys `(1 − η_c) ≤ η_r + √(2k(1 − bc(Pa,Qa)))`. When the
per-arrival Hellinger affinity is high (`bc → 1`) and `k` is below the budget,
the right-hand side pins the sum of losses near one. -/
theorem master_tradeoff_iid {Ωa : Type*} [Fintype Ωa]
    (Pa Qa : FinDist Ωa) (k : ℕ) (ρbase δ Δ : ℝ) (hδ : 0 < δ) (hΔ : 0 < Δ)
    (D : (Fin k → Ωa) → ℝ) (hD0 : ∀ x, 0 ≤ D x) (hD1 : ∀ x, D x ≤ 1) :
    1 - (Scenario.mk (Pa.iid k) (Qa.iid k) ρbase δ Δ hδ hΔ).etaC D
      ≤ (Scenario.mk (Pa.iid k) (Qa.iid k) ρbase δ Δ hδ hΔ).etaR D
        + Real.sqrt (2 * (k : ℝ) * (1 - Pa.bc Qa)) := by
  set S := Scenario.mk (Pa.iid k) (Qa.iid k) ρbase δ Δ hδ hΔ
  have h1 := S.master_tradeoff D hD0 hD1
  have h2 := Pa.tvDist_iid_le Qa k
  have hSG : S.G = Pa.iid k := rfl
  have hSB : S.Bd = Qa.iid k := rfl
  rw [hSG, hSB] at h1
  linarith

end

end Scenario

end BudgetStakes
