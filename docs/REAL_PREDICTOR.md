# Real-Predictor Study — external validity (does a cheap real predictor pay off?)

**Status:** complete. Answers the sharpest external-validity question for the whole
project: every other experiment injects *synthetic* prediction error via a knob η; a
real predictor sits at ONE fixed quality point, costs something to compute, and — per
unified-benchmark finding F3 — the consistency upside on average-case inputs is
small. So is the realized benefit even smaller, and worth the cost?

**Method (no synthetic perturbation anywhere).** The predictor is the cheapest,
most realistic one possible: **last-window historical statistics**. Real Wikipedia
daily pageviews give a live day (2024-06-15 = truth) and earlier days
(1/7/30-day-stale = the predictor); forecast error is genuine temporal drift. We
map the trace onto a fixed serving topology (200 request types, 600 resources,
deg 6, m=600, cap-1) and measure both algorithm families. Driver:
`scripts/run_real_predictor.py` (~15 s, 30 trials, 95% CIs in the JSON).

## 1. Results

| staleness | histogram L1 drift | **histogram order-err (Kτ)** | **induced μ order-err (Kτ)** | MPD base | MPD real | MPD oracle | **gap-capture** | Follow (blind) |
|---|---|---|---|---|---|---|---|---|
| 1 day  | 0.69 | 0.383 | **0.189** (−51%) | 0.923 | 0.957 | 0.973 | **68 %** | 0.677 |
| 7 days | 1.14 | 0.449 | **0.271** (−40%) | 0.925 | 0.948 | 0.973 | **47 %** | 0.481 |
| 30 days| 1.39 | 0.485 | **0.315** (−35%) | 0.925 | 0.938 | 0.975 | **27 %** | 0.356 |

Ceiling (MinDegree, realized degrees) ≈ 0.986 throughout. *gap-capture =
(MPD_real − base)/(MPD_oracle − base).* Figure: `results/real_predictor.png`.

**Cost per instance:** predictor build **0.108 ms** = **2.1 % of OPT** (Hopcroft–Karp
5.13 ms), 25 % of one online matching pass.

## 2. What it says — three honest answers to "is it worth it?"

**A. Cost: the premise mostly doesn't bite here.** For this problem class the
predictor is a **linear-time count** (μ = A·p over historical frequencies), not an ML
inference — 0.1 ms, 2 % of the cost of computing OPT once. There is no expensive
model to amortize. (If one *did* bolt on a heavy learned forecaster, §C explains why
it would have almost nothing to add.)

**B. Benefit: real, partial, decaying — and never harmful (for MPD).** A stale
historical degree forecast captures **27–68 %** of the achievable oracle gap,
shrinking with staleness, and **always stays above the forecast-free baseline**
(0.938–0.957 vs 0.923–0.925, even at 30 days). So the user's intuition is right that
the realized benefit is *smaller* than the synthetic-sweep peak — but it is positive
and bounded-below by the baseline, because the robust route never crashes.

**C. Why MPD survives real drift while blind histogram-following collapses.** The
same stale forecast that lets MPD capture 27–68 % of the gap is **catastrophic for
the raw type-histogram route**: `FollowPrediction` collapses to 0.68 → 0.36, far
*below* the 0.92 baseline. The reason is the project's order-error finding (★1, ACI
App. D) made concrete on real data:

> The degree predictor μ = A·p **aggregates** the traffic distribution through the
> topology. Per-resource averaging **smooths the drift**: the histogram's order error
> is Kτ 0.38–0.49, but the induced degree predictor's is only **0.19–0.32 (~halved)**.
> Since MPD depends on the predictor only through its *order* (★1), the cheap,
> aggregated, order-faithful degree predictor is exactly the robust way to consume a
> noisy real forecast — whereas following the raw histogram directly exposes the full
> drift. A heavier ML forecaster would have to beat an order error that is already low
> *because of the topology, not the predictor* — little room left to pay for.

**D. The robust algorithms behave as advertised on real drift, too.** Feeding the same
stale histogram to the adaptive/robust type-advice algorithms: the **Combiner** holds
the baseline (0.925) at every staleness (never crashes), while **TestAndMatch** sits
between blind-follow and baseline (0.86 → 0.73) and *degrades* with staleness — its
worst-case-calibrated threshold lets progressively-staler advice through. That is the
Phase 3c "threshold too lenient" / recalibration finding (`PHASE3C_REPORT.md` §5–6)
reproduced on real data, and a concrete case where the simple robust-tuned combiner
beats the test-and-fallback.

## 3. Bottom line for the thesis

This converts the "synthetic error" critique into a positive, quantified result:

> A realistic predictor here is a **near-free historical count** (2 % of OPT cost),
> not an ML model. Consumed through the **degree-prediction route**, a stale real
> forecast captures **27–68 %** of the achievable gap and **never drops below the
> forecast-free baseline**, because topology aggregation makes the cheap predictor
> *order-faithful* (the quantity ★1 showed governs the loss). Consumed naively
> through the **raw histogram**, the identical forecast is catastrophic (0.36–0.68) —
> which is exactly what the robust algorithms (Combiner, test-and-fallback) are for.
> Net: the benefit is modest and decays with staleness, but the cost is negligible
> and the downside is capped — so on structured inputs the realistic predictor *is*
> worth it, and on easy inputs (F3) there is simply little to win or lose either way.

## 4. Limitations

- One trace (Wikipedia top-articles) and one fixed topology family. The same study on
  the Azure-LLM / Mooncake traces would test universality (natural extension).
- cap-1 matching for comparability with the unified benchmark and ★1; the serving
  b-matching version (`run_serving_trace.py`) is the capacity-c companion.
- "Oracle forecast" = expected degrees under true live traffic; "ceiling" = realized
  degrees (MinDegree). gap-capture is reported against the former (the best a
  *traffic* predictor could do), not the latter.
