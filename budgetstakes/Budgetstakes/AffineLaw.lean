/-
Copyright (c) 2026 Zhuolun Li. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Zhuolun Li
-/
import Budgetstakes.PayoffIdentity

/-!
# Stage 2: the affine law

Formalizes, on finite heterogeneous cell families (paper `docs/paper/06_theory.md` §7.3):

* **The affine law:** `ρ_follow = ρ_perfect − ℓ₁/2`
* **Break-even form:** `stakes = (ℓ₁* − ℓ₁)/2` with `ℓ₁* = 2(ρ_perfect − ρ_base)`
* **Follow-advantage:** `ρ_follow − ρ_base = stakes` (ties Stage 1 to the law)
* **Max-stakes cap:** `ρ_perfect − ρ_base ≤ ε·σ² = 2ε(1 − ρ_base)` when all `|e i| ≤ ε`

Here the advice has matched magnitudes: the truth's signal in cell `i` is `|e i|`,
and the advice direction is right iff `e i ≥ 0`. Following collects
`1 + θ i (1/2 + e i)` in cell `i`; perfect advice collects `1 + θ i (1/2 + |e i|)`;
the advice-to-truth `ℓ₁` distance contributes `2 θ i (|e i| − e i) / N` per cell
(zero when the direction is right, `4 θ i |e i| / N` when wrong).

The per-cell algebra treats `|e i|` as an opaque atom, so `ring` closes it without
any case split on the sign of `e i`.
-/

namespace BudgetStakes

namespace CellFamily

noncomputable section

variable {m : ℕ} (F : CellFamily m)

/-- Competitive ratio of following the advice: `Σ (1 + θ (1/2 + e)) / N`. -/
def rhoFollow : ℝ := (∑ i, (1 + F.θ i * (1 / 2 + F.e i))) / F.N

/-- Competitive ratio of following *perfect* advice (every direction right). -/
def rhoPerfect : ℝ := (∑ i, (1 + F.θ i * (1 / 2 + |F.e i|))) / F.N

/-- The `ℓ₁` distance between the realized type distribution and the advice. -/
def advL1 : ℝ := (∑ i, 2 * F.θ i * (|F.e i| - F.e i)) / F.N

/-- The break-even advice error `ℓ₁* = 2 (ρ_perfect − ρ_base)`. -/
def l1Star : ℝ := 2 * (F.rhoPerfect - F.rhoBase)

/-- **The affine law** (paper §7.3): the follow-ratio is the perfect-advice ratio
minus exactly half the advice error. Unconditional. -/
theorem affine_law : F.rhoFollow = F.rhoPerfect - F.advL1 / 2 := by
  unfold rhoFollow rhoPerfect advL1
  rw [Finset.sum_div, Finset.sum_div, Finset.sum_div]
  have h : ∀ i : Fin m,
      (1 + F.θ i * (1 / 2 + F.e i)) / F.N
        = (1 + F.θ i * (1 / 2 + |F.e i|)) / F.N
          - (2 * F.θ i * (|F.e i| - F.e i)) / F.N / 2 := by
    intro i
    ring
  simp_rw [h]
  rw [Finset.sum_sub_distrib]
  congr 1
  rw [← Finset.sum_div]

/-- The follow-advantage over the baseline is exactly the stakes of Stage 1. -/
theorem rhoFollow_sub_rhoBase : F.rhoFollow - F.rhoBase = F.stakes := by
  unfold rhoFollow rhoBase stakes
  rw [Finset.sum_div, Finset.sum_div, Finset.sum_div, ← Finset.sum_sub_distrib]
  congr 1
  funext i
  ring

/-- The perfect-advice advantage over the baseline, in closed form. -/
theorem rhoPerfect_sub_rhoBase :
    F.rhoPerfect - F.rhoBase = (∑ i, F.θ i * |F.e i|) / F.N := by
  unfold rhoPerfect rhoBase
  rw [Finset.sum_div, Finset.sum_div, Finset.sum_div, ← Finset.sum_sub_distrib]
  congr 1
  funext i
  ring

/-- **Break-even form of the affine law**: the stakes are `(ℓ₁* − ℓ₁)/2`.
Following beats the baseline exactly when the advice error is below `ℓ₁*`. -/
theorem stakes_eq_half_l1Star_sub_advL1 :
    F.stakes = (F.l1Star - F.advL1) / 2 := by
  rw [← F.rhoFollow_sub_rhoBase, F.affine_law]
  unfold l1Star
  ring

/-- The advice error is nonnegative. -/
theorem advL1_nonneg : 0 ≤ F.advL1 := by
  unfold advL1
  apply div_nonneg
  · apply Finset.sum_nonneg
    intro i _
    have h1 : 0 ≤ F.θ i := (F.θ_pos i).le
    have h2 : 0 ≤ |F.e i| - F.e i := sub_nonneg.mpr (le_abs_self _)
    positivity
  · unfold N
    apply Finset.sum_nonneg
    intro i _
    have := (F.θ_pos i).le
    linarith

/-- **Max-stakes cap** (paper §7.3): when every signal is at most `ε`, the full
upside is at most `ε · σ²`, i.e. `2ε(1 − ρ_base)`. -/
theorem rhoPerfect_sub_rhoBase_le (ε : ℝ) (he : ∀ i, |F.e i| ≤ ε) :
    F.rhoPerfect - F.rhoBase ≤ ε * F.specialistMass := by
  rw [F.rhoPerfect_sub_rhoBase]
  unfold specialistMass
  rw [← mul_div_assoc, Finset.mul_sum]
  have hN : 0 ≤ F.N := by
    unfold N
    apply Finset.sum_nonneg
    intro i _
    have := (F.θ_pos i).le
    linarith
  have hnum : (∑ i, F.θ i * |F.e i|) ≤ ∑ i, ε * F.θ i := by
    apply Finset.sum_le_sum
    intro i _
    calc F.θ i * |F.e i| ≤ F.θ i * ε :=
          mul_le_mul_of_nonneg_left (he i) (F.θ_pos i).le
      _ = ε * F.θ i := mul_comm _ _
  rcases eq_or_lt_of_le hN with h0 | hpos
  · rw [← h0, div_zero, div_zero]
  · gcongr

/-- The cap in slack form: the full upside is at most `2ε(1 − ρ_base)`. -/
theorem rhoPerfect_sub_rhoBase_le_slack (ε : ℝ) (he : ∀ i, |F.e i| ≤ ε)
    (hN : F.N ≠ 0) :
    F.rhoPerfect - F.rhoBase ≤ 2 * ε * (1 - F.rhoBase) := by
  have h := F.rhoPerfect_sub_rhoBase_le ε he
  rw [F.slack_eq_half_specialistMass hN]
  linarith

end

end CellFamily

end BudgetStakes
