# Phase 3 Progress — Advisor Talk Script

*Spoken script, ~10–12 minutes. Plain-language explanations are built in; lines
marked **[slow down]** are where the listener may need an extra sentence or two.
Feel free to cut the bracketed asides if you're short on time.*

---

## 1. Where we are (30 seconds)

"Thanks for meeting. Quick reminder of the project: I'm doing an experimental
study of algorithms for *online bipartite matching* — and extending it to the
new family of algorithms that use *predictions*. Since we last spoke, I've
finished the reproduction phase and most of the new-contribution phase. Today I
want to focus on the new phase — Phase 3 — because that's where two interesting
findings have come out."

---

## 2. A 90-second refresher on the problem

**[slow down — this frames everything]**

"Let me set the scene in plain terms. *Online bipartite matching* is the math
behind things like ride-hailing or online advertising. Imagine an ad system: you
have a fixed set of advertisers known in advance, and users show up one at a
time. The moment a user arrives, you must immediately and irrevocably assign them
to a compatible advertiser — you can't wait, and you can't undo it. The goal is
to match as many as possible.

The catch is that you're deciding *without knowing who shows up next*. So you can
make choices that look fine now but block better matches later.

To score an algorithm, we use something called the **competitive ratio**. Think
of it as a grade from 0 to 1: we compare the algorithm's result to a perfect
'oracle' that could see the entire future in advance and solve it optimally. A
ratio of 0.9 means the online algorithm captured 90% of what was achievable in
hindsight. Higher is better; 1.0 is perfect."

"The new twist — and the heart of my project — is **algorithms with
predictions**. The idea: in the real world you often have a forecast — say, from
a machine-learning model trained on past traffic. The algorithm can use that
forecast, but the forecast might be wrong. So we care about two things:
- **consistency** — how well it does when the prediction is *perfect*, and
- **robustness** — how well it does when the prediction is *garbage*.

The dream is to be good at both: benefit when the forecast is right, but never get
hurt when it's wrong."

---

## 3. What I built in Phase 3 (1 minute)

"In this phase I implemented the first and most fundamental prediction-based
algorithm, from a 2022 paper. It's called **MinPredictedDegree**, but the idea is
simple to state:

**[slow down]** 'When a request arrives, match it to its *rarest* available
option first.' The prediction it uses is just how 'popular' each resource is
expected to be. The intuition: rare resources should be grabbed early, because
popular ones will have more chances to be matched later anyway. It's a very
natural, almost common-sense rule.

I also built four different ways for a prediction to be *wrong* — because in real
life predictions don't just fail randomly; they fail in *structured* ways. For
example: a forecast might be uniformly noisy, or it might be *systematically*
biased (always over-estimating), or it might be adversarially bad, or it might be
based on slightly outdated data. I wanted to measure how each *kind* of error
affects performance — not just how *big* the error is."

---

## 4. Finding #1 — the headline result (2–3 minutes)

**[slow down — this is the main thing to land]**

"Here's the first finding, and I think it's the most interesting one.

The common assumption in this field is: 'the more wrong your prediction is, the
worse you do.' People summarize prediction quality with a single number — how far
off the values are.

What I found is that **the *size* of the error is almost the wrong thing to
measure. What actually matters is whether the prediction still gets the *ordering*
right.**

Let me make that concrete. Remember the rule is 'match the rarest option first.'
So the algorithm only cares about the *ranking* of options from rare to popular —
not the exact numbers. That means:

- If a forecast is *systematically* biased — say it doubles every popularity
  estimate — the numbers are very wrong, but the *ranking* is unchanged. And I
  confirmed this: that kind of error does **literally zero** damage. The
  algorithm doesn't even notice.
- But an *adversarial* error that deliberately flips the ranking — making rare
  things look popular — is devastating, even if the numbers barely move.

And when I plot performance against an 'ordering-error' measure instead of the
usual size-of-error measure, **all four error types collapse onto a single
curve.** In other words, performance is essentially a clean function of *how
scrambled the ranking is* — regardless of which kind of error caused it.

Why this matters for us: it says the standard way the field measures prediction
quality can be *misleading*. Two forecasts with the same 'error size' can have
wildly different real-world impact. The original 2022 paper only tested one kind
of noise, so this comparison across error structures is new — it's not in their
work. *(If you want, I have one figure that shows the four curves landing on top
of each other — it's quite striking.)*"

---

## 5. Finding #2 — simple beats complex (1–2 minutes)

"The second finding reinforces a theme from the benchmark paper I'm building on.

Some of the older algorithms are quite heavy — they do expensive pre-computation,
solving optimization problems before they even start. I compared those against
the simple 'match the rarest first' rule.

**The simple rule wins.** On the graphs where prediction information actually
helps, plain MinPredictedDegree — which just sorts options by popularity — ranks
*higher* than the expensive algorithms, even after I upgrade those expensive
algorithms with the same prediction trick. So all that machinery isn't buying
anything beyond what a simple, well-chosen ordering already gives you.

This is a nice, quotable message: in practice, *simplicity and a good ordering
rule beat complexity*. It echoes the original benchmark paper's conclusion and
extends it into the prediction setting."

---

## 6. Real-world validation (1–2 minutes)

"I also wanted to make sure this isn't just a synthetic-data story, so I brought
in six real datasets — Facebook friendship networks, biological networks, and
economic networks — the same ones the benchmark paper used.

Two things to report, and I want to be candid about both:

**The good news:** using the standard way of preparing these graphs, my results
reproduce the benchmark paper closely — the numbers line up within a few
percentage points across all six datasets. That gives me confidence the whole
pipeline is correct.

**[slow down — be honest here]** **One honest caveat:** the paper also used a
*second* way of preparing the graphs, and there my simple algorithms don't match
their reported numbers — sometimes higher, sometimes lower depending on the
dataset. I investigated and ruled out the obvious explanations. My best read is
that there's an unstated detail in how they built those graphs that I can't
recover without their original code — and those public datasets have also been
revised since 2018. So rather than paper over it, I'm documenting it as an open
discrepancy and using the method that *does* validate cleanly. I actually think
this is a useful observation in itself: when you reproduce an experimental paper,
the *simple* algorithms turn out to be more sensitive to unstated setup details
than the complex ones.

And the key positive: **on every one of the six real datasets, the
prediction-based algorithm comes out on top** — reaching a perfect score on the
economic networks. So the main story holds up strongly on real data."

---

## 7. Where this leaves the timeline (45 seconds)

"So in terms of the plan: the reproduction phase is fully done, and the core of
the new phase — the algorithm, the four error models, the headline finding, the
real-data validation — is all done and documented, with tests.

The remaining piece is the most sophisticated family of algorithms — the ones
that *detect* whether a prediction is trustworthy and fall back to a safe default
if not. That's the next chunk of work. Interestingly, my first finding motivates
it nicely: I showed that the simple algorithm can drop *below* the safe baseline
when predictions are adversarial — and these smarter algorithms are exactly the
mechanism designed to prevent that."

---

## 8. What I'd like your input on (the asks)

"A few things I'd value your guidance on:

1. **Is the first finding — that performance depends on the *ordering* error, not
   the error size — something you've seen reported before?** If it's genuinely
   new, is it worth writing up on its own, or as the centerpiece of the thesis?

2. **If the results reach a publishable level, would you be open to being a
   co-author?** And do you have a target venue in mind?

3. For the next phase, one of the algorithms relies on a fairly heavy statistical
   tool that has no ready-made implementation — even the authors note that. I'm
   planning to substitute a **simpler, practical version** and document the
   difference. **Is that an acceptable approach for our purposes?**

4. Given my background, would you suggest I prioritize finishing this
   prediction direction, or the alternative 'streaming model' direction we
   discussed?"

---

*(Backup, if asked for a number: on the synthetic 'heavy-tailed' graph, the
prediction algorithm scores ~0.99 with a perfect forecast and degrades smoothly
toward the ~0.95 no-prediction baseline as the forecast worsens — and dips below
it only under deliberately adversarial forecasts. On real data it tops all six
datasets, hitting 1.00 on the economic networks.)*
