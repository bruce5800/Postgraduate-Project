/-
Copyright (c) 2026 Zhuolun Li. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Zhuolun Li
-/
import Mathlib

/-!
# Stage 1: the payoff identity and the slack identity

Formalizes, on finite heterogeneous cell families (paper `docs/paper/06_theory.md`):

* **§7.4, Lemma 2 (payoff identity):** `E[score] = 2 · stakes`
* **§7.3 (slack identity):** `1 − ρ_base = σ²/2`

Model: a family of `m` independent rare-resource cells. Cell `i` has contention
`θ i ∈ (0,1]` and signed advice-relative bias `e i ∈ [−1/2, 1/2]`
(`e i = (s i − 1/2) · d̂ i`; positive means the truth agrees with the advice).
A single arrival is: the flexible request of cell `i` with mass `1/N`, its
advice-favored specialist with mass `θ i (1/2 + e i) / N`, or its disfavored
specialist with mass `θ i (1/2 − e i) / N`, where `N = ∑ i (1 + θ i) = OPT`.
The score of an arrival is `+1` on favored specialists, `−1` on disfavored,
`0` on flexible. Everything here is finite `Finset` algebra — no measure theory.
-/

namespace BudgetStakes

/-- A finite heterogeneous cell family. -/
structure CellFamily (m : ℕ) where
  /-- per-cell contention (probability the cell's specialist arrives) -/
  θ : Fin m → ℝ
  /-- signed bias relative to the advice direction, `(s − 1/2)·d̂` -/
  e : Fin m → ℝ
  /-- contentions are positive -/
  θ_pos : ∀ i, 0 < θ i
  /-- contentions are at most one -/
  θ_le_one : ∀ i, θ i ≤ 1
  /-- biases lie in `[−1/2, 1/2]` -/
  e_abs_le : ∀ i, |e i| ≤ 1 / 2

namespace CellFamily

noncomputable section

variable {m : ℕ} (F : CellFamily m)

/-- The normalizer `N = ∑ (1 + θ i)`; it equals `OPT` on the family. -/
def N : ℝ := ∑ i, (1 + F.θ i)

/-- Arrival mass of cell `i`'s flexible request. -/
def pFlex (_i : Fin m) : ℝ := 1 / F.N

/-- Arrival mass of cell `i`'s advice-favored specialist. -/
def pFav (i : Fin m) : ℝ := F.θ i * (1 / 2 + F.e i) / F.N

/-- Arrival mass of cell `i`'s advice-disfavored specialist. -/
def pDis (i : Fin m) : ℝ := F.θ i * (1 / 2 - F.e i) / F.N

/-- Expected per-arrival score: `+1` on favored, `−1` on disfavored, `0` on flex. -/
def scoreExp : ℝ := ∑ i, (F.pFav i - F.pDis i)

/-- The stakes: follow-advantage over the baseline, normalized by `OPT`. -/
def stakes : ℝ := (∑ i, F.θ i * F.e i) / F.N

/-- Specialist mass `σ² = (∑ θ i)/N` — the probability that an arrival is a
specialist, and the variance bound on the score. -/
def specialistMass : ℝ := (∑ i, F.θ i) / F.N

/-- Baseline ratio: the uniform-routing baseline collects `1 + θ i / 2` per cell. -/
def rhoBase : ℝ := (∑ i, (1 + F.θ i / 2)) / F.N

/-- `N` is positive when the family is nonempty. -/
lemma N_pos (hm : 0 < m) : 0 < F.N := by
  have hterm : ∀ i : Fin m, (0 : ℝ) < 1 + F.θ i := fun i =>
    add_pos one_pos (F.θ_pos i)
  have : Nonempty (Fin m) := Fin.pos_iff_nonempty.mp hm
  exact Finset.sum_pos (fun i _ => hterm i) Finset.univ_nonempty

/-- The three masses of a cell sum to `(1 + θ i)/N`, so all masses sum to 1. -/
theorem mass_sum_eq_one (hN : F.N ≠ 0) :
    ∑ i, (F.pFlex i + F.pFav i + F.pDis i) = 1 := by
  have h : ∀ i : Fin m,
      F.pFlex i + F.pFav i + F.pDis i = (1 + F.θ i) / F.N := by
    intro i
    unfold pFlex pFav pDis
    ring
  simp_rw [h]
  rw [← Finset.sum_div]
  exact div_self hN

/-- **The payoff identity** (paper Lemma 2): the expected score equals twice the
stakes — for every heterogeneous profile, magnitudes matched or not. Holds
unconditionally thanks to the `x/0 = 0` convention. -/
theorem payoff_identity : F.scoreExp = 2 * F.stakes := by
  unfold scoreExp stakes
  have h : ∀ i : Fin m,
      F.pFav i - F.pDis i = 2 * (F.θ i * F.e i) / F.N := by
    intro i
    unfold pFav pDis
    ring
  simp_rw [h]
  rw [← Finset.sum_div, ← Finset.mul_sum, mul_div_assoc]

/-- **The slack identity** (paper §7.3): the baseline slack is exactly half the
specialist mass, `1 − ρ_base = σ²/2`. -/
theorem slack_eq_half_specialistMass (hN : F.N ≠ 0) :
    1 - F.rhoBase = F.specialistMass / 2 := by
  unfold rhoBase specialistMass
  have hsplit : (∑ i, (1 + F.θ i / 2)) = F.N - (∑ i, F.θ i) / 2 := by
    unfold N
    rw [Finset.sum_add_distrib, Finset.sum_add_distrib, ← Finset.sum_div]
    ring
  rw [hsplit, sub_div, div_self hN]
  ring

end

end CellFamily

end BudgetStakes
