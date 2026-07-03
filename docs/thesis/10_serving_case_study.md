<!--
Thesis Ch 10 — AI-Inference Serving Case Study. Adapted from paper/07 §8 + PHASE4_SERVING_REPORT.md.
Slightly fuller than the paper (thesis affords a chapter). Guardrail: case study, NOT a novelty
claim; the SLO-probe negative is in Ch 8, referenced here. Cross-refs to chapters.
-->

# Chapter 10. Application Case Study: AI-Inference Serving

The thesis's abstraction is not confined to classical matching markets; it instantiates a
contemporary systems problem. This chapter casts request routing in an AI-inference serving
system as online matching and shows the framework recovers the field's established results.
It is presented, deliberately, as a **case study, not a novelty claim** — the systems facts
below are known, and the with-predictions vocabulary is a re-labeling of them (a decision
justified by the literature review of Chapter 8 and the negative probe summarized in §10.2).

## 10.1 The serving instantiation

We map serving to online $b$-matching: the offline resources are model replicas or cache
shards, each with a **capacity** $c$ (it can serve up to $c$ concurrent requests, hence
$b$-matching rather than $1$-matching); arrivals are requests drawn from a non-uniform,
bursty traffic distribution over request types; an edge is a capability or cache affinity;
and **goodput** — the fraction of requests served — is the competitive ratio against the
$b$-matching optimum. We instantiate this on three real traces (Wikipedia pageviews, an
Azure LLM inference trace, and the Mooncake prefix-cache trace) and across four serving
concerns.

- **Capacity as robustness.** Increasing the capacity $c$ smooths the effect of a bad
  prediction: a capacity-aware baseline stays safe, while *blindly* trusting a traffic
  forecast degrades *further* as capacity grows. Capacity is thus a *substitute* for
  algorithmic robustness — the systems analogue of the robustness-insurance thesis.
- **Forecasts vs live load.** Under dynamic service times (requests hold a slot for a real
  duration, released event-by-event), a live-load signal beats a stale traffic forecast — a
  reactive load balancer outperforms a forecast-following router when the forecast has aged.
- **Cache-affinity routing.** For prefix-cache-aware routing, a *stable* affinity router
  beats a reactive one — the reverse of the traffic-forecast case, because cache locality
  rewards persistence.

Each of these recovers an established systems result cleanly, demonstrating that the
framework instantiates the problem faithfully.

## 10.2 A probe for a genuinely new result, and its negative

Because the literature suggested the with-predictions lens might yield a *new* actionable
serving result on a tail objective, we probed it (the full account is in Chapter 8). On an
SLO/tail objective — protecting a tight-SLO class of requests under bursty load — a
non-predictive policy (static headroom, or a reactive-adaptive reservation based on observed
load) matches a clairvoyant oracle to within $\le 3\%$ across every regime swept; a trivial
static reservation of one slot even beats the oracle in the moderate regime. Two reasons,
both robust: protecting a tight-SLO minority needs only a small static headroom, no forecast;
and bursts are persistent enough that reacting to observed load is nearly as good as
forecasting it. The tail objective is forgiving too — a third face of the thesis's wall,
after throughput (Chapters 4–7) and predictor-learning (Chapter 8). We found no natural
regime where foresight helps, so serving remains a case study.

## 10.3 Chapter summary

The serving instantiation shows the framework reaches a live systems problem and recovers its
established results — capacity as a robustness substitute, live load over stale forecasts,
stability for cache locality — and that even a tail objective does not open a genuine
with-predictions win. The application is a faithful case study of the thesis, not an
independent contribution.
