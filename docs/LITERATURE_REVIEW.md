# Literature Review — Novelty / Prior-Art Audit

Adversarial prior-art review (deep multi-source search, 25 claims verified, 0
refuted, 20 primary sources). Goal: decide which findings are genuinely novel and
how to position the paper. **Verdict per question below; act on the recommendation.**

## Bottom line

The work **is publishable at an experimental-algorithms venue (ALENEX / ACM JEA /
SEA / ESA experimental track)** — *if positioned correctly*:

- **LEAD with** the **unified experimental benchmark** of learning-augmented
  online bipartite matching under a **common structured prediction-error model**
  (genuinely novel, unoccupied) + the **empirical test-and-fallback study**.
- **Reframe** the order-error result as "first to *empirically isolate and unify*
  order-error dependence across error structures" — NOT "we discovered order
  matters" (ACI's own appendix pre-empts that).
- **Demote** the AI-serving instantiation to an **application case-study**, not a
  novelty claim (the systems results are established; the with-predictions framing
  is new but risks a "repackaging" dismissal).

## Per-question verdicts

| Q | Topic | Verdict |
|---|---|---|
| Q1 | MPD performance ~ order-error (not magnitude) | **PARTIALLY-KNOWN, now precisely characterized** (action item 1 done — read ACI App. D + ran `run_order_vs_theory.py`). ACI Cor. D.2 *already* establishes order-dependence (loss ≤ `n−LIS`) and monotone-bias-zero. The genuinely-new, defensible part: ACI's `n−LIS` bound is **~20–75× loose** and **saturates** (≈n for any non-trivial error, so it can't distinguish structures), whereas **Kendall-τ predicts the realized loss** and the four error models collapse onto it. Frame as "empirical tightness + the right order measure", NOT "order matters". |
| Q2 | Unified experimental benchmark of LA online matching | **NOVEL (unoccupied) — BUILT (★2 done).** `scripts/run_unified_benchmark.py` + `docs/UNIFIED_BENCHMARK.md`: all three families on one harness with 95% CIs. Findings F1–F4 (robustness is engineered; structural vs adaptive mechanisms; naive followers crash below the floor; the combiner is dominated and exposes the irrevocability/hybrid penalty). Chłędowski combiner included as a benchmarked baseline, not claimed. |
| Q3a | stable prefix routing > reactive cache-affinity | **ALREADY-ESTABLISHED** — foundational across Preble, DualMap, Mooncake, llm-d. Re-derivation, not novel. |
| Q3b | real-time load > stale forecast | **PARTIALLY-KNOWN & COMPLICATED** — Mooncake shows reactive signals alone are *insufficient* (delayed → phase-staggering) and ADD prediction; SageServe shows forecasts WIN for provisioning. A blanket "real-time beats forecasts" headline is at risk. |
| Q3c | the *with-predictions framing* of serving routing | **NEW framing** — no serving paper uses "learning-augmented / algorithms-with-predictions" vocabulary — but high risk of "repackaging known systems results" dismissal. |
| Q4 | empirical study of the Choo/BEM test-and-fallback | **NOVEL (unoccupied)** — defined only theoretically; authors admit the Jiao et al. tester has no deployable implementation. Testing-cost / threshold-calibration / misjudgement-rate study is open and well-motivated. |
| Q5 | positioning | Lead with Q2 + Q4 (+ Q1 as demonstration); serving as case-study. Target ALENEX/JEA/SEA. Precedent template: Chłędowski et al. ICML 2021. |

## Key precedents / competition found

- **Chłędowski, Polak, Szabucki, Żołna (ICML 2021)** "Robust Learning-Augmented
  Caching: An Experimental Study" (arXiv:2106.14693) — the **direct format/venue
  template**: an experimental study of with-predictions algorithms (in caching).
  Also establishes that the **blind-follow-with-switching combiner** ("cheap
  worst-case insurance") is already known empirically → **benchmark it, don't
  claim it as new**.
- Primary matching papers confirmed single-algorithm / mostly-theoretical: ACI
  (2110.11439), Choo et al. (2405.09784), BEM (2511.23388).
- Serving prior art (the established systems results): Preble (2407.00023),
  Mooncake (2407.00079), DualMap (2602.06502), SageServe (2502.14617), SkyLB
  (2505.24095), llm-d blog.

## Action items before finalizing novelty framing

1. ~~Directly read ACI Appendix D~~ **DONE.** Cor. D.2 gives an *upper bound*
   (loss ≤ `n−LIS`), not a tight prediction. Empirically (`run_order_vs_theory.py`)
   the bound is ~20–75× loose and saturates; Kendall-τ is the predictive order
   measure. Lead the order-error result with "we characterize the bound's
   tightness/saturation and identify Kendall-τ as the governing order measure,
   unified across error structures" — and explicitly cite ACI Cor. D.2 for the
   order-dependence and monotone-zero results (do NOT claim those).
2. **Read Choo et al. Appendix E** — check whether their proof-of-concept already
   hints at the "worst-case threshold too lenient on average-case" observation
   (our recalibration finding). Not examined in this review.
3. **Monitor for a competing experimental follow-up** of Choo/BEM (fast-moving
   field; BEM is SOFSEM 2026, very recent).
4. ~~**Decide the serving angle**~~ **DONE — case study.** The SLO/tail-objective
   rescue was probed (`scripts/run_serving_slo_probe.py`, `docs/SERVING_SLO_PROBE.md`):
   across overload levels and uniform/bursty-HIGH regimes, a non-predictive policy
   (static headroom or reactive-adaptive) matches a clairvoyant oracle to within ≤3%
   — foresight does not help, so the SLO objective is forgiving too. Serving is
   presented as an application case study, not a with-predictions novelty claim.

## Caveats (from the review itself)

- Some serving evidence rests on a production blog (llm-d) and a recent preprint
  (DualMap) — weaker than peer-reviewed sources but corroborated by multiple
  independent systems papers.
- One non-load-bearing sub-claim ("Choo et al. source code released") could not be
  verified — do not assume their code exists.
- The order-error verdict was assessed from the ACI abstract + claim set, not a
  line-by-line read of Appendix D — hence action item 1.
- Our own empirical results (the 4-model collapse, zero-effect of monotone bias)
  were not independently verifiable here; their novelty depends on no prior
  unification existing, which the search supports but cannot prove exhaustively.

*Full run: 103 agents, 563 tool calls, 25/25 claims confirmed, 20 primary sources.*
