<!--
Draft §6 — external validity (C2 support). Numbers:
 §6.1 real predictor: scripts/run_real_predictor.py (Wikipedia), docs/REAL_PREDICTOR.md.
      staleness 1/7/30d: hist-Kτ .38/.45/.49 → induced μ-Kτ .19/.27/.32; MPD base .923/.925/.925,
      real .957/.948/.938, oracle .973/.973/.975; gap-capture 68/47/27%; Follow .68/.48/.36;
      cost 0.108ms = 2.1% of OPT. Figure 5 = real_predictor.png.
 §6.2 six real graphs: scripts/run_realworld_robustness.py, docs/REALWORLD_ROBUSTNESS.md.
      F1 6/6; F3 mean +.049, smallest on econ; F2 clean social/bio, partial 2 econ; F4 dramatic.
      Figure 6 = realworld_robustness.png.
 §6.3 learning negative (M0–M3): docs/RANK_LEARNING_M0_M3.md. rank≡MSE on real features (τ .126=.126).
Guardrails: F2 "qualitatively 6/6, strictly 4/6" (don't round up); learning result is an honest negative.
-->

# 6. External Validity

Sections 3–5 are on synthetic graphs with a synthetic error knob. Is the picture real? We
stress it three ways: a genuine, cheap predictor on a real request trace (§6.1); the six
real-world graphs (§6.2); and whether *learning* the predictor changes anything (§6.3).

## 6.1 A real, cheap predictor

We replace the synthetic error knob with the cheapest realistic predictor: last-window
historical statistics. Real Wikipedia daily pageviews give a live day (the truth) and
earlier days (a 1-, 7-, or 30-day-stale forecast), so the prediction error is genuine
temporal drift; we map the trace onto a fixed serving topology and consume the forecast
through the degree route (MPD) (**Figure 5**; `docs/REAL_PREDICTOR.md`).

Three facts emerge, all favorable and all honest. First, **the cost premise does not
bite**: the predictor is a linear-time count ($\mu = A\,p$ over historical frequencies),
$0.108$ ms per instance — about $2\%$ of the cost of computing $\mathrm{OPT}$ once — not an
ML inference. Second, **the benefit is real, partial, and never harmful**: a stale
forecast captures $27\%$–$68\%$ of the achievable oracle gap (falling with staleness) and
*always* stays above the forecast-free baseline ($0.938$–$0.957$ vs $0.923$–$0.925$, even
at 30 days). Third, and explaining why, **topology aggregation makes the cheap predictor
order-faithful**: the induced degree predictor's order error is only Kendall-$\tau\approx
0.19$–$0.32$, roughly *half* the raw type-histogram's ($0.38$–$0.49$) — and since MPD
depends only on order (Section 4), the aggregated degree route survives real drift.
Consuming the *same* stale forecast through the raw histogram instead is catastrophic:
blind FollowPrediction collapses to $0.68\to0.36$, far below the $\approx0.92$ baseline —
exactly what the robust algorithms of Sections 3 and 5 are for.

## 6.2 Six real-world graphs

We re-run the degree-prediction roster of Section 3 on the six Network-Repository graphs
(two Facebook social, two C. elegans biological, two economic input-output), across the
same quality columns, with 95% CIs (**Figure 6**; `docs/REALWORLD_ROBUSTNESS.md`).

The two load-bearing findings are universal. **F1 holds on all six graphs**: naive MPD
fed an adversarial predictor falls *below* the Ranking floor everywhere — by $0.07$
(Caltech36: $0.843<0.913$) to $0.11$ (CE-PG: $0.782<0.883$). **F3 is universal and
confirms its own logic**: the consistency upside (best prediction algorithm at perfect
advice, over the floor) is small everywhere (mean $+0.049$; range $+0.022$–$+0.077$), and
it is *smallest exactly where the baseline is strongest* — the two dense economic graphs,
with Ranking already $0.965$/$0.977$, give the tiniest upsides ($+0.035$/$+0.022$).

The structural-robustness finding **F2 holds qualitatively on all six** (the augmentations
are always less sensitive to prediction quality than naive MPD) and *strictly* on the four
social/bio graphs (augmentation spread $0.22$–$0.29\times$ MPD's); on the two dense
economic graphs the protection is only *partial* — the augmentation cushions the
adversarial drop (beause: $0.939$ vs naive MPD's $0.893$) but cannot fully clear the
unusually high $0.965$ floor, dipping $\approx0.03$ below it (spread ratio $0.53$–$0.55$).
This econ boundary is instructive rather than a failure: those graphs are so dense that
matching is nearly trivial (Ranking $\approx0.97$, MinDegree $=1.00$), so there is neither
upside to capture (F3) nor much downside to protect — the mechanisms compress together
where robustness does not matter. Finally, F4 is *dramatic* here: the worst-case-designed
Feldman/Jaillet–Lu are the weakest advice-free entries on the econ graphs ($0.73$–$0.77$),
and the MPD augmentation lifts them to $0.99$ — a $+0.26$ rescue.

## 6.3 Does *learning* the predictor help? A negative result

Because MPD consumes the predictor only through its order (Section 4), one might train the
predictor with an order-aware (rank) loss rather than regression. We test this and report
an honest negative (`docs/RANK_LEARNING_M0_M3.md`). With *deliberately divergent* synthetic
features — one carrying magnitude, one carrying order — rank-training does beat regression
sharply (matching ratio $0.989\approx$ oracle vs $0.974$, with rank-training having *worse*
regression error but better order). But the advantage is gated by two things that both
vanish in practice: it is zero when features do not induce an order/magnitude divergence
and zero on easy instances (F3 again), peaking at only $+1.3\%$ on synthetic graphs; and,
decisively, **on real temporal features it disappears** — trained on lagged counts from
real serving traces, the rank- and regression-trained predictors produce *identical* order
(Kendall-$\tau$ $0.126$ vs $0.126$) and identical matching ratio, across every topology and
lag we tried. The dissociation that powers order-aware training is a property of engineered
features, not of realistic ones. The lesson reinforces the thesis: once a predictor is
order-faithful — which a cheap historical count already is (§6.1) — neither a better
algorithm nor a better-trained predictor buys much on average-case matching.

## Summary

On real predictors, real graphs, and a learned predictor, the same wall stands: the
advice-free baseline is near-optimal, unguarded following is unsafe, and predictions buy
downside protection rather than performance. Having established the wall empirically across
every setting we could reach, we now prove it is necessary.
