# Phase 3 Progress — Advisor Talk Script

*Spoken script, ~7–8 minutes, to be presented while walking through
`PHASE3_REPORT.md`. Section pointers like (report §3.2) tell you where to point
in the document. Lines marked **[slow down]** are where the listener may need an
extra sentence. The basic problem setup and the consistency/robustness idea were
covered last time, so this jumps straight into what's new.*

---

## 1. Opening (20 seconds)

"Since we last met I finished the reproduction phase and the core of the
prediction phase. I'll talk through this progress report. The short version: the
new algorithm is implemented and tested, it's validated on real data, and two
findings came out that I don't think are in the original papers."

---

## 2. What I built this phase (45 seconds) — *(report §1 and §2)*

"At the top of the report is a table of what's built. The key piece is the
prediction-based algorithm — **MinPredictedDegree**. The rule is intuitive:
*when a request arrives, match it to its rarest available option first* — save the
popular options for later, since they'll get more chances.

Around it I built four different ways a prediction can be *wrong* — because real
forecasts don't fail randomly, they fail in *structured* ways: uniform noise,
systematic bias, adversarial, and outdated data.

**[slow down]** Section 2 of the report is a set of correctness checks. The one
worth mentioning: I verified that when the prediction is perfect, my algorithm
exactly matches the ideal 'oracle' version; and when the prediction is pure
random noise, it exactly reduces to the classic no-prediction baseline. So the
*same* algorithm smoothly spans the whole range from 'perfect forecast' to
'useless forecast' — which is exactly the consistency-to-robustness range we care
about."

---

## 3. Finding #1 — the headline *(report §3.1 and §3.2)* (2–3 minutes)

**[slow down — this is the main thing to land]**

"This is the most interesting result — it's in Section 3.2.

The usual assumption in this field is: 'the more wrong your prediction is, the
worse you do.' People summarize prediction quality with a single number — how far
off the predicted values are.

What I found is that **the *size* of the error is almost the wrong thing to
measure. What matters is whether the prediction still ranks the options in the
right *order*.**

Here's why, in plain terms. The rule is 'match the rarest option first,' so the
algorithm only cares about the *ranking* of options from rare to popular — not
the exact numbers. That leads to two surprising consequences:

- A *systematic* bias — say the forecast doubles every estimate — makes the
  numbers very wrong, but the *ranking* is unchanged. I confirmed it does
  **literally zero** damage. The algorithm doesn't even notice.
- An *adversarial* error that flips the ranking — making rare things look
  popular — is devastating, even if the numbers barely move.

Now look at the second figure in the report. When I plot performance against an
'ordering-error' measure instead of the usual size-of-error measure, **all four
error types collapse onto a single curve.** Performance is essentially a clean
function of *how scrambled the ranking is* — no matter which kind of error caused
it.

Why it matters: the standard way the field measures prediction quality can be
*misleading* — two forecasts with the same 'error size' can have completely
different real impact. The original 2022 paper only tested one kind of noise, so
this comparison across error structures is new."

---

## 4. Finding #2 — simple beats complex *(report §3.3)* (1–2 minutes)

"Section 3.3 is the second finding. Some of the older algorithms are heavy — they
solve optimization problems before they even start. I compared them against the
simple 'rarest first' rule.

**The simple rule wins.** On the graphs where prediction information helps, plain
MinPredictedDegree ranks *higher* than the expensive algorithms — even after I
upgrade those expensive algorithms with the same prediction trick. So all that
machinery isn't buying anything beyond a good ordering rule. The quotable message:
in practice, *simplicity plus a good ordering beats complexity* — which echoes and
extends the benchmark paper's own conclusion."

---

## 5. Real-world validation *(report §3.4)* (1–2 minutes)

"Section 3.4 is the real-data check. I brought in six real datasets — Facebook
friendship networks, biological networks, and economic networks — the same ones
the benchmark paper used. I want to be candid about both halves of the result.

**The good news:** with the standard way of preparing these graphs, my numbers
reproduce the benchmark paper closely — within a few percentage points across all
six datasets. That gives me confidence the whole pipeline is correct.

**[slow down — be honest here]** **One honest caveat:** the paper also used a
*second* graph-preparation method, and there my *simple* algorithms don't match
their reported numbers — higher on some datasets, lower on others. I investigated
and ruled out the obvious explanations. My read is that there's an unstated detail
in how they built those graphs that I can't recover without their original code —
and these public datasets have also been revised since 2018. So rather than paper
over it, I document it as an open discrepancy and use the method that *does*
validate cleanly. I actually think it's a useful observation in itself: when you
reproduce an experimental paper, the *simple* algorithms turn out to be more
sensitive to unstated setup details than the complex ones.

**And the key positive:** on every one of the six real datasets, the
prediction-based algorithm comes out on top — reaching a perfect score on the
economic networks. So the main story holds up strongly on real data."

---

## 6. The consistency / robustness picture *(report §4)* (45 seconds)

"Section 4 ties it together. For this algorithm the trade-off between
'benefit-when-right' and 'safe-when-wrong' is *automatic* — there's no special
machinery. A perfect forecast gives the best score, a useless forecast falls back
to the safe baseline, and the curves in between show exactly how gracefully it
degrades — which is something the theory only gives loose bounds for, but I can
now show precisely."

---

## 7. What's left, and what's next *(report §5)* (45 seconds)

"Section 5 lists what's not yet done. The remaining big piece is the most
sophisticated family of algorithms — the ones that *detect* whether a prediction
is trustworthy and fall back to a safe default if it isn't. That's the next chunk
of work.

And my first finding motivates it nicely: I showed the simple algorithm can
actually drop *below* the safe baseline when predictions are adversarial — and
these smarter algorithms are exactly the mechanism designed to prevent that. So
the two phases connect naturally."

---

*(Backup number, if asked: on the heavy-tailed synthetic graph, the algorithm
scores ~0.99 with a perfect forecast and degrades smoothly toward the ~0.95
no-prediction baseline as the forecast worsens — dipping below it only under
deliberately adversarial forecasts. On real data it tops all six datasets, hitting
1.00 on the economic networks.)*
