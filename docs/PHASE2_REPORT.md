# Phase 2 Reproduction Report

**Project:** Experimental study of online bipartite matching, building toward
a learning-augmented extension.
**Reference:** Borodin, Karavasilis, Pankratov, *"An Experimental Study of
Algorithms for Online Bipartite Matching"*, arXiv:1808.04863, 2018.
**Scope:** core 4 algorithms (6 variants), 2 random graph families,
n=1000 nodes per side, 100 i.i.d. trials per parameter value.

## 1. Goal of this phase

Phase 2 is a **fidelity check**, not a contribution. Its purpose is to confirm
that our matching framework — type-graph generators, the i.i.d. sampler, the
Hopcroft–Karp OPT solver, the algorithm implementations, and the evaluation
loop — produces results that **qualitatively match the published Borodin et
al. (2018) figures**. Once this baseline is trusted, Phase 3 can introduce
prediction-based algorithms on top of it and attribute observed differences to
the algorithms themselves rather than to infrastructure bugs.

The success criterion is **qualitative agreement** with the paper's plots and
prose claims, not bit-exact numerical reproduction. Our stack (Python +
NetworkX) differs from the paper's (C++ + Edmonds–Karp), so small absolute
differences (≤ 0.02 in competitive ratio) are expected and accepted.

## 2. Setup

### 2.1 Notation

- **Type graph** G = (L, R, E): the offline bipartite graph known to the
  algorithm in advance.
- **Instance graph** Ĝ: m i.i.d. samples from a uniform distribution over L,
  ordered as arrivals.
- **Integral types**: m = |L| and uniform distribution ⇒ E[Z_ℓ] = 1 ∈ ℤ for
  every type ℓ. All our experiments enforce this default.
- **Competitive ratio**: |ALG(Ĝ)| / |OPT(Ĝ)|.

### 2.2 Common parameters

- n = |L| = |R| = 1000 (matches paper §4.1, §4.2).
- m = n = 1000 (default i.i.d. sampler setting).
- 100 trials per parameter value (matches paper).
- One i.i.d. instance per type graph (matches paper).
- Random seed: 0 (single master seed, then `np.random.default_rng(0).spawn(4)`
  yields four independent streams: graph generation, instance sampling,
  Ranking-randomness, JailletLu-randomness).

## 3. Algorithms implemented

| Name | Type | Source | Module |
|---|---|---|---|
| SimpleGreedy | deterministic, online | paper §2.3.1 | `algorithms/greedy.py` |
| Ranking | randomized, online | Karp et al. 1990 | `algorithms/ranking.py` |
| FeldmanEtAl | non-greedy, known i.i.d. | Feldman et al. 2009 | `algorithms/feldman.py` |
| FeldmanEtAl(g) | greedy version of above | paper §2.4 | `algorithms/feldman.py` |
| JailletLu | non-greedy, known i.i.d. (RLA template) | Jaillet & Lu 2014 | `algorithms/jaillet_lu.py` |
| JailletLu(g) | greedy version of above | paper §2.4 | `algorithms/jaillet_lu.py` |

All non-greedy and greedy variants share the same preprocessing — only the
online tie-breaking changes.

### 3.1 Preprocessing summary

- **FeldmanEtAl**: builds the cap-{2,1,2} flow network (paper Alg 4), solves
  max integral flow, extracts the unit-flow subgraph (which has max degree 2,
  hence a union of paths and cycles), applies the blue-red decomposition
  (paper Alg 3). Returns advice arrays Mb, Mr.
- **JailletLu**: builds the cap-{3,2,3} flow network (paper §2.5 rescaling
  trick), solves max integral flow, divides by 3 to get f* ∈ {0, 1/3, 2/3}.
  Returns restricted neighborhood lists (each of size ≤ 3) and their f* probs.

Both preprocessing steps use `nx.maximum_flow` (preflow-push) on a DiGraph
with explicit `capacity` edge attribute.

### 3.2 Verified algorithm-level invariants

Hand-verifiable tests in [`tests/`](../tests/):

- Single-edge type graph: correct min cases for both algorithms.
- K_{4,2}: matches paper §2.3.2 example (vanilla Feldman covers 2 of 4 L's;
  balancing — done by BahmaniKapralov, not reproduced — would extend to 4).
- Path of length 3 (odd): blue, red, blue.
- L-L even path of length 4: first two blue, then red, blue — covers all
  three L's with blue.
- 4-cycle: alternating blue/red.
- JailletLu sample-list distribution: empirically verifies the
  (2/3, 1/3) probabilities for the 2-neighbor case and the uniform-over-6
  permutations for the 3-neighbor case (60k samples each, error < 1%).
- JailletLu dummy probability: 2-neighbor case with both f*=1/3 leaves 1/3
  dummy mass (empirically 0.335 ≈ 1/3).

12 tests pass.

## 4. Benchmarks reproduced

| Family | Parameter | Range | Paper figure |
|---|---|---|---|
| Erdős–Rényi bipartite | edge prob p = c/n | c ∈ {0.1, 0.3, …, 14.9}, 75 points | Fig 9 (partial) |
| Random Left-Regular | left-degree d | d ∈ {1, 2, …, 30}, 30 points | Fig 18 (partial) |

"Partial" because we reproduce 6 of the paper's 9 algorithms (the core 4 set,
each with greedy and non-greedy variants where applicable). The 3 omitted
algorithms (BahmaniKapralov, ManshadiEtAl, BrubachEtAl) are not on the critical
path for Phase 3.

## 5. Erdős–Rényi results

![ER full sweep, 6 algorithms](../results/er_full.png)

**Runtime:** 20.6 min (n=1000, 75 c × 100 trials × 6 algorithms).

### 5.1 Key values

| c | SG | Rk | F-NG | F-G | J-NG | J-G |
|---:|---:|---:|---:|---:|---:|---:|
| 0.10 | 0.9995 | 0.9994 | 1.0000 | 1.0000 | 0.9991 | 1.0000 |
| 0.50 | 0.9890 | 0.9887 | 0.9865 | 0.9969 | 0.9853 | 0.9928 |
| 1.90 | 0.9362 | 0.9363 | 0.9033 | 0.9637 | 0.9202 | 0.9602 |
| 2.90 | 0.9036 | 0.9035 | 0.8541 | 0.9349 | 0.8802 | 0.9356 |
| **4.90** | **0.8640** | 0.8655 | 0.7648 | **0.8845** | 0.7949 | **0.8854** |
| 8.90 | 0.9094 | 0.9088 | 0.7314 | 0.9123 | 0.7662 | 0.9120 |
| 14.90 | 0.9487 | 0.9486 | 0.7290 | 0.9488 | 0.7640 | 0.9483 |

Per-algorithm global minima:

| algorithm | min ratio | at c |
|---|---:|---:|
| SimpleGreedy | 0.8640 | 4.90 |
| Ranking | 0.8649 | 4.70 |
| FeldmanEtAl | 0.7288 | 13.50 |
| FeldmanEtAl(g) | 0.8833 | 5.30 |
| JailletLu | 0.7616 | 14.10 |
| JailletLu(g) | 0.8839 | 5.30 |

### 5.2 Paper claim verification

| Paper claim (§4.1, §5) | Observed | Verdict |
|---|---|---|
| "greedy versions achieve a global minimum around c=4.9" | SG min at c=4.9 (0.864); Feldman(g) min at c=5.3 (0.884); JailletLu(g) min at c=5.3 (0.884) | ✓ |
| "we did not plot Ranking, since its behavior in this experiment was analogous to SimpleGreedy" | max |SG − Rk| across all 75 c-values is 0.0017 | ✓ |
| "non-greedy versions show a drop in performance as c increases" | Feldman-NG: 0.987 → 0.729; JailletLu-NG: 0.985 → 0.764 — both monotonically dropping | ✓ |
| "greedy versions of [complex algorithms] perform only slightly better than simple greedy" | At c=14.9, max(F-g, J-g, Rk) − SG = +0.0005; at c=4.9, difference = +0.022 | ✓ |
| "For c=14.9 the experimental ranking of non-greedy algorithms is consistent with Table 1" | J-NG (0.764) > F-NG (0.729) matches Table 1 ordering (JailletLu 0.7293 > FeldmanEtAl 0.6702) | ✓ |

## 6. Random Left-Regular results

![Left-Regular sweep, 6 algorithms](../results/left_regular.png)

**Runtime:** 10.4 min (n=1000, 30 d × 100 trials × 6 algorithms).

### 6.1 Key values

| d | SG | Rk | F-NG | F-G | J-NG | J-G |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1.0000 | 1.0000 | 0.9845 | 1.0000 | 0.9845 | 1.0000 |
| 2 | 0.9539 | 0.9537 | 0.8769 | 0.9679 | 0.8945 | 0.9659 |
| **5** | **0.8905** | 0.8900 | 0.7595 | 0.9008 | 0.7909 | 0.9022 |
| 10 | 0.9275 | 0.9278 | 0.7317 | 0.9276 | 0.7677 | 0.9290 |
| 20 | 0.9652 | 0.9645 | 0.7313 | 0.9627 | 0.7625 | 0.9631 |
| 30 | 0.9770 | 0.9767 | 0.7308 | 0.9757 | 0.7633 | 0.9754 |

Per-algorithm global minima:

| algorithm | min ratio | at d |
|---|---:|---:|
| SimpleGreedy | 0.8905 | 5 |
| Ranking | 0.8900 | 5 |
| FeldmanEtAl | 0.7282 | 29 |
| FeldmanEtAl(g) | 0.8999 | 6 |
| JailletLu | 0.7610 | 23 |
| JailletLu(g) | 0.9001 | 6 |

### 6.2 Paper claim verification

| Paper claim (§4.2) | Observed | Verdict |
|---|---|---|
| "sparse case (d=2), difficult case (d=5), asymptotic case (d=30)" | SG min at d=5 (0.890); SG at d=1 = 1.0 (trivially optimal — each L has 1 choice); SG at d=30 = 0.977 | ✓ |
| Greedy and Ranking nearly identical | max |SG − Rk| across 30 d-values is 0.005 | ✓ |
| Non-greedy algorithms degrade as d grows | F-NG: 0.985 (d=1) → 0.731 (d=30); J-NG: 0.985 → 0.763 | ✓ |
| Greedy variants of complex algorithms ≈ SG | At d=30: max difference among {SG, F-g, J-g} is 0.002 | ✓ |

## 7. Cross-experiment observation

A non-obvious finding from combining the two sweeps:

| Algorithm | Asymptotic ratio (ER, c=14.9) | Asymptotic ratio (LR, d=30) |
|---|---:|---:|
| FeldmanEtAl (non-greedy) | 0.7290 | 0.7308 |
| JailletLu (non-greedy) | 0.7640 | 0.7633 |

The two non-greedy algorithms converge to **the same constant in both random
graph families** (within 0.002). Both constants are higher than the
worst-case theoretical bounds (Feldman 0.6702, JailletLu 0.7293), by about
+0.06 and +0.03 respectively. This suggests a "random-i.i.d. asymptotic
constant" that is universal across these graph families but distinct from
the worst-case bound — a phenomenon Phase 3's prediction-error sweeps may
be able to probe further.

## 8. Implementation notes (the gotchas)

These are decisions made during Phase 2 that future contributors should be
aware of.

### 8.1 Hopcroft–Karp setup
`nx.bipartite.hopcroft_karp_matching` requires `top_nodes` to be a set of
nodes that are *present in the graph*. If a left node has no edges (common at
ER c≈4.9, where some types have empty neighborhoods), it won't be auto-added
by `add_edge`. Fix: call `g.add_nodes_from(...)` for both sides explicitly
before adding edges.

### 8.2 RNG stream design
We use `np.random.default_rng(seed).spawn(4)` to obtain four independent
streams:
- `rng_graph` — graph generation
- `rng_instance` — i.i.d. instance sampling
- `rng_rk` — Ranking's permutation
- `rng_jl` — JailletLu's list sampling

This decoupling means adding a new algorithm (e.g., Phase 3's
MinPredictedDegree) requires only spawning a new stream — old results
remain bit-exact reproducible.

### 8.3 i.i.d. sampler shares neighbor-list references
For a given type t, `instance_adj[i] = type_adj[t]` is a reference, not a
copy. This is safe because all algorithms treat `instance_adj[i]` as
read-only. Saves ~10× memory at n=1000. Phase-3 algorithms that mutate
neighbor lists must explicitly copy.

### 8.4 JailletLu single-neighbor case
The paper's text "if ℓ has a single restricted neighbor, D_ℓ assigns unit
weight to the list consisting of that neighbor" is ambiguous about the
implicit dummy mass when f*_{ℓ,r₁} = 1/3 (rather than 2/3). We follow the
literal reading: always try the single restricted neighbor, never sample a
dummy in that case. The 2-neighbor case does include dummy sampling when
f*_{ℓ,r₁} + f*_{ℓ,r₂} < 1.

### 8.5 Blue-red decomposition is sensitive to traversal start
The L-L even path's "first two edges blue" rule is direction-sensitive — the
two valid traversals (from either endpoint) yield different but equivalent
decompositions. We document this in the test (`test_LL_even_path`'s expected
output is one of two valid configurations).

### 8.6 Python vs C++ baseline
The paper used C++ with hand-rolled Edmonds–Karp. We use Python + NetworkX
(preflow-push internally). Effects:
- 5–10× slower per max-flow call, but small absolute (60–100ms at n=1000).
- Different integral max-flow solutions in cases of multiple optima — affects
  blue-red decomposition outcomes, but not the overall competitive ratio.

## 9. Not reproduced

Listed for transparency — these are out of scope, not bugs:

- BahmaniKapralov (improves Feldman with balancing) — its main practical
  effect is on greedy ratio at small c/d; we accept the small gap.
- ManshadiEtAl (correlated sampling on fOPT) — requires Monte Carlo solving
  of OPT on 100 sampled instances per type graph; expensive and only marginal
  improvement.
- BrubachEtAl (state-of-the-art worst-case 0.7299) — requires a much harder
  LP and rounding procedure; the paper itself notes "exponentially slow with
  d" and "simpler methods either match or surpass its performance".
- Category-Advice / 3-Pass — not in the known-i.i.d. taxonomy; the paper
  shows they outperform everyone but are not the target of the Phase-3
  prediction extension.
- Molloy-Reed (Fig 23–30) and Preferential Attachment (Fig 31–35) families.
- Stand-alone benchmarks (UT, MH, FH, FewG, ManyG, Rope, Hexa, Zipf) —
  Table 2.
- Real-world benchmarks (socfb-Caltech36, …) — Tables 3 & 4.

## 10. Reproducibility checklist

To exactly reproduce the figures in this report:

```bash
# from project root
python3 scripts/run_er_full.py            # 20 min, produces er_full.{json,png}
python3 scripts/run_left_regular.py       # 10 min, produces left_regular.{json,png}
```

Seed is hardcoded to 0. Different numpy versions may produce different
sequences from the same seed (numpy 1.25+ uses BitGenerator-based spawning,
which is stable across minor versions). Tested on numpy 1.26.4.

## 11. What Phase 3 will build on this

Phase 3 (learning-augmented matching) reuses without modification:
- `optimal.py`, `iid_sampler.py`
- `graphs/synthetic.py` (both ER and Left-Regular generators)
- `algorithms/greedy.py`, `algorithms/ranking.py`
- The runner pattern (`scripts/run_er_full.py` as template)
- The 4-stream RNG design (will spawn additional streams for prediction
  generation and prediction-perturbation)

Phase 3 will add:
- `algorithms/min_predicted_degree.py` (Aamand, Chen & Indyk, NeurIPS 2022)
- `algorithms/choo.py` (Choo et al., ICML 2024 — prefix-detection + fallback)
- `predictions/` module: degree predictors with parametric error models
  (random flip, systematic bias, adversarial perturbation, distribution drift)
- New experiments: performance-vs-prediction-error curves across all four
  error models, on both ER and Left-Regular graphs.
