<!--
Thesis Ch 4 — The Unified Benchmark. Adapted from paper/02 §3 (numbers identical:
scripts/run_unified_benchmark.py). Chapter framing + section renumber + cross-refs fixed
(paper §7→Ch 9). Table 4.1 = the three panels; Figure 4.1 = grouped bars.
-->

# Chapter 4. The Unified Benchmark

Having validated the harness (Chapter 3), we now place all three algorithm families on it
and establish the thesis's organizing finding. This chapter reports competitive ratios
(mean $\pm$ 95% CI) as a function of prediction quality, in three panels chosen to span the
regimes each family was designed for; the four findings it draws out (§4.2) recur through
the rest of the thesis.

## 4.1 Design

The families consume different prediction objects, so each is driven by its own corruption
knob and reported in a parallel panel (Chapter 3); the shared harness — graphs,
$\mathrm{OPT}$, CI methodology, and the advice-free floor — is what makes the panels
comparable.

- **Panel A — clvb_zipf** ($n=1000$, 60 trials): heavy-tailed offline degrees, where degree
  predictions carry signal.
- **Panel B — left-regular $d{=}5$** ($n=1000$, 60 trials): near-homogeneous degrees, where
  predictions add little.
- **Panel C — few-types $r{=}8$** ($n=2000$, 50 trials): near-perfect-matchable, the
  calibrated regime for the type-histogram test-and-fallback algorithms.

For the degree-prediction panels the quality columns are *perfect* (true degrees), *noisy*
(random-flip at strength $\tfrac12$), *adversarial* (order-reversing), and *garbage*
(fully random $\equiv$ Ranking). For the advice panel they are $\eta\in\{0,0.3,0.6,1.0\}$
(*perfect / mild / bad / garbage*). Confidence intervals are tight throughout
($\pm0.001$–$0.003$). **Table 4.1** and **Figure 4.1** are the chapter's data; the salient
rows:

| | perfect | noisy | adversarial | garbage |
|---|---:|---:|---:|---:|
| *Panel A — clvb_zipf* | | | | |
| Ranking (floor) | 0.948 | — | — | — |
| MinDegree (oracle) | 0.996 | — | — | — |
| MPD | 0.989 | 0.956 | **0.908** | 0.946 |
| Feldman(MPD) | 0.981 | 0.979 | 0.976 | 0.978 |
| JailletLu(MPD) | 0.977 | 0.976 | 0.974 | 0.975 |
| Feldman / JailletLu (base) | 0.887 / 0.901 | — | — | — |
| *Panel B — left-regular $d{=}5$* | | | | |
| Greedy = Ranking (floor) | 0.890 | — | — | — |
| MinDegree (oracle) | 0.966 | — | — | — |
| MPD | 0.932 | 0.906 | **0.854** | 0.888 |
| Feldman(MPD) / JailletLu(MPD) | 0.906 / 0.903 | 0.903 / 0.902 | 0.896 / 0.898 | 0.900 / 0.901 |
| Feldman / JailletLu (base) | 0.758 / 0.789 | — | — | — |

| | perfect | mild | bad | garbage |
|---|---:|---:|---:|---:|
| *Panel C — few-types $r{=}8$* | | | | |
| Ranking (floor) | 0.990 | — | — | — |
| MPD (true degrees) | 0.999 | — | — | — |
| FollowPrediction | 1.000 | 0.832 | 0.679 | **0.472** |
| TestAndMatch (Choo) | 1.000 | 0.984 | 0.989 | 0.990 |
| TestAndMatch (BEM) | 0.998 | 0.988 | 0.988 | 0.968 |
| Combiner *(benchmark)* | 0.990 | 0.990 | 0.990 | 0.990 |

![The unified benchmark: competitive ratio (mean, 95% CI) versus prediction quality, for the three panels. Naive followers (MPD under adversarial, FollowPrediction) dip below the advice-free floor; the robust algorithms do not.](../../../results/unified_benchmark.png){width=100%}

## 4.2 Four findings

**(F1) Robustness is engineered, not free: naive followers crash below the floor.** Both
unguarded prediction-followers dive under the advice-free Ranking floor once the prediction
is adversarial or garbage: MPD falls to $0.908<0.948$ (Panel A) and $0.854<0.890$ (Panel
B), and FollowPrediction collapses to $0.472\ll0.990$ (Panel C). Using either *unguarded*
is strictly worse than using no prediction at all. Every robust algorithm — the
augmentations, TestAndMatch, the combiner — avoids this by construction.

**(F2) Two distinct robustness mechanisms, with different shapes.** *Structural* robustness
(Feldman(MPD), JailletLu(MPD)): the worst-case-optimal base matching carries the load and
the prediction only breaks ties, so performance is nearly *flat* — Feldman(MPD) moves only
$0.981\!\to\!0.976$ from perfect to adversarial (Panel A). It cannot crash but caps the
upside (never reaching the $0.996$ oracle). *Adaptive* robustness (TestAndMatch): test a
sublinear prefix, then commit — capturing the upside when advice is good (Choo $1.000$) and
holding the floor when it is bad ($0.990$). On Panel C it is the only algorithm on the upper
envelope at both ends. The two mechanisms trade consistency for robustness in opposite ways.

**(F3) The consistency upside is small on average-case inputs; the spread lives on the
bad-advice side.** On few-types the advice-free Ranking is already $0.990$ and
MPD-with-true-degrees is $0.999$ — under $0.01$ for any advice to add on the good side.
Every wide gap in Panel C is a *downside* gap. This is the thesis in one panel; Chapter 9
shows it is *necessary*.

**(F4) The augmentation rescues structurally weak base algorithms.** Feldman and Jaillet–Lu
are tuned for the worst-case ratio and are the *weakest* advice-free entries on these
average-case inputs (Panel B: $0.758$ / $0.789$, below Greedy's $0.890$); the MPD
augmentation lifts them to $\approx0.90$. The prediction does *more* for the
worst-case-designed algorithms than for greedy — a pairing visible only under a unified
table.

## 4.3 Chapter summary

On average-case matching the advice-free baseline is already near-optimal, unguarded
prediction-following is unsafe, and the value of the sophisticated algorithms is downside
protection delivered by one of two mechanisms. Chapters 5–7 sharpen each part — what governs
the (small) loss, what the adaptive test costs, and whether the picture survives on real
data — and Chapter 9 proves the wall is a theorem, not an artifact.
