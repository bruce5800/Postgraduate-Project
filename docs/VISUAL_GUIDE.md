# Visual Guide — explainers for talks, the thesis, and the README

Standalone, browser-openable visuals that make the abstract online-bipartite-matching
material concrete. Each is a single self-contained HTML file (no build step):
open it in any browser, interact, and screenshot for slides or embed in a web report.

These exist because the project is otherwise theory-heavy; they are the artifacts
to reach for when explaining the work to a non-technical audience (advisor,
examiners) or grounding the abstraction.

## The visuals

| File | What it shows | Use it to explain |
|---|---|---|
| [`visuals/01_online_matching_explainer.html`](visuals/01_online_matching_explainer.html) | Interactive: step through 4 user arrivals; switch between SimpleGreedy / Ranking / MinPredictedDegree and watch each decide on the *same* instance | **the online/irrevocable nature** of the problem, and **why "save the rare resource" (MPD) beats naive greedy** — greedy reaches 3/4, MPD reaches 4/4 |
| [`visuals/02_real_world_applications.html`](visuals/02_real_world_applications.html) | Static map: the abstract bipartite structure → four markets (online ads, ride-hailing, kidney exchange, job assignment), filling in offline / online / match for each | **what the abstraction *means* in practice** — directly answers "this is too abstract" |
| [`visuals/03_test_and_match_explainer.html`](visuals/03_test_and_match_explainer.html) | Interactive: drag advice quality from perfect to garbage; watch the prefix test pass/fail and the adaptive algorithm track the better of blind-follow vs baseline | **the Phase 3c consistency/robustness mechanism** — why "test then maybe fall back" captures the upside of good advice without the downside of bad advice |

## The teaching instance (visual 01)

Four ads with different popularity (= predicted degree): `A` popular (3), `B`
medium (2), `C`, `D` niche (1). Four users arrive: `u1→{A,C}`, `u2→{A,B}`,
`u3→{A}`, `u4→{B,D}`. The best possible matching is 4.

- **SimpleGreedy** grabs the first available ad → `u1` takes the popular `A`,
  so when `u3` (who *only* wants `A`) arrives, `A` is gone → `u3` unmatched →
  **3/4**.
- **MinPredictedDegree** grabs the *rarest* available ad → `u1` takes niche `C`,
  leaving `A` free for `u3` → **4/4 (optimal)**.

This is the smallest instance that makes the Phase 3a "rare-resource-first"
intuition land: the niche ads are the scarce resource; grabbing them early frees
the popular ads for the arrivals that depend on them.

## Application mapping (visual 02)

| Application | offline (known) | online (arrives) | a match = | domain twist |
|---|---|---|---|---|
| Online advertising | advertisers & ad slots | user impressions | show a compatible ad | scale, millisecond latency, budgets |
| Ride-hailing | idle drivers | ride requests | assign driver to rider | real-time, geographic, irrevocable |
| Kidney / organ exchange | available organs / donors | patients | allocate to compatible patient | compatibility & ethics constraints |
| Job / task assignment | workers / servers | jobs / tasks | route task to a capable one | load balancing — the streaming angle |

## Notes

- The files inline the claude.ai design tokens (light-mode CSS variables) so they
  render standalone. Visual 02 loads the Tabler icons webfont from a CDN
  (jsdelivr); it degrades gracefully (blank icon slots) if offline.
- To regenerate or restyle, edit the HTML directly — there is no toolchain.
- Visual 03 uses an illustrative baseline of 0.82 so both the consistency upside
  and the robustness floor are visible at once. On the easy average-case
  instances we actually measured, the baseline (Ranking) is ≈0.99, so in practice
  the robustness — not the consistency lift — is the main value (see
  `PHASE3C_REPORT.md` §4 and §6).
