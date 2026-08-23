---
title: "Defence script — The Limits of Predictions for Online Bipartite Matching"
author: "Zhuolun Li · MSc Computer Science, University of Bristol"
geometry: margin=1in
fontsize: 11pt
---

**Deck:** `defence.pptx` (13 slides + 2 backup). The same script is in each slide's
speaker-notes pane, so you can present from PowerPoint's presenter view alone; this
document adds the timing plan and the Q&A preparation.

**Total:** 2,001 words ≈ **14.8 minutes at 135 wpm**. If you run fast, slow down on
slides 6 and 8 — those are the two that carry the argument.

## Timing plan

| # | Slide | Target | Cumulative |
|---|---|---|---|
| 1 | Title | 0:55 | 0:55 |
| 2 | The problem | 0:50 | 1:45 |
| 3 | Two guarantees, two families | 1:10 | 2:55 |
| 4 | Three questions | 0:55 | 3:50 |
| 5 | Method — one harness | 1:15 | 5:05 |
| 6 | **Finding 1 — the benchmark** | 1:20 | 6:25 |
| 7 | Finding 2 — order error | 1:15 | 7:40 |
| 8 | **Finding 3 — test-and-fallback** | 1:20 | 9:00 |
| 9 | External validity | 1:20 | 10:20 |
| 10 | Negative results | 1:20 | 11:40 |
| 11 | Theory outlook | 1:25 | 13:05 |
| 12 | Critical evaluation | 1:20 | 14:25 |
| 13 | Conclusion | 1:05 | **15:30** |

Two slides are load-bearing. **Slide 6** is where the examiners either accept or reject
the headline; **slide 12** is where you show you can examine your own work. If you have
to cut live, cut slide 9 down to the single 0.36-vs-0.92 sentence.

## Three things to land, whatever else happens

1. The advice-free baseline already reaches **0.990**; the entire consistency headroom is
   **0.009**; unguarded following crashes to **0.472**. The asymmetry is about fifty to one.
2. What governs the residual loss is **order, not magnitude** — and order-dependence
   itself is Aamand–Chen–Indyk's result, not yours.
3. Q3 is **bracketed, not closed**. You prove one inequality and read your own
   measurements through it. Say this before you are asked.

## Anticipated questions

Ordered by how likely they are to come up. Each answer is grounded in a specific part of
the thesis — give the section number, it is the strongest thing you can do in a viva.

**1. "You say 'first unified benchmark' and 'first empirical study'. How do you know?"**

> A systematic prior-art review, §8.3. I searched from several independent starting
> points and checked each novelty claim against the primary papers rather than their
> abstracts, and the review deflated two of my own claims — it reframed the order-error
> finding as partially pre-empted by Aamand–Chen–Indyk's Appendix D, and demoted the
> serving results to a case study. The claims that survived that process are the two I
> lead with. §2.6 states the gap the review found.

**2. "Isn't the wall just an artefact of the instances you chose?"**

> That is the right challenge, and I concede part of it in §10.3: known-i.i.d. is the
> model in which the advice-free baseline is strongest, so the choice partly pre-selects
> the finding. What I can offer against it is breadth. Figure 6.4 sweeps baseline strength
> across the whole difficulty range and the resolution limit persists at every point. The
> findings re-run on six real-world graphs of three different kinds, and on three real
> traces. And I attacked the wall twice — a better-trained predictor and a different
> objective — and it held both times. What I do *not* claim is that it holds for
> adversarial arrival order; that is the first item of future work.

**3. "§10.2 says no rule at any prefix length can capture the upside — but you also say you prove no theorem beyond one inequality. Which is it?"**

> Two separate statements, and I should separate them cleanly. The inequality is proved:
> for any two instance distributions sharing the same advice, forgone upside is bounded
> below by robustness loss plus the prefix distributions' statistical distance. The
> *quantitative* reading — the ≈0.004 threshold — rests on a budget law that this thesis
> does not prove, and it applies to the decomposable rare-resource family that produces
> Figure 6.4. Both limits are stated in §10.2 and again in §10.3.

**4. "Why not implement an actual tolerant distribution tester?"**

> Because the algorithms I am evaluating specify the empirical-ℓ₁ surrogate; substituting
> a different test would mean evaluating a different algorithm. §10.2 argues the
> surrogate's blindness is structural rather than an implementation artefact — it tests
> the *distance* rather than the *payoff*. But I accept the qualification: I have shown
> the failure modes of the mechanism as published, not of every possible prefix rule, and
> an implemented tolerant tester would strengthen the resolution-limit claim.

**5. "0.009 of headroom sounds like a property of your few-types instances."**

> It is a property of strong baselines, and that is the point rather than an accident.
> F3 holds on all six real graphs, with a mean upside of +0.049 — and it is smallest
> exactly where the baseline is strongest, on the two dense economic graphs. That is F3's
> own mechanism confirming itself. On the weakest baselines the upside does grow — which
> is precisely what Figure 6.4 shows, and precisely why the *capturable* upside still
> does not.

**6. "What should a systems engineer actually do with this?"**

> Three things. Use a cheap order-faithful predictor rather than an expensive accurate
> one — a linear-time historical count captured 27–68% of the available gap at 0.11 ms
> against 4.4 ms to compute the optimum once. Never consume a prediction unguarded: the
> same forecast, consumed through the raw histogram route, collapsed to 0.36 against a
> 0.92 baseline. And on the serving side, provisioning is the cheaper
> lever: over the capacity range I swept, added capacity buys the same protection the
> adaptive test does (Figure 9.1).

**7. "n = 2000 is small. Would the picture change at scale?"**

> The Python harness capped instance size, and I list that in §10.3. It is a real
> limitation with a specific direction: §10.2's reading predicts the capturable-upside
> threshold scales as 1/√n, so larger instances would make the wall *more* pronounced,
> not less. Testing that is the cleanest single extension of the work.

**8. "What is genuinely yours, as opposed to Aamand–Chen–Indyk's, Choo's, or BEM's?"**

> Their algorithms and their guarantees are theirs; I implemented them from the papers and
> adapted them to a common error model and optimum. Order-dependence is their theorem.
> Mine are: the unified benchmark and its four findings (Ch. 4); the characterisation of
> which order measure governs the loss and how loose the published bound is — 16–75×, and
> saturating (Ch. 5); the first empirical study of test-and-fallback, including the
> threshold pathology and the resolution limit (Ch. 6); and the trade-off inequality of
> §10.2.

**9. "Your negative results — how do you know the implementation wasn't just weak?"**

> M0 is the control. With engineered features where magnitude and order genuinely
> diverge, rank-training does beat regression — 0.989 against 0.974 — while fitting the
> truth *worse*. So the mechanism works when its precondition holds. M3 then shows the
> precondition does not hold on real temporal features: identical Kendall-τ of 0.126 for
> both predictors. The negative is conditional and I can name the condition, which is what
> makes it a result rather than a failure.

**10. "If the advice-free baseline is already at 0.99, why does this research area exist?"**

> Because the guarantees are worst-case and they are real: in the adversarial model no
> deterministic algorithm beats 1/2 and Ranking is optimal at 1 − 1/e. The area is not
> wrong; my claim is narrower — on *average-case* inputs of this problem, the thing those
> algorithms deliver in practice is downside protection rather than performance. Chapter 3
> shows the same gap in miniature: Feldman and Jaillet–Lu sit 0.03–0.06 *above* their own
> worst-case bounds on average-case inputs.

**11. "What would you do differently?"**

> Three things, and they are in §10.3. Make instance difficulty a first-class axis of the
> benchmark from the start rather than a follow-up to the finding. Carry a second
> objective — tail latency — through the whole benchmark instead of adding it as a late
> probe. And run the decisive realistic experiment before the synthetic ones: M3 is both
> cheaper than M0 and M1 and the one that settled the question.

**12. "Where would predictions actually pay off?"**

> Where the baseline is provably far from optimal, which is exactly where I did not look.
> Adversarial or non-stationary arrival orders is the first candidate; objectives on which
> the baseline is not near-optimal — tail latency, per-type fairness, migration cost — is
> the second. My own tail-latency probe closed the simplest such attempt but not the space.

## If you are asked something you cannot answer

Say so, then say what you would do to find out. "I did not measure that. The experiment
that would settle it is X, and it is one script on the existing harness." That answer is
worth more than a guess, and the harness makes it credible.

\newpage

## Full script, slide by slide

### Slide 1 — Title

Good morning, and thank you for reading the thesis.

My project is an experimental study of learning-augmented algorithms for online bipartite matching — algorithms that are handed a prediction about the future and are supposed to exploit it when it is good and survive it when it is bad.

The single sentence I would like you to leave with is on the slide: on average-case inputs, predictions in this problem are robustness insurance, not a performance lever. Everything I show in the next fifteen minutes is either evidence for that sentence or an attempt to break it.

I will spend about four minutes on the problem and the method, seven on the results, and the last few on what the project achieved and where it falls short.

### Slide 2 — The problem

Online bipartite matching is the canonical model of irrevocable sequential allocation.

One side of the graph — the resources — is known in advance. The other side, the requests, arrives one at a time. Each request must be matched to a free compatible resource, or dropped, immediately, before you see the rest of the input. Nothing can be undone.

That abstraction sits underneath online advertising, ride-hailing dispatch, and request routing in modern inference-serving systems.

Throughout, performance is the ratio of the matching an algorithm produces to the offline optimum on the same instance — so 1.0 means it did as well as an algorithm that saw the whole input in advance.

### Slide 3 — Two guarantees, two families

The influential idea in this area is to hand such an algorithm a prediction about the input and ask for two guarantees at once.

Consistency: near-optimal performance when the prediction is good. Robustness: no worse than a prediction-free algorithm when the prediction is wrong.

For matching specifically, two families exist. MinPredictedDegree consumes a prediction of how contended each resource will be, and protects the scarcest resources first. The test-and-fallback family tests a prediction of the arrival mix on a short prefix of the requests, and then commits — either to following the prediction or to falling back on an advice-free baseline.

The problem is at the bottom of the slide. These two families had only ever been analysed in isolation: each on its own input model, its own notion of prediction error, and almost entirely through worst-case theory. There was no common ground on which to compare them, or to ask what a prediction is actually worth.

### Slide 4 — Three questions

The thesis is organised around three questions.

Q1 is the comparison question: how do these algorithms actually compare, head to head, on common inputs under a single error model — and how much does a prediction buy on realistic data?

Q2 goes inside the adaptive mechanism: what does its test cost, how well is its accept-or-reject decision calibrated, and where does it go wrong?

Q3 is the "why" question: the gap between the worst-case promise and the average-case experience — is it an accident of the algorithms and generators I happened to choose, or is it necessary?

The first two I answer experimentally. The third I answer in outlook form, and I will be explicit later about exactly how far that answer goes.

### Slide 5 — Method — one harness

Here is the instrument. One harness, in which every algorithm sees the same graphs, the same arrival sequences, the same offline optimum, and the same paired random streams — so within a comparison, the only thing that varies is the prediction.

One choice matters more than the rest: the errors are structured, injected along the structure of the instance rather than as independent noise. I will come back to why that mattered.

On the right is the discipline point. Before building anything on this harness I reproduced the published study of Borodin, Karavasilis and Pankratov. All five qualitative claims I checked reproduce within 0.02 — with a different language and a different max-flow routine. That is what lets me attribute every later difference to the algorithms rather than to my infrastructure.

It then runs on synthetic families, six real-world graphs, and three real traces.

### Slide 6 — Finding 1 — the unified benchmark

This is the central result, and the figure is the consistency–robustness plane: each algorithm is a point, horizontal axis is how it does under the worst advice, vertical axis is how it does under perfect advice. Up and to the right is better.

Read the four numbers underneath. On the few-types instances, the advice-free baseline — Ranking, which uses no prediction at all — already reaches 0.990 of the offline optimum. Perfect advice reaches 0.999. So the entire consistency headroom, the whole prize for having a good prediction, is 0.009.

Now the other side. An algorithm that simply follows the same prediction without guarding itself collapses to 0.472 when the prediction is bad — less than half the optimum, and far below the baseline that ignores predictions entirely. The guarded algorithm holds 0.990 whatever the advice.

So the asymmetry is roughly fifty to one. Every wide gap in this benchmark is a downside gap; nothing widens on the upside. The practical worth of these sophisticated algorithms is not that they win — it is that they never crash.

### Slide 7 — Finding 2 — order error

The loss is small — so what governs it?

The algorithm consumes its predictor only through the ordering it induces, so the question is not how large the error is but which order error matters.

Plotted against a Kendall-tau order error — the fraction of resource pairs ranked in the wrong relative order — all four error models collapse onto one curve, Spearman 0.979. A purely monotone rescaling has zero order error and, as predicted, zero loss.

The left panel also shows the known bound from the literature is correct but loose by sixteen to seventy-five times, and saturates near its maximum for every non-trivial error — so it cannot tell a harmful prediction from a harmless one.

On credit: that order rather than magnitude matters is Aamand, Chen and Indyk's theorem. Mine is the characterisation — which order measure governs the loss, and how much room their bound leaves.

### Slide 8 — Finding 3 — test-and-fallback

Question two: what goes wrong inside the adaptive mechanism.

First, a calibration pathology. The acceptance threshold is calibrated against the baseline's proved worst-case ratio, which on average-case inputs is far too lenient. The consequence is counter-intuitive: a small, noisy prefix over-estimates the distance, rejects borderline advice and lands safely on the floor — right, but for the wrong reason. A larger, more accurate prefix measures correctly, accepts, and does worse. More measurement, worse decision.

Recalibrating removes that pathology, and exposes the deeper thing: the resolution limit. No practical threshold can capture an upside smaller than its own estimator's noise.

The figure is the one to remember. Sweeping the number of request types sweeps the baseline's strength. As the baseline weakens the potential upside grows — the upper curve — but the upside a sublinear test can safely capture stays pinned near zero across the whole range. The curves separate rather than converge.

### Slide 9 — External validity

A benchmark on synthetic instances is only worth as much as its external validity, so I replaced the synthetic knob with the cheapest realistic predictor I could think of: last-window historical counts from a real Wikipedia pageview trace, where the error is genuine temporal drift rather than injected noise.

Three things. The predictor is cheap — a linear-time count, about a tenth of a millisecond, against four and a half milliseconds to compute the optimum once. Its benefit is real but partial: it captures between twenty-seven and sixty-eight percent of the available gap, falling with staleness, and it never drops below the baseline.

And the reason it survives is the mechanism from the previous slide. Aggregating the forecast onto the serving topology roughly halves its order error — and order is the only thing the algorithm consumes. Consuming the very same forecast through the raw histogram route, without a guard, collapses to 0.36 against a 0.92 baseline.

I also re-ran the whole roster on six real-world graphs — social, biological and economic. The crash finding holds on all six.

### Slide 10 — Negative results

I did not simply accept the wall. Two attempts to get past it, both reported as results rather than left out.

First, train the predictor better: since the algorithm consumes only the ordering, train it with an order-aware loss. M0 shows the mechanism is real — with engineered features the rank-trained predictor reaches 0.989 against 0.974 while fitting the truth worse. M1 shows the advantage is doubly gated and peaks at just over one percent. M3 is decisive: on genuine temporal features from a real trace the two predictors produce identical order and identical matchings. The divergence that powers the idea is a property of engineered features.

Second, change the objective — if throughput is too forgiving, try tail latency under bursty load. There the best non-predictive policy comes within three percent of a policy that knows the future exactly.

Both negatives reinforce the finding rather than escaping it.

### Slide 11 — Theory outlook

Question three. Is the wall an accident of my inputs, or should it be expected?

I prove one inequality. Take two instance distributions sharing the same advice — one where following it helps, one where it hurts. Every test-and-fallback algorithm, deciding by any measurable rule on its prefix, satisfies the displayed bound: the upside it forgoes is bounded below by its robustness loss plus the statistical distance between the two prefix distributions. The proof is a short conditioning argument — no function of the prefix can behave differently on two prefix distributions that are statistically close.

That converts "consistent and robust" into a question of sample complexity.

Reading my measurements through it: the stakes are capped by the slack the baseline leaves, so on strong-baseline instances the prefix you would need exceeds the whole instance. At the benchmark's parameters that puts the uncapturable upside at about 0.004 — exactly the order of the upsides I measured.

On scope, because this is where I would expect you to push: only the inequality is proved here. The budget law behind the number, and whether it extends beyond decomposable families, is not established in this thesis, and I say so wherever the outlook is used.

### Slide 12 — Critical evaluation

Let me be explicit about how far the project got against its own objectives.

Q1 is met in full. Q2 is met with one qualification I would rather state than have you find: the test I measured is the surrogate the original authors specify, not an implemented tolerant tester. So these are strictly the failure modes of the mechanism as published.

Q3 is the one the thesis falls furthest short of — bracketed, not closed.

Four judgements with hindsight. The structured error models were the best decision in the project; independent noise would have averaged away the order effect entirely.

Two are debatable. Known-i.i.d. is right for comparability, but it is also the model where the baseline is strongest, so the choice partly pre-selected my headline finding. And measuring only matching size is what most limits the conclusion's reach — a second objective should have run through the whole benchmark rather than arriving as a late probe.

And a process lesson: I ran the synthetic stages before the real-feature test, when the real-feature test is both cheaper and decisive.

### Slide 13 — Conclusion

To close. On average-case online matching the honest verdict has three parts.

A cheap, order-faithful predictor already captures nearly all there is to capture. The sophisticated machinery earns its keep as insurance rather than as performance. And finding out whether to trust a prediction costs more, on these inputs, than the prediction is worth.

Where should someone look for predictions that genuinely pay? Precisely where I did not: adversarial or non-stationary arrival orders, where the advice-free baseline is provably far from optimal; objectives on which the baseline is not near-optimal, such as tail latency or fairness; and finishing the budget–stakes law so that the outlook becomes a characterisation rather than a reading.

This is a study of the limits of a popular idea on one well-understood problem. Recognising where predictions cannot help is, I hope, as useful as knowing where they can.

Thank you. I am happy to take questions.

### Slide 14 — Backup — the full benchmark  *(backup, not presented)*

Backup slide. The four findings of the unified benchmark, re-run on six real-world graphs from Network Repository — two Facebook social, two C. elegans biological, two economic input-output.

F1 and F3, the two load-bearing findings, hold on all six. F2 holds qualitatively on all six and strictly on four; the two exceptions are the dense economic graphs, where matching is nearly trivial — so there is neither upside to capture nor much downside to protect. That boundary is F3's own mechanism at work rather than an exception to it.

F4 is the most dramatic: the worst-case-designed algorithms are the weakest advice-free entries on these graphs, and the prediction lifts them by 0.26.

### Slide 15 — Backup — limitations  *(backup, not presented)*

Backup slide: the limitations, as stated in the thesis.

The two I would volunteer first if asked what most constrains the conclusion are the input model and the objective. The wall is an average-case statement in the known-i.i.d. model, and it is a statement about matching size. Both are named in the future work as exactly where a positive counterpart should be looked for.

On the test model: the surrogate is what the original authors specify, and section 10.2 argues its blindness is structural rather than an implementation artefact — but that argument is an interpretation of measurements, not a measurement of an actual tolerant tester.
