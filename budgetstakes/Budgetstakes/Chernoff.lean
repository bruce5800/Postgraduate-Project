/-
Copyright (c) 2026 Zhuolun Li. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Zhuolun Li
-/
import Budgetstakes.MasterTradeoff

/-!
# Stage 4: concentration for the directional statistic (Theorem 1(ii), weak form)

A fully self-contained finite Chernoff bound: for i.i.d. draws from a finite
distribution `P` and a score `c : Ω → [−1,1]` with mean `μ = E_P[c] > 0`,

  `P^k ( ∑ i, c (x i) ≤ 0 ) ≤ exp (−k μ² / 4)`.

Applied to the directional statistic (where `μ = 2·stakes` by Stage 1's payoff
identity) this is the achievability half of the budget–stakes law in its
Hoeffding-weak form: the constant is `1/4` and the variance is bounded by `1`
rather than by the specialist mass `σ²` — the `σ²`-sharp version awaits a
Bernstein-type bound (Stage 6).

Design: no measure theory. Independence enters through exactly one
combinatorial identity, `sum_prod_eq_pow`
(`∑ x : Fin k → Ω, ∏ i, g (x i) = (∑ ω, g ω)^k`), proved by induction; the
pointwise MGF bound is `e^y ≤ 1 + y + y²` for `|y| ≤ 1`
(`Real.abs_exp_sub_one_sub_le`), and the tilt is fixed at `t = μ/2`.
-/

namespace BudgetStakes

open scoped Classical

/-- Sums of products over function spaces factorize:
`∑ x : Fin k → Ω, ∏ i, g (x i) = (∑ ω, g ω)^k`. This single identity carries
all the independence used in Stage 4. -/
lemma sum_prod_eq_pow {Ω : Type*} [Fintype Ω] (g : Ω → ℝ) (k : ℕ) :
    (∑ x : Fin k → Ω, ∏ i, g (x i)) = (∑ ω, g ω) ^ k := by
  calc (∑ x : Fin k → Ω, ∏ i, g (x i))
      = ∑ x ∈ Fintype.piFinset (fun _ : Fin k => (Finset.univ : Finset Ω)),
          ∏ i, g (x i) := by rw [Fintype.piFinset_univ]
    _ = ∏ _i : Fin k, ∑ ω, g ω :=
        (Finset.prod_univ_sum (fun _ : Fin k => (Finset.univ : Finset Ω))
          (fun _ ω => g ω)).symm
    _ = (∑ ω, g ω) ^ k := by
        rw [Finset.prod_const, Finset.card_univ, Fintype.card_fin]

namespace FinDist

noncomputable section

variable {Ω : Type*} [Fintype Ω] (P : FinDist Ω)

/-- Probability of an event. -/
def prob (φ : Ω → Prop) : ℝ := ∑ ω, if φ ω then P.p ω else 0

lemma prob_congr {φ ψ : Ω → Prop} (h : ∀ ω, φ ω ↔ ψ ω) : P.prob φ = P.prob ψ := by
  unfold prob
  exact Finset.sum_congr rfl fun ω _ => by rw [if_congr (h ω) rfl rfl]

lemma expect_nonneg {f : Ω → ℝ} (hf : ∀ ω, 0 ≤ f ω) : 0 ≤ P.expect f :=
  Finset.sum_nonneg fun ω _ => mul_nonneg (P.nonneg ω) (hf ω)

lemma expect_mono {f g : Ω → ℝ} (h : ∀ ω, f ω ≤ g ω) : P.expect f ≤ P.expect g :=
  Finset.sum_le_sum fun ω _ => mul_le_mul_of_nonneg_left (h ω) (P.nonneg ω)

lemma expect_affine (a b : ℝ) (f : Ω → ℝ) :
    P.expect (fun ω => a + b * f ω) = a + b * P.expect f := by
  unfold expect
  have h : ∀ ω : Ω, P.p ω * (a + b * f ω) = a * P.p ω + b * (P.p ω * f ω) := by
    intro ω
    ring
  simp_rw [h]
  rw [Finset.sum_add_distrib, ← Finset.mul_sum, ← Finset.mul_sum, P.sum_one, mul_one]

lemma expect_neg (f : Ω → ℝ) : P.expect (fun ω => -f ω) = -P.expect f := by
  unfold expect
  rw [← Finset.sum_neg_distrib]
  exact Finset.sum_congr rfl fun ω _ => by ring

lemma expect_le_one {f : Ω → ℝ} (hf : ∀ ω, f ω ≤ 1) : P.expect f ≤ 1 := by
  have h := P.expect_mono (g := fun _ => 1) hf
  calc P.expect f ≤ P.expect (fun _ => 1) := h
    _ = 1 := by
        unfold expect
        simp [P.sum_one]

/-- The `k`-fold product (i.i.d. prefix) distribution. -/
def iid (k : ℕ) : FinDist (Fin k → Ω) where
  p := fun x => ∏ i, P.p (x i)
  nonneg := fun x => Finset.prod_nonneg fun i _ => P.nonneg _
  sum_one := by rw [sum_prod_eq_pow, P.sum_one, one_pow]

/-- **Finite Chernoff, lower tail** (the achievability engine of Theorem 1(ii)):
a score with `|c| ≤ 1` and positive mean `μ` has
`P^k(∑ c ≤ 0) ≤ exp(−k μ²/4)`. -/
theorem iid_prob_sum_nonpos_le (c : Ω → ℝ)
    (hc : ∀ ω, |c ω| ≤ 1) (hμ : 0 < P.expect c) (k : ℕ) :
    (P.iid k).prob (fun x => (∑ i, c (x i)) ≤ 0)
      ≤ Real.exp (-(k : ℝ) * (P.expect c) ^ 2 / 4) := by
  set μ := P.expect c with hμdef
  set t := μ / 2 with ht
  have hμ1 : μ ≤ 1 := P.expect_le_one fun ω => (abs_le.mp (hc ω)).2
  have ht0 : 0 < t := by positivity
  have ht1 : t ≤ 1 / 2 := by rw [ht]; linarith
  -- Step 1: indicator ≤ exponential tilt, pointwise in the prefix.
  have step1 : (P.iid k).prob (fun x => (∑ i, c (x i)) ≤ 0)
      ≤ ∑ x : Fin k → Ω, (P.iid k).p x * Real.exp (-t * ∑ i, c (x i)) := by
    unfold prob
    apply Finset.sum_le_sum
    intro x _
    by_cases hx : (∑ i, c (x i)) ≤ 0
    · rw [if_pos hx]
      have h1 : (1 : ℝ) ≤ Real.exp (-t * ∑ i, c (x i)) := by
        have hy : 0 ≤ -t * ∑ i, c (x i) := by
          have hrw : -t * (∑ i, c (x i)) = t * (-(∑ i, c (x i))) := by ring
          rw [hrw]
          exact mul_nonneg ht0.le (by linarith)
        linarith [Real.add_one_le_exp (-t * ∑ i, c (x i))]
      calc (P.iid k).p x = (P.iid k).p x * 1 := (mul_one _).symm
        _ ≤ _ := mul_le_mul_of_nonneg_left h1 ((P.iid k).nonneg x)
    · rw [if_neg hx]
      exact mul_nonneg ((P.iid k).nonneg x) (Real.exp_pos _).le
  -- Step 2: the tilted sum factorizes into a k-th power.
  have step2 : (∑ x : Fin k → Ω, (P.iid k).p x * Real.exp (-t * ∑ i, c (x i)))
      = (P.expect (fun ω => Real.exp (-t * c ω))) ^ k := by
    have hfac : ∀ x : Fin k → Ω,
        (P.iid k).p x * Real.exp (-t * ∑ i, c (x i))
          = ∏ i, (P.p (x i) * Real.exp (-t * c (x i))) := by
      intro x
      show (∏ i, P.p (x i)) * Real.exp (-t * ∑ i, c (x i)) = _
      rw [Finset.mul_sum, Real.exp_sum, Finset.prod_mul_distrib]
    simp_rw [hfac]
    rw [sum_prod_eq_pow (fun ω => P.p ω * Real.exp (-t * c ω)) k]
    rfl
  -- Step 3: per-factor MGF bound at the tilt t = μ/2.
  have step3 : P.expect (fun ω => Real.exp (-t * c ω)) ≤ Real.exp (-μ ^ 2 / 4) := by
    have hpt : ∀ ω, Real.exp (-t * c ω) ≤ 1 + (-t * c ω) + t ^ 2 := by
      intro ω
      set y := -t * c ω with hy
      have hyabs : |y| ≤ 1 := by
        rw [hy, abs_mul, abs_neg]
        have h1 : |t| = t := abs_of_pos ht0
        have h2 := hc ω
        calc |t| * |c ω| ≤ |t| * 1 :=
              mul_le_mul_of_nonneg_left h2 (abs_nonneg t)
          _ = t := by rw [mul_one, h1]
          _ ≤ 1 := by linarith
      have hb := Real.abs_exp_sub_one_sub_id_le hyabs
      have hy2 : y ^ 2 ≤ t ^ 2 := by
        have h2 := abs_le.mp (hc ω)
        have hc2 : c ω ^ 2 ≤ 1 := by nlinarith [h2.1, h2.2]
        have hexp : y ^ 2 = t ^ 2 * c ω ^ 2 := by rw [hy]; ring
        rw [hexp]
        calc t ^ 2 * c ω ^ 2 ≤ t ^ 2 * 1 :=
              mul_le_mul_of_nonneg_left hc2 (sq_nonneg t)
          _ = t ^ 2 := mul_one _
      have := abs_le.mp hb
      nlinarith [this.2]
    calc P.expect (fun ω => Real.exp (-t * c ω))
        ≤ P.expect (fun ω => (1 + t ^ 2) + (-t) * c ω) := by
          apply P.expect_mono
          intro ω
          have := hpt ω
          linarith
      _ = (1 + t ^ 2) + (-t) * μ := P.expect_affine _ _ _
      _ ≤ Real.exp ((-t) * μ + t ^ 2) := by
          have := Real.add_one_le_exp ((-t) * μ + t ^ 2)
          linarith
      _ = Real.exp (-μ ^ 2 / 4) := by
          congr 1
          rw [ht]
          ring
  -- Step 4: assemble.
  have hB0 : 0 ≤ P.expect (fun ω => Real.exp (-t * c ω)) :=
    P.expect_nonneg fun ω => (Real.exp_pos _).le
  calc (P.iid k).prob (fun x => (∑ i, c (x i)) ≤ 0)
      ≤ (P.expect (fun ω => Real.exp (-t * c ω))) ^ k := by
        rw [← step2]; exact step1
    _ ≤ (Real.exp (-μ ^ 2 / 4)) ^ k := by gcongr
    _ = Real.exp (-(k : ℝ) * μ ^ 2 / 4) := by
        rw [← Real.exp_nat_mul]
        congr 1
        ring

/-- **Finite Chernoff, upper tail**: a score with negative mean concentrates
below zero — the bad-world error of the directional test. -/
theorem iid_prob_sum_nonneg_le (c : Ω → ℝ)
    (hc : ∀ ω, |c ω| ≤ 1) (hμ : P.expect c < 0) (k : ℕ) :
    (P.iid k).prob (fun x => 0 ≤ ∑ i, c (x i))
      ≤ Real.exp (-(k : ℝ) * (P.expect c) ^ 2 / 4) := by
  have hneg : 0 < P.expect (fun ω => -c ω) := by
    rw [P.expect_neg]; linarith
  have hcn : ∀ ω, |(-c ·) ω| ≤ 1 := fun ω => by
    simpa [abs_neg] using hc ω
  have h := P.iid_prob_sum_nonpos_le (fun ω => -c ω) hcn hneg k
  have hev : ∀ x : Fin k → Ω,
      ((∑ i, -c (x i)) ≤ 0) ↔ (0 ≤ ∑ i, c (x i)) := by
    intro x
    rw [Finset.sum_neg_distrib]
    constructor <;> intro <;> linarith
  rw [(P.iid k).prob_congr hev] at h
  have hsq : (P.expect (fun ω => -c ω)) ^ 2 = (P.expect c) ^ 2 := by
    rw [P.expect_neg]; ring
  rwa [hsq] at h

end

end FinDist

end BudgetStakes
