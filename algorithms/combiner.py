"""Chłędowski-style dynamic switching combiner (a BENCHMARK, not a contribution).

Chłędowski, Polak, Szabucki & Żołna (ICML 2021, "Robust Learning-Augmented
Caching: An Experimental Study") established empirically that a *blind-follow +
baseline* combiner with online switching is cheap worst-case insurance. We port
that idea to online matching and include it as a BASELINE in the unified benchmark
to contextualise the one-shot test-and-fallback algorithms (Choo/BEM). We do NOT
claim it as novel — it is the obvious meta-algorithm and the cited prior work owns
it.

Mechanism (follow-the-leader with hysteresis):
  - Two SHADOW simulations run on their own matched sets — `follow` (Mimic, the
    blind predictor-follower) and `base` (Ranking) — purely to track which expert
    is ahead in matches so far.
  - One LIVE run holds the real (irrevocable) matched set and executes the action
    of the *current* expert. It switches expert only when the other shadow leads
    by more than a hysteresis margin γ (prevents thrashing on noise).
  - It starts on `base` (safe): with garbage advice the follower never pulls ahead,
    so the combiner stays ≈ Ranking; with good advice the follower leads, and after
    a γ-step warm-up the combiner switches to it and captures most of the upside.

This is the textbook robustness/consistency trade-off of a switching combiner: it
sacrifices a little consistency (the warm-up lag) for a never-far-below-baseline
guarantee — distinct from Choo/BEM, which commit once after a sublinear test.
"""
from __future__ import annotations
import numpy as np


def _mimic_stepper(chat: np.ndarray, partners: list[list[int]]):
    """A fresh Mimic plan (Algorithm 2): for each type, hand out partners[l] in
    order, one per arrival of that type, up to chat[l] arrivals. The closure binds
    its OWN matched set so shadow and live runs don't interfere."""
    budget = chat.astype(np.int64).copy()
    ptr = np.zeros(len(chat), dtype=np.int64)

    def step(l: int, matched: np.ndarray) -> int:
        if budget[l] <= 0:
            return 0
        budget[l] -= 1
        p = partners[l]
        if ptr[l] < len(p):
            r = p[ptr[l]]
            ptr[l] += 1
            if not matched[r]:
                matched[r] = True
                return 1
        return 0

    return step


def combiner(
    instance_adj: list[list[int]],
    types: np.ndarray,
    n_right: int,
    partners: list[list[int]],
    chat: np.ndarray,
    rng: np.random.Generator,
    gamma: int = 10,
) -> tuple[int, dict]:
    """Dynamic switching combiner of FollowPrediction and Ranking.

    Returns (matching size, info). info: final_expert, n_switches, sf/sb shadow
    counts. γ is the (untuned) hysteresis margin in matches.
    """
    n = len(instance_adj)
    n_types = len(chat)

    live_matched = np.zeros(n_right, dtype=bool)
    sf_matched = np.zeros(n_right, dtype=bool)   # shadow follow
    sb_matched = np.zeros(n_right, dtype=bool)   # shadow base (Ranking)

    # One shared Ranking permutation drives both the live base-action and the
    # base shadow (same expert, different matched sets).
    perm = rng.permutation(n_right)
    base_rank = np.empty(n_right, dtype=np.int64)
    base_rank[perm] = np.arange(n_right)

    def ranking_choice(neighbors: list[int], matched: np.ndarray) -> int:
        best, br = -1, np.iinfo(np.int64).max
        for r in neighbors:
            if not matched[r] and base_rank[r] < br:
                br = base_rank[r]
                best = r
        if best != -1:
            matched[best] = True
            return 1
        return 0

    live_follow = _mimic_stepper(chat, partners)    # mimic state for the live run
    shadow_follow = _mimic_stepper(chat, partners)  # independent mimic state

    current = "base"            # start safe
    sf_count = sb_count = 0
    size = 0
    n_switches = 0
    for i in range(n):
        l = int(types[i])
        nb = instance_adj[i]
        # 1. live action by the current expert (irrevocable).
        if current == "follow":
            size += live_follow(l, live_matched)
        else:
            size += ranking_choice(nb, live_matched)
        # 2. advance both shadows on their own matched sets.
        sf_count += shadow_follow(l, sf_matched)
        sb_count += ranking_choice(nb, sb_matched)
        # 3. follow-the-leader with hysteresis for the NEXT arrival.
        if current != "follow" and sf_count - sb_count > gamma:
            current = "follow"; n_switches += 1
        elif current != "base" and sb_count - sf_count > gamma:
            current = "base"; n_switches += 1

    info = {"final_expert": current, "n_switches": n_switches,
            "sf_count": sf_count, "sb_count": sb_count}
    return size, info
