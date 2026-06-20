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

- **Synthetic workload.** Topology and traffic are synthetic (Zipfian); a real
  serving / MoE-routing / request trace would harden the finding (the planned
  "real trace" depth was not taken in this increment).
- **MPD under capacity** is implemented (`greedy_with_capacity` with a degree
  rank) but not swept here; a capacity × order-error study would extend Phase 3a.
- **Free-disposal / weighted variants** (top-c rewards, request values) are
  natural serving extensions not modeled.

## 6. Reproducibility

```bash
python3 tests/test_serving_small.py     # 5 tests
python3 scripts/run_serving.py          # ~8s; capacity × forecast-error grid
```
Seed 0; outputs `results/serving.json`, `results/serving_cliff.png`,
`results/serving_envelope.png`.
