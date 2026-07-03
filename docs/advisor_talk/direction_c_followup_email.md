# Follow-up email to advisor — Direction C (draft)

*Draft for you to edit/send. Written in English to match the talk you just gave; if
[advisor] would prefer Chinese, say the word and I'll produce a Chinese version. Fill in
the bracketed bits. Attach the four notes listed at the bottom.*

---

**Subject:** Follow-up on today's theory result — a written walk-through

Dear Professor [Name],

Thank you for your time today. I realise I moved through the theory quickly and it was
fairly dense, so I've written it out below at a readable pace — please feel free to read
whenever convenient, and I'm happy to meet again to go through any part.

Let me start from the one idea, in plain terms, before any formalism.

**The one idea.** When we hand an online algorithm a prediction ("advice") to help it, we
would like to *check* whether the advice is trustworthy before committing to it — this is
exactly what the recent "test-and-fallback" matching algorithms (Choo et al. 2024;
Burathep–Erlebach–Moses 2026) do: they watch a short prefix of the input, test the advice,
then either follow it or fall back to a safe advice-free algorithm. My result is that this
check faces a fundamental obstacle:

> On the inputs where the advice *could* meaningfully help, verifying it requires seeing
> more data than the algorithm gets before it must act; and on the inputs where you *can*
> verify it quickly, the advice was not going to help anyway, because the simple
> advice-free algorithm is already near-optimal there. **Verifiability and value are
> coupled — you can have one or the other, not both.**

This is why, across all my experiments (synthetic graphs, six real graphs, real request
traces, a serving objective), predictions never gave a real *performance* gain on
average-case inputs — they only ever act as *insurance* against catastrophically bad
advice. I now believe that empirical wall is a **theorem**, not a coincidence.

**A concrete picture.** Think of one small situation: a flexible request arrives that can
use either of two servers, and I must place it *now*; a moment later a "picky" request may
arrive that can use only one specific server. If I selfishly put the flexible request on
that server, the picky one is stranded. The right move is to save the scarce server — but
whether it's right depends on a *future* arrival I haven't seen. Good advice tells me which
way to guess; bad advice points me the wrong way. The catch: to tell good advice from bad,
I must observe enough of these little situations to see which way they tend to go — and if
each one is only seen a handful of times in the prefix, I simply can't tell. Scale this up
to many independent such situations and you get the theorem.

**Why it is a theorem, not just a pattern.** The key step is a reduction. Being able to
*safely use* the advice is equivalent to being able to *statistically distinguish*
"advice that's close enough to the truth to help" from "advice that's far enough to hurt."
Crucially this is not checking whether the advice is *exactly* right — only whether it's in
the *good range* vs the *bad range*. Distinguishing "somewhat close" from "somewhat far"
(rather than "exactly right" from "far") is a well-studied and provably *hard* statistical
problem — **tolerant testing** — which needs almost as many samples as there are possible
outcomes (Canonne–Jain–Kamath–Li, COLT 2022: it takes ~n/log n samples, versus only ~√n
for the easier "exactly right" version). Since the algorithm only sees a *sublinear*
prefix, it cannot run this test — and this holds for *any* decision rule, not just the
specific threshold the papers use. That last point is what makes the result an
impossibility rather than a comment on one algorithm.

**What is genuinely new.** The recent papers give *upper bounds* — algorithms — and even
put the baseline's strength into their acceptance threshold, but only constructively; none
proves a lower bound of this kind. Nobody has (a) connected the *sample complexity of
testing* to the *value of advice* in an online algorithm, or (b) observed that the
structure making the test feasible is the same structure making the baseline near-optimal.
Those two points are the contribution. (I did a prior-art search; the closest works are
Choo 2024, Burathep–Erlebach–Moses 2026, Wei–Zhang 2020, Yoshinaga–Kawase 2026, and I can
position against each.)

**Honest status.** I want to be precise about what is and isn't done:
- The core inequality tying consistency, robustness, and the prefix's information content
  is **proven** and self-contained.
- The reduction to the testing problem is **clean** (the prefix is literally i.i.d.
  samples).
- The single "gadget" is **computed in closed form and verified numerically**; the
  conversion from advice-error to matching-loss turned out to be an exact linear law, also
  verified.
- The one external ingredient — the tolerant-testing lower bound — is a **cited, exact
  result** and, importantly, it lands on the side that makes my theorem true.
- **Remaining:** one routine step (naming the two specific "hard" distributions the
  testing lower bound guarantees). No step now requires inventing new mathematics.

**Where I'd value your guidance.**
1. Is the reduction to tolerant testing sound to you, and are there subtleties in matching
   the standard hard instance into my construction that I should be careful about?
2. My impossibility is strongest in the regime with many rare types (the only regime where
   advice has room to help). Is that scope a referee would accept, or should I push for a
   version that also bites with few types?
3. Positioning: does this read as a standalone theory paper (SODA/ESA/ITCS-style), or as
   the theory section of my experimental study? Either way the experiments are the
   companion evidence.

I've attached my notes if you'd like the formal details: the proof skeleton, the single-cell
computation, the construction, and the close-out on the two technical points above. I'd be
glad to meet this week to walk through whichever part is most useful.

Thank you again for your guidance.

Best regards,
[Your name]

*Attachments:* `T1_PROOF_SKELETON.md`, `T1_W1_single_cell.md`, `T1_W3_construction.md`,
`T1_W2_W3a_closeout.md` (and the figure `impossibility_frontier.png`).
