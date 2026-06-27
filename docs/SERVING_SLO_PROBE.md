# Serving SLO probe — can predictions rescue serving? (verdict: no)

**Status:** done. Tests whether the serving instantiation can be lifted from
"application case study" to a genuine *with-predictions* result by switching from the
throughput objective (known to be forgiving — finding F3) to an **SLO / tail
objective**, where a reactive baseline *might* be far from optimal. **Verdict:
negative — the SLO objective is also forgiving; serving stays a case study.**

**Driver:** `scripts/run_serving_slo_probe.py` (event-driven, ~1 s).

## Setup

Event-driven serving with real service durations. Requests carry an SLO **class**:
HIGH (a drop = an SLO violation) or LOW (best-effort). Arrivals are bursty and
non-stationary (periodic bursts on a hot type-set), in an **intermittent-overload**
regime (off-peak uncontended, bursts overload). Objective: a joint
**COST = HIGH-violation-rate + 0.3·LOW-drop-rate** — a policy must protect HIGH
during bursts *without* needlessly dropping LOW off-peak.

All policies prioritise HIGH; they differ only in how they **reserve** capacity:
- **reactive** (reserve 0) — greedy, no reservation.
- **static-reserve R** — always keep R slots free for HIGH (best non-predictive
  *static* policy; we sweep R).
- **reactive-adaptive** — reserve per resource the HIGH demand *observed in the recent
  trailing window* (reacts to load, no foresight) — the strong non-predictive baseline.
- **clairvoyant** — reserve the *actual upcoming* HIGH demand within a horizon
  (perfect future knowledge) — the upper bound on what any burst predictor could do.

If clairvoyant ≪ the best non-predictive policy → a prediction gap exists. If they
tie → reacting to observed load is as good as forecasting → no rescue.

## Result (representative; the gap is ≤3% across every regime swept)

Bursty-HIGH regime (the *most* prediction-favourable: tight-SLO demand itself spikes):

| policy | HIGH-viol | LOW-drop | COST |
|---|---:|---:|---:|
| reactive | 0.261 | 0.135 | 0.301 |
| static-reserve=1 | 0.097 | 0.350 | 0.202 |
| **reactive-adaptive** | 0.082 | 0.399 | **0.202** |
| **clairvoyant (oracle)** | 0.075 | 0.402 | **0.196** |

**GAP (best non-predictive − clairvoyant) = 0.006 (3% relative).** In the
uniform-HIGH regime a trivial **static reserve of 1 slot** drove HIGH violations to
**0.001** and *beat* the clairvoyant outright (negative gap). Across heavy overload,
moderate overload, uniform-HIGH and bursty-HIGH, the foresight gap was always ≤3% and
often negative.

## Why serving is forgiving even on the tail objective

Two independent reasons, both robust to the sweep:
1. **Protecting a tight-SLO minority needs only a small static headroom.** Reserving
   one slot per resource for HIGH already nearly eliminates violations — no forecast
   required.
2. **Bursts are persistent, so reacting ≈ forecasting.** By the time a burst is
   underway, the reactive-adaptive policy observes the rising HIGH load and reserves;
   because bursts last longer than the reaction lag, foresight only saves the very
   onset. `reactive-adaptive ≈ clairvoyant` confirms it.

This is the same wall the project keeps hitting (F3 / M1 / M3), now on a third
objective: **a simple non-predictive policy is near-optimal; predictions are
robustness insurance, not a performance lever.**

## Decision (closes LITERATURE_REVIEW action item 4)

Serving is presented as an **application case study**, not a with-predictions novelty
claim. The probe is the evidence that we *looked* for a rescuing regime (tail/SLO
under bursts, vs a reactive-adaptive baseline) and did not find one — which is itself
worth a sentence in the paper, and reinforces the central thesis rather than
contradicting it.

**Caveat (honest):** "no rescue" means no *natural* regime in the sweep gave a >15%
foresight gap; an exotic hand-tuned corner might, but a result that appears only
under fine-tuning is not an actionable serving conclusion.
