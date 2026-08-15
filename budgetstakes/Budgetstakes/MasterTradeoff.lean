/-
Copyright (c) 2026 Zhuolun Li. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Zhuolun Li
-/
import Mathlib

/-!
# Stage 3: the master trade-off inequality (Lemma 1), non-asymptotic

Formalizes paper §7.2 in exact, non-asymptotic form on finite sample spaces.

Two layers:

* **Statistical core** (`FinDist.expect_sub_le_tvDist`): for finite distributions
  `P, Q` on `Ω` and any decision rule `D : Ω → [0,1]` — deterministic or the
  follow-probability of a randomized rule — `E_P[D] − E_Q[D] ≤ TV(P,Q)`.
  This is the finite form of the coupling characterization of total variation:
  no rule computed from the observation can behave more differently across two
  worlds than their laws differ.

* **Competitive-ratio wrapper** (`Scenario.master_tradeoff`): two worlds sharing
  one advice; following gains `δ` in world `G` and loses `Δ` in world `Bd`; a
  test-and-fallback algorithm's value is `ρ_base + δ·E_G[D]` resp.
  `ρ_base − Δ·E_Bd[D]`. With `η_c` the forgone-upside fraction and `η_r` the
  robustness-loss fraction, `(1 − η_c) ≤ η_r + TV(L_G, L_Bd)` — **exactly**.

Modeling note (honest boundary): the paper's `o(1)` absorbs the prefix's own
`O(k/n)` contribution to the ratio; here the value is defined as the
post-decision ratio, which makes the inequality exact. The prefix space `Ω` is
arbitrary finite — Stage 5 instantiates it with `Fin k → Arrival` and product
laws.
-/

namespace BudgetStakes

/-- A finitely supported probability distribution, as plain real weights. -/
structure FinDist (Ω : Type*) [Fintype Ω] where
  /-- point masses -/
  p : Ω → ℝ
  /-- masses are nonnegative -/
  nonneg : ∀ ω, 0 ≤ p ω
  /-- masses sum to one -/
  sum_one : ∑ ω, p ω = 1

namespace FinDist

noncomputable section

variable {Ω : Type*} [Fintype Ω] (P Q : FinDist Ω)

/-- Expectation of a real observable. -/
def expect (f : Ω → ℝ) : ℝ := ∑ ω, P.p ω * f ω

/-- Total variation distance, finite form: `½ Σ |P − Q|`. -/
def tvDist : ℝ := (∑ ω, |P.p ω - Q.p ω|) / 2

lemma tvDist_nonneg : 0 ≤ P.tvDist Q := by
  unfold tvDist
  apply div_nonneg _ (by norm_num)
  exact Finset.sum_nonneg fun ω _ => abs_nonneg _

lemma tvDist_comm : P.tvDist Q = Q.tvDist P := by
  unfold tvDist
  congr 1
  exact Finset.sum_congr rfl fun ω _ => abs_sub_comm _ _

/-- The positive parts of `P − Q` sum to exactly `TV(P,Q)` — because the signed
differences sum to zero. -/
lemma sum_posPart_eq_tvDist :
    ∑ ω, max (P.p ω - Q.p ω) 0 = P.tvDist Q := by
  have hzero : ∑ ω, (P.p ω - Q.p ω) = 0 := by
    rw [Finset.sum_sub_distrib, P.sum_one, Q.sum_one, sub_self]
  have hpt : ∀ ω : Ω,
      max (P.p ω - Q.p ω) 0 = (|P.p ω - Q.p ω| + (P.p ω - Q.p ω)) / 2 := by
    intro ω
    rcases abs_cases (P.p ω - Q.p ω) with ⟨h1, h2⟩ | ⟨h1, h2⟩
    · rw [h1, max_eq_left h2]
      ring
    · rw [h1, max_eq_right h2.le]
      ring
  simp_rw [hpt]
  rw [← Finset.sum_div, Finset.sum_add_distrib, hzero, add_zero]
  rfl

/-- **The coupling bound** (statistical core of Lemma 1): a `[0,1]`-valued rule's
expectation differs across two worlds by at most their total variation. -/
theorem expect_sub_le_tvDist (D : Ω → ℝ)
    (hD0 : ∀ ω, 0 ≤ D ω) (hD1 : ∀ ω, D ω ≤ 1) :
    P.expect D - Q.expect D ≤ P.tvDist Q := by
  unfold expect
  rw [← Finset.sum_sub_distrib]
  have hstep : ∀ ω : Ω,
      P.p ω * D ω - Q.p ω * D ω ≤ max (P.p ω - Q.p ω) 0 := by
    intro ω
    have hfactor : P.p ω * D ω - Q.p ω * D ω = (P.p ω - Q.p ω) * D ω := by ring
    rw [hfactor]
    rcases le_total 0 (P.p ω - Q.p ω) with hd | hd
    · calc (P.p ω - Q.p ω) * D ω ≤ (P.p ω - Q.p ω) * 1 :=
            mul_le_mul_of_nonneg_left (hD1 ω) hd
        _ = P.p ω - Q.p ω := mul_one _
        _ ≤ max (P.p ω - Q.p ω) 0 := le_max_left _ _
    · calc (P.p ω - Q.p ω) * D ω ≤ 0 :=
            mul_nonpos_of_nonpos_of_nonneg hd (hD0 ω)
        _ ≤ max (P.p ω - Q.p ω) 0 := le_max_right _ _
  calc ∑ ω, (P.p ω * D ω - Q.p ω * D ω)
      ≤ ∑ ω, max (P.p ω - Q.p ω) 0 := Finset.sum_le_sum fun ω _ => hstep ω
    _ = P.tvDist Q := P.sum_posPart_eq_tvDist Q

end

end FinDist

/-- Two worlds sharing one advice: prefix laws `G` (following gains `δ`) and
`Bd` (following loses `Δ`), over a common baseline ratio `ρ_base`. -/
structure Scenario (Ω : Type*) [Fintype Ω] where
  /-- prefix law in the good world -/
  G : FinDist Ω
  /-- prefix law in the bad world -/
  Bd : FinDist Ω
  /-- the advice-free baseline ratio -/
  ρbase : ℝ
  /-- gain of following in the good world -/
  δ : ℝ
  /-- loss of following in the bad world -/
  Δ : ℝ
  δ_pos : 0 < δ
  Δ_pos : 0 < Δ

namespace Scenario

noncomputable section

variable {Ω : Type*} [Fintype Ω] (S : Scenario Ω) (D : Ω → ℝ)

/-- Algorithm value in the good world: follow with probability `D ω`. -/
def valueG : ℝ := S.ρbase + S.δ * S.G.expect D

/-- Algorithm value in the bad world. -/
def valueBd : ℝ := S.ρbase - S.Δ * S.Bd.expect D

/-- Fraction of the upside forgone in the good world. -/
def etaC : ℝ := 1 - (S.valueG D - S.ρbase) / S.δ

/-- Robustness loss in the bad world, as a fraction of `Δ`. -/
def etaR : ℝ := (S.ρbase - S.valueBd D) / S.Δ

lemma one_sub_etaC_eq : 1 - S.etaC D = S.G.expect D := by
  have hδ : S.δ ≠ 0 := S.δ_pos.ne'
  unfold etaC valueG
  field_simp
  ring

lemma etaR_eq : S.etaR D = S.Bd.expect D := by
  have hΔ : S.Δ ≠ 0 := S.Δ_pos.ne'
  unfold etaR valueBd
  field_simp
  ring

/-- **The master trade-off (Lemma 1), exact form**: for every decision rule
`D : Ω → [0,1]` — any measurable rule, since `Ω` is finite —
`(1 − η_c) ≤ η_r + TV(L_G, L_Bd)`. When the two worlds are indistinguishable
on the prefix (`TV → 0`), consistency and robustness cannot both hold. -/
theorem master_tradeoff (hD0 : ∀ ω, 0 ≤ D ω) (hD1 : ∀ ω, D ω ≤ 1) :
    1 - S.etaC D ≤ S.etaR D + S.G.tvDist S.Bd := by
  rw [S.one_sub_etaC_eq, S.etaR_eq]
  have h := S.G.expect_sub_le_tvDist S.Bd D hD0 hD1
  linarith

/-- Rearranged: the two losses are bounded below by `1 − TV`. -/
theorem etaC_add_etaR_ge (hD0 : ∀ ω, 0 ≤ D ω) (hD1 : ∀ ω, D ω ≤ 1) :
    1 - S.G.tvDist S.Bd ≤ S.etaC D + S.etaR D := by
  have h := S.master_tradeoff D hD0 hD1
  linarith

end

end Scenario

end BudgetStakes
