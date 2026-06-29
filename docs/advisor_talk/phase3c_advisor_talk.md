# Phase 3c — Advisor Progress Talk (≈6 min)

Audience: advisor, not deeply technical. Talk to the two artifacts on screen:
the **visuals** (`docs/visuals/*.html`, open in a browser) and
**`PHASE3C_REPORT.md`**. Below is roughly what to say; the *italics* are stage
directions, not lines to read aloud.

---

## 0. One sentence on where we are (15 sec)

"Last week I finished the *adaptive* prediction algorithms — the ones that decide
for themselves whether to trust the advice. That closes the algorithm side of the
project. Today I want to (1) show you three visuals I built to make the problem
concrete, and (2) walk through the one result I think is genuinely paper-worthy."

---

## 1. Make it concrete first — the visuals (1.5 min)

*Open `visuals/01_online_matching_explainer.html`. Click through the 4 arrivals.*

"The whole project is about **online matching**: resources are known up front,
but requests arrive one at a time and each must be matched *immediately and
irreversibly* — no take-backs. The hard part is that a greedy choice now can
strand a request later.

Here's the smallest example that shows it. Four ads, four users.
- *Switch to SimpleGreedy.* Naive greedy grabs the popular ad first — and then the
  user who *only* wanted that ad is stranded. **3 out of 4.**
- *Switch to MinPredictedDegree.* The prediction-aware version grabs the *rare*
  ad first, saving the popular one for the user who depends on it. **4 out of 4.**

That 'save the scarce resource' intuition is the entire value of predictions."

*Open `visuals/02_real_world_applications.html` briefly.* "And it's not a toy — the
same structure is ride-hailing, ad serving, kidney exchange, job scheduling.
*(One line each, point at the map.)*"

*Open `visuals/03_test_and_match_explainer.html`. Drag the advice-quality slider
from perfect to garbage.* "This last one is exactly what I built this week, so let
me move to the results with it on screen."

---

## 2. The Phase 3c result — robustness insurance (2 min)

*Keep visual 03 on screen; have `PHASE3C_REPORT.md` §3 open alongside.*

"The danger with predictions is obvious: **what if the advice is wrong?** Earlier
in the project I showed that the simple prediction algorithm, when fed adversarial
advice, performs *worse* than using no advice at all. That's unacceptable in
practice.

The algorithm I built this week — *Test-and-Match*, from two 2024/2026 papers —
fixes that. It **spends a tiny prefix of the arrivals testing whether the advice
matches reality**, and if it doesn't, it throws the advice away and falls back to
a safe default.

*Drag the slider on visual 03; point at §3's table.* The picture is textbook:
- When advice is good, it follows it and wins.
- When advice is bad, the blind version collapses — *point: 1.00 down to 0.45* —
  but Test-and-Match **detects the bad advice and never crashes**; it sits on the
  upper envelope the whole way.

So the headline is: **adaptive prediction algorithms are robustness insurance.**"

---

## 3. The honest twist — and why it's the real contribution (2 min)

*This is the part to slow down on. §4 + §5 + §6 of the report.*

"Now the honest part, and it's actually the most interesting finding.

**(a) The upside is tiny.** On these average-case inputs, even *perfect* advice
barely beats using no advice — 1.00 vs 0.99. The reason is that the simple
no-advice baseline is *already nearly optimal* here. That's been the through-line
of the whole project: on typical inputs, fancy algorithms don't buy much; their
value is preventing disasters, not raising the average.

**(b) A counter-intuitive result I want to highlight.** I expected a *more
accurate* test to always make a *better* decision. The opposite happened. *§5
table.* A bigger, more accurate test made the *worse* call here.

The reason is subtle and, I think, reportable: the accept/reject threshold in
these papers is tuned for a *worst-case* baseline. But our baseline isn't
worst-case — it's nearly perfect. So the threshold is **too lenient**: it accepts
mildly-bad advice that a practitioner should reject. A small, noisy test
accidentally rejects it (and gets lucky); an accurate test faithfully follows the
miscalibrated threshold — and loses.

**(c) I then fixed it.** *§6.* I recalibrated the threshold to the *measured*
baseline instead of the worst-case assumption. The pathology disappears — the
bigger test no longer hurts.

But the fix exposes a deeper truth: once the baseline is this good, the room for
advice to help is *smaller than the test can even measure reliably*. The safe
move and the optimal move both become 'just reject and play it safe.' That's a
clean, honest, slightly surprising conclusion — and it's mine, from the
experiments, not something the papers state."

---

## 4. Where this leaves the thesis / what I'd value input on (45 sec)

"So the algorithm side is done — four baselines, three families of prediction
algorithms, all reproduced and stress-tested. The recurring, defensible message
is: **on average-case inputs, learning-augmented matching is about robustness
insurance, not raw performance** — and I can show that quantitatively for every
algorithm family.

I also did a deep literature check. The strongest publishable angle looks like a
**unified experimental benchmark** of these algorithms under one error model, plus
this **test-and-fallback** study — that combination doesn't exist yet for matching.

What I'd value your read on: does the 'robustness-insurance, with a concrete
threshold-miscalibration finding' framing sound like enough of a contribution to
aim at an experimental-algorithms venue, or should I push harder on one specific
piece?"

---

## Cheat-sheet (numbers you might be asked)

| Question | Answer |
|---|---|
| Blind-follow with bad advice? | crashes 1.00 → 0.45 as advice worsens |
| Test-and-Match with bad advice? | stays ~0.97–0.99 (falls back to baseline) |
| Perfect advice lift over baseline? | ~1.00 vs ~0.99 — tiny (baseline already ≈OPT) |
| The counter-intuitive bit | bigger/more-accurate test → *worse* decision, because the worst-case threshold is too lenient on easy inputs |
| The fix | recalibrate threshold to the *measured* baseline; pathology gone |
| The deeper limit | when baseline ≈ optimal, the advice upside is below the test's resolution — safe = reject |
| Faithfulness caveat (if pressed) | we use an empirical-L1 test, same proof-of-concept the papers' own authors fall back to (no off-the-shelf tester exists) |

*Don't volunteer the caveat row unless asked — it's a documented, paper-sanctioned
deviation.*
