<!--
Thesis Ch 9 — The Impossibility Theorem (LIGHTER than paper/06 §7 per the user).
Intuition-forward; state the three pillars in words + one key formula each; DEFER full
formal proofs to an appendix / "in preparation". Keep the honest proof-status note.
Sources: paper/06, docs/T1_*. Figure 9.1 = impossibility_frontier.png. Cross-refs to chapters.
-->

# Chapter 9. The Impossibility Theorem: Why the Wall Is Necessary

Every experimental chapter met the same wall: on average-case matching the advice-free
baseline is near-optimal, predictions buy robustness insurance rather than performance, and
— for the test-and-fallback algorithms — no acceptance threshold both captures the tiny
upside and stays safe (Chapter 6). This chapter argues the wall is not an accident of a
particular threshold, graph, or algorithm, but a *theorem*. To keep the exposition focused
we give the intuition and the architecture of the proof here, and defer the full formal
development to Appendix [PROOF].

## 9.1 The claim

Informally:

> On strong-baseline instances, no test-and-fallback algorithm whose test inspects only a
> **sublinear** prefix of the arrivals can be both consistent and robust.

A *test-and-fallback* algorithm (Chapter 3) observes the first $k$ arrivals, decides — by
*any* rule — whether to follow the advice or fall back to Ranking, and commits. The claim is
that when the budget $k$ is sublinear ($k=o(n)$) and the baseline is strong, the achievable
(consistency, robustness) region collapses to the single point "just play the baseline":
one can be safe, or capture the upside, but not both.

**Figure 9.1** is the empirical face of this. As the baseline weakens (moving right to
left), the *potential* upside — how much perfect advice beats the baseline — grows; but the
upside a sublinear test can *safely capture* stays pinned near zero. The gap between the two
curves is the impossibility.

## 9.2 The intuition: testability and baseline strength are the same knob

The heart of the argument is a coupling that is easy to state and, once seen, hard to
un-see. To decide safely whether to trust the advice, the algorithm must, from its short
prefix, tell *good* advice (close enough to the truth to help) from *bad* advice (far enough
to hurt). This is a statistical test on the distribution of request types. Such a test is
only feasible when there are **few types, each arriving many times** — otherwise the prefix
is too sparse to estimate anything. But few high-count types is *exactly* the regime in
which the matching is near-perfect and the advice-free baseline is already near-optimal, so
there is nothing worth testing for. Where the baseline is weak enough that advice could
genuinely help, the types are many and each is seen only a handful of times, and no
sublinear prefix can run the test.

In one sentence: **the structure that makes the test feasible is the structure that makes
the baseline near-optimal — so wherever you can test the advice, you do not need it.** The
rest of the chapter turns this intuition into a proof.

## 9.3 The architecture of the proof

The proof rests on three pillars; we state each in words and give its one key formula,
leaving the formal details to the appendix.

**Pillar 1 — a trade-off inequality (rigorous).** If two instances that require *opposite*
decisions (follow vs fall back) look statistically the same over the prefix — that is, their
prefix distributions have small total-variation distance $\gamma_k$ — then no rule on the
prefix can serve both. Formally, writing $\eta_c$ for the fraction of the upside an algorithm
forgoes and $\eta_r$ for its robustness loss, one shows
$$(1-\eta_c)\;\le\;\eta_r+\gamma_k+o(1).$$
When the prefix is uninformative ($\gamma_k\to0$) the algorithm cannot be both consistent
($\eta_c\to0$) and robust ($\eta_r\to0$). This lemma is short and self-contained; it is the
two-sided core of the result.

**Pillar 2 — a reduction to distribution testing (any rule).** The prefix is *literally* a
set of i.i.d. samples from the type distribution. We build a family in which following the
advice helps exactly when the advice is $\ell_1$-close to the truth and hurts exactly when it
is $\ell_1$-far; on it, a consistent-and-robust algorithm would in effect *distinguish close
from far from the samples* — a **tolerant** distribution-testing problem. Because the
algorithm's decision is an arbitrary function of the samples, the lower bound below rules out
*every* rule, not just the empirical-distance threshold used in practice — which is what
distinguishes our result from the constructive baseline-coupling already present in Choo et
al.'s algorithm.

**Pillar 3 — tolerant testing is nearly as hard as learning the distribution.** The final
ingredient is a known and, at first, surprising fact from distribution testing. *Verifying*
that a distribution equals a known one needs only $\Theta(\sqrt r)$ samples — sublinear in
the number of types $r$. But *tolerant* testing — distinguishing "somewhat close" from
"somewhat far," which is what safe advice-use requires — needs $\tilde\Theta(r/\log r)$
samples, nearly *linear* in $r$ [CJKL22, VV11]. Our construction has $r=\Theta(n)$ types, so
the test needs $\tilde\Theta(n/\log n)$ samples — more than any sublinear prefix provides.
The good-advice side is genuinely a *ball* around the truth (not a single point), which is
what places the problem in the hard tolerant regime rather than the easy $\sqrt r$ one. A
side benefit of the construction is that the map from advice error to matching loss is an
*exact linear law* (verified numerically), which pins the constants cleanly.

Chaining the three: on the family, any $(1-o(1))$-consistent, robust, sublinear-test
algorithm would solve a tolerant test it provably cannot, so no such algorithm exists.

## 9.4 The theorem

> **Theorem (informal).** For every sublinear test budget $k=o(n/\log n)$ there is a
> known-i.i.d. matching family with $\Theta(n)$ types and a strong baseline on which no
> test-and-fallback algorithm — by any rule on its prefix — is simultaneously
> $(1-o(1))$-consistent and robust. The achievable (robustness, consistency) region collapses
> to the baseline point.

Together with the easy strong-baseline side (few types $\Rightarrow$ near-optimal baseline
$\Rightarrow$ no upside to capture), this is precisely the scissors of Figure 9.1, now with a
proof: the upside lives only where the tolerant test is infeasible.

## 9.5 Scope, status, and honesty

**Scope.** The strong form is stated for the regime with $\Theta(n)$ types — which is the
only regime with an upside to contest, and hence the natural one; a version that also bites
at constant $r$ is left open. The reduction inherits the empirical-$\ell_1$ modeling of the
test used by the algorithms it bounds (Chapter 3).

**Relation to prior work.** Choo et al. and BEM give algorithms (upper bounds) and no lower
bound in this model; Choo et al.'s threshold already couples to the baseline ratio, but
*constructively*. Our contribution is the two-sided, *rule-independent* impossibility and the
identification of testability with baseline strength; the reduction from
distribution-testing sample complexity to the value of advice in an online algorithm is, to
our knowledge, new.

**Status (stated plainly).** The trade-off inequality (Pillar 1) is proved; the construction's
constants and the linear conversion law are derived and numerically verified; the
tolerant-testing barrier (Pillar 3) is a cited, exact result on the theorem-preserving side of
the tolerant/non-tolerant divide. One routine step of the construction — exhibiting the two
indistinguishable witness distributions guaranteed by the testing lower bound — and a final
review remain before the full proof is complete. The thesis presents the theorem with this
status stated, as befits in-progress theoretical work; the empirical scissors of Figure 9.1
is independent evidence that the statement is true.
