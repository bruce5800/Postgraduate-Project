# Phase 4 Report — AI Inference Serving Instantiation (online b-matching)

**Status:** complete. A faithful domain instantiation of the whole framework —
online bipartite matching with predictions, recast as request routing in an
inference serving system, with resource **capacity c** (b-matching) and a
**non-uniform traffic distribution** whose forecast is the "advice".

## 1. The instantiation (and why it is faithful, not a relabel)

| Abstract | Serving |
|---|---|
| offline node r | serving resource (MoE expert / model replica / cache shard), **capacity c** |
| online type ℓ | request type (prompt category / token class) |
| edge (ℓ, r) | resource r can serve request-type ℓ (capability / cache affinity) |
| traffic distribution p | the live request mix (**Zipfian** head/tail traffic) |
| advice ĉ (type histogram) | a **traffic forecast**; a bad forecast is a **stale / drifted** one |
| matching size / OPT | goodput = served requests / best possible |

Two things make this genuine rather than cosmetic:
1. **Traffic is non-uniform.** The original Choo/BEM setting had a uniform type
   distribution; here p is Zipfian, so the predicted type histogram is *literally*
   a traffic forecast and "bad advice" is a realistic stale forecast — the natural
   error mode in serving. (We extended `sample_instance` with a `p` argument.)
2. **Capacity c (b-matching).** Real resources serve many requests, not one. We
   added `optimal.max_b_matching_size` (compressed max-flow) and capacity-aware
   online algorithms (`algorithms/capacity.py`): a `load[r]` counter replaces the
   boolean `matched[r]`, generalizing the entire family (greedy / Ranking / MPD /
   FollowPrediction / TestAndMatch).

## 2. What was built

| Component | File |
|---|---|
| Traffic-distribution sampling | `iid_sampler.sample_instance(..., p=)` |
| Serving topology (Zipfian traffic, sparse capability) | `graphs/serving.py` |
| b-matching OPT (capacity c) | `optimal.max_b_matching_size` |
| Capacity-aware greedy/Ranking/MPD, FollowPrediction, TestAndMatch | `algorithms/capacity.py` |
| Tests (5) | `tests/test_serving_small.py` |
| Experiment | `scripts/run_serving.py` |

**Verified anchors (tests):** b-matching at c=1 equals ordinary matching; OPT
grows monotonically with capacity (saturating at #requests); perfect forecast →
advice b-matching = OPT at every capacity; garbage forecast → TestAndMatch detects
it and stays robust under capacity.

## 3. The domain finding — capacity is the safe substitute for a forecast

![serving capacity](../results/serving_cliff.png)

n_resources=200, n_types=40, deg=8, 800 requests, Zipf traffic, 25 trials.
Goodput under a **garbage forecast** (forecast error L1≈1.4) as capacity grows:

| capacity c | blindly follow forecast | TestAndMatch (adaptive) | forecast-free baseline |
|---:|---:|---:|---:|
| 1 | 0.773 | 0.995 | 0.998 |
| 2 | 0.593 | 0.964 | 0.974 |
| 4 | 0.471 | 0.935 | 0.965 |
| 8 | 0.401 | 0.949 | 0.988 |
| 16 | 0.348 | 0.949 | 0.995 |

Three things, and they invert the naive intuition that "more capacity ⇒ less need
for smart routing":

1. **The forecast-free baseline is near-optimal at every capacity** (0.96–1.00).
   Capacity is robustness you get for free — a simple greedy router barely leaves
   anything on the table.
2. **Blindly trusting a stale forecast is catastrophic, and the catastrophe
   *deepens* with capacity** (goodput 0.77 → 0.35). In competitive-ratio terms,
   capacity raises OPT, but routing to the wrong (forecast-implied) resources does
   not capture it — so the *relative* loss grows.
3. **The adaptive test-and-fallback stays robust at every capacity** (within ~0.05
   of the baseline), so its protective value — the gap to blind trust — **grows
   with capacity** (from +0.22 at c=1 to +0.60 at c=16).

![serving envelope](../results/serving_envelope.png)

The forecast-error envelope makes the same point: at tight capacity (c=1) blind
trust crashes only mildly (to 0.77), but at ample capacity (c=8) it crashes far
deeper (to 0.40), while the adaptive curve stays flat at ~0.99 in both.

**Serving takeaway.** In a well-provisioned serving system a forecast-free policy
is already near-optimal; the real operational risk is a routing layer that blindly
trusts a stale traffic forecast — and that risk is *largest* precisely when you
have ample capacity. The cheap prefix test is exactly the guard against it.

## 3b. Real-trace hardening — forecast staleness on Wikipedia traffic

`scripts/run_serving_trace.py` replaces the synthetic forecast perturbation with a
**real** one. The workload is real Wikipedia daily pageviews (`data/trace/wiki/`,
fetched from the Wikimedia API): the live day (2024-06-15) is the request stream,
and an **earlier day's distribution is the forecast**. Forecast error is then real
temporal drift — the older the forecast, the staler it is. No synthetic noise
anywhere. (Mapping: pages = request types, cache shards = resources, a cache hit =
a match, "predict today's hot pages from an old day" = the traffic forecast.)

The real drift is monotone in staleness, over 500 request types:

| forecast staleness | real drift L1(p_live, q) |
|---|---:|
| 1 day | 0.68 |
| 7 days | 1.16 |
| 30 days | 1.41 |

![serving real trace](../results/serving_trace.png)

Goodput under the real stale forecast (M=3000 requests, 20 trials):

| staleness | blind (c=2) | blind (c=8) | adaptive | baseline |
|---|---:|---:|---:|---:|
| 1 day | 0.712 | 0.628 | ~1.00 | ~1.00 |
| 7 days | 0.641 | 0.411 | ~1.00 | ~1.00 |
| 30 days | 0.577 | 0.302 | ~1.00 | ~1.00 |

The synthetic Phase-4 findings reproduce on real data, with a real error axis:
- **the staler the forecast, the worse blind trust does** (0.71 → 0.58 at c=2;
  0.63 → 0.30 at c=8) — monotone in real drift;
- **the cliff deepens with capacity** (c=8 worse than c=2 at every staleness);
- **the adaptive test-and-fallback stays robust at every staleness** (~1.00),
  and the forecast-free baseline is near-optimal throughout.

Because the error is genuine temporal drift on a recognizable real workload (the
live day's top pages are real time-sensitive events — UEFA Euro 2024, Inside Out
2, etc.), this answers the "synthetic only" objection directly.

## 4. How this strengthens the thesis

This is the applied face of the project's unifying thesis. Phase 2 (Borodin):
simple greedy ≈ complex on average-case. Phase 3a: predictions help only on skewed
structure; the advice-free baseline is the floor. Phase 3c: the value of advice is
robustness-insurance, not consistency lift. Phase 4 lands it in a concrete,
current domain: **for inference serving, capacity is the safe substitute for a
forecast, and the one thing you must not do is trust a stale forecast blindly —
which a sublinear test cheaply prevents.** That is a crisp, citable systems message
that the abstract findings alone do not deliver.

## 5. Limitations / next

- **Topology is synthetic.** Traffic *and the forecast error* are now real
  (Wikipedia pageviews + temporal drift, §3b); the resource topology (which shard
  serves which page) remains a synthetic cache-placement choice — a real cache
  layout would close the last gap.
- **MPD under capacity** is implemented (`greedy_with_capacity` with a degree
  rank) but not swept here; a capacity × order-error study would extend Phase 3a.
- **Free-disposal / weighted variants** (top-c rewards, request values) are
  natural serving extensions not modeled.

## 6. Reproducibility

```bash
python3 tests/test_serving_small.py        # 5 tests
python3 scripts/run_serving.py             # ~8s; synthetic capacity × forecast-error
python3 scripts/run_serving_trace.py       # ~9s; real Wikipedia trace, forecast staleness
```
Seed 0; outputs `results/serving*.{json,png}`. The Wikipedia pageview JSONs are
cached in `data/trace/wiki/` (committed, ~230 KB); to refresh, re-fetch the
Wikimedia "top articles per day" REST endpoint for the dates in
`scripts/run_serving_trace.py`.
