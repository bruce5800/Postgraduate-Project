# Direction A (learning-to-rank for matching) — M0–M3 verdict

**Status:** tested decisively across three experiments. **Verdict: the core premise
holds in principle but is practically inert on real features — Direction A does NOT
elevate to a standalone top-venue method.** This is an honest negative result; it is
cheap to have learned (three small experiments) and it *strengthens* the project's
central thesis rather than wasting the work.

## The arc

| Step | Question | Result |
|---|---|---|
| **M0** `run_rank_vs_mse_mve.py` | Does training-to-rank *ever* beat training-to-regress? | **YES, sharply** — with deliberately divergent synthetic features, rank-trained ratio 0.989 ≈ oracle vs MSE-trained 0.974, and rank-trained has *worse* MSE (87.6 vs 33.4) but better order (τ 0.058 vs 0.255). The mechanism exists. |
| **M1** `run_rank_when_it_matters.py` | When does it help, and how much? | Advantage = 0 at zero feature-divergence and on easy graphs (F3); grows with both — but **peak only +1.3% ratio** on synthetic graphs, because average-case matching is forgiving to order error. Gated by the floor→oracle gap. |
| **M3** `run_rank_real_trace.py` | Does the divergence arise with REAL features? | **NO.** On real temporal features (lagged induced degrees, Azure-LLM + Mooncake traces), **rank-training ≡ MSE-training**: identical order error (Kendall-τ 0.126 = 0.126) and identical matching ratio (both capture ~90% of the gap), across every topology/lag config tested. |

## Why M3 kills the standalone-method framing

The M0 advantage requires features where **order-accuracy and magnitude-accuracy
conflict** — one feature good for scale but wrong on order, another the reverse, so
the two training objectives pull to different predictors. Real temporal features
(a resource's reference counts over the last L windows) are **co-linear noisy
estimates of the same underlying popularity**: there is no order/magnitude conflict,
so MSE-training already recovers the order as well as rank-training. The dissociation
was a property of the *engineered* features, not of the *problem*.

Robustness (M3): tested deg ∈ {3,4,6,8}, n_res ∈ {300,400,500,600}, L ∈ {2,3,5}. In
**every** config the rank-advantage is within noise of zero (−0.0002 … +0.0005) and
τ_rank ≈ τ_mse to three decimals. The conclusion is not a gap artifact — it is that
the two objectives learn the same order from real features.

Two independent reasons the win evaporates, both tracing back to the project's own
findings:
1. **Real features don't diverge** (M3) — so the rank/MSE distinction never fires.
2. **The matching gap is small anyway** (M1 / F3) — even a perfect predictor only
   buys ~1–2% over the order-faithful baseline on average-case inputs.

## What this is worth (don't discard it)

This is a **clean, rigorous negative result** that belongs in the experimental paper
as a section, and it reinforces the central thesis:

> We tested whether *learning* the MPD predictor with a decision-aligned (rank) loss
> instead of regression improves online matching. It does **only** when the features
> induce an order/magnitude conflict; with realistic temporal features it does not —
> regression already yields an order-faithful predictor that captures most of the
> (small) achievable gap. Combined with F3, the practical message sharpens: on
> average-case matching, *neither a better algorithm nor a better-trained predictor
> buys much* — the value of predictions is robustness insurance, and a cheap
> order-faithful predictor is already enough to claim it.

## Implication for the publication strategy

- **Do NOT** invest M2 (decision-focused baseline) / M4 (the Kendall-τ bound) as a
  standalone method paper — the empirical payoff isn't there.
- **DO** fold M0–M3 into the experimental paper as a section ("Does learning the
  predictor help? A negative result") — it is honest, novel-in-the-negative, and
  thesis-reinforcing.
- The **other elevation directions remain open and do NOT depend on the
  rank-vs-MSE divergence** (see `docs/RESEARCH_PLAN_A.md` §"alternatives"):
  - **C** — recalibrated test-and-fallback *with a guarantee* + the irrevocability
    **lower bound** (formalise the Phase-3c §6 impossibility: "when the baseline is
    near-optimal no empirical-L1 threshold both captures the upside and stays safe").
    This is algorithm+theory, doesn't need feature divergence, and we already have
    the empirical mechanism.
  - **D** — online learning of the predictor across a sequence of instances, with a
    regret bound (a new *problem setting*, not a new result).
  - **B** alone — the tight Kendall-τ bound as a pure-theory contribution.

## Artifacts

- `scripts/run_rank_vs_mse_mve.py` → `results/rank_vs_mse_mve.png` (M0)
- `scripts/run_rank_when_it_matters.py` → `results/rank_when_it_matters.png` (M1)
- `scripts/run_rank_real_trace.py` → `results/rank_real_trace.png` (M3; Azure-LLM
  serving + real temporal features; Mooncake noted as unsuitable — prefix-cache
  structure has no balanced contention)
