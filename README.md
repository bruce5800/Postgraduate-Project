# matching-experiments

Code, experiments, and thesis for

> **The Limits of Predictions for Online Bipartite Matching:
> A Unified Experimental Study and an Impossibility Theorem**
> (MSc thesis, University of Bristol)

One sentence: **on average-case online matching, predictions are robustness insurance
rather than a performance lever — and where you can test the advice, you do not need it.**
The experiments discover this wall (first unified benchmark of the learning-augmented
matching algorithms); the theory proves it is necessary (an impossibility theorem via a
reduction to tolerant distribution testing).

## 🎮 Interactive explainer

The Chapter-9 impossibility theorem, as five hands-on gadgets (drag the sliders, run into
the wall yourself — no background needed):

- **Hosted:** <https://claude.ai/code/artifact/5842dbf9-6688-429b-9c57-d733cda285d7>
- **Local:** open [`docs/interactive/impossibility_explainer.html`](docs/interactive/impossibility_explainer.html)
  in any browser (self-contained, no dependencies; 中文版:
  [`impossibility_explainer_zh.html`](docs/interactive/impossibility_explainer_zh.html))

## Thesis & paper

All chapters live as markdown (edit those, not the TeX) and build three ways:

| Output | Source | Build | Result |
|---|---|---|---|
| English draft (52 pp) | `thesis/en/*.md` | `thesis/latex/build.sh` | `thesis/latex/main.pdf` |
| 中文草稿 (49 pp) | `thesis/zh/*.md` | `thesis/latex/build_zh.sh` | `thesis/latex/main_zh.pdf` |
| **Bristol template (81 pp)** | `thesis/en/*.md` | `thesis/latex_school/build_school.sh` | `thesis/latex_school/thesis.pdf` |

11 chapters + Appendix A (reproduction guide) + Appendix B (proof details).
Citations are pandoc `[@key]` resolved against [`docs/references.bib`](docs/references.bib)
(citeproc for the drafts, biblatex/biber + the template's ACM-numeric style for the school
build). The venue-paper drafts (§-numbered, submission-oriented) are in `docs/paper/`.

## Findings at a glance

- **F1** Naive prediction-following crashes *below* the advice-free floor (0.472 vs 0.990
  on few-types; universal on 6 real graphs).
- **F2** Two robustness mechanisms — structural (augmentations; flat, capped) and adaptive
  (test-and-fallback; upper envelope) — trade consistency for robustness in opposite ways.
- **F3** The consistency upside is tiny on average-case inputs (< 0.01 where the baseline
  is 0.99); every wide gap is a downside gap.
- **F4** The MPD augmentation rescues the worst-case-designed algorithms (+0.26 on econ graphs).
- **Negatives (reported honestly):** rank-loss predictor training wins only on engineered
  features and vanishes on real traces (Kendall-τ 0.126 = 0.126); no serving SLO/tail regime
  where foresight beats a reactive baseline (≤ 3% from clairvoyant).
- **Theorem (Ch. 9):** no test-and-fallback algorithm with a sublinear test — under *any*
  decision rule — is simultaneously consistent and robust on strong-baseline instances;
  reduction to tolerant identity testing (Θ̃(n/log n) samples, Canonne et al. COLT 2022).
  *Status:* core lemma proved, construction verified numerically; one routine
  witness-instance step + final review outstanding (stated plainly in §9.5/§B.7).

## Project status

| Phase | Goal | Status |
|---|---|---|
| 1–2 | Harness + reproduce Borodin et al. (ER, left-regular) | done — [`docs/PHASE2_REPORT.md`](docs/PHASE2_REPORT.md) |
| 3a–3d | MPD + error models; augmentations; 6 real graphs; Choo/BEM test-and-fallback | done — [`docs/PHASE3_REPORT.md`](docs/PHASE3_REPORT.md), [`docs/PHASE3C_REPORT.md`](docs/PHASE3C_REPORT.md) |
| 4 | AI-inference serving case study (b-matching; Wikipedia/Azure/Mooncake traces) | done — [`docs/PHASE4_SERVING_REPORT.md`](docs/PHASE4_SERVING_REPORT.md) |
| ★1–★4 | Order-error vs ACI bound; unified benchmark + combiner; real predictor; real-graph universality | done — [`docs/UNIFIED_BENCHMARK.md`](docs/UNIFIED_BENCHMARK.md), [`docs/REAL_PREDICTOR.md`](docs/REAL_PREDICTOR.md), [`docs/REALWORLD_ROBUSTNESS.md`](docs/REALWORLD_ROBUSTNESS.md) |
| A (M0–M3) | Learning-to-rank the predictor | closed as an honest negative — [`docs/RANK_LEARNING_M0_M3.md`](docs/RANK_LEARNING_M0_M3.md) |
| SLO probe | A with-predictions serving rescue on a tail objective | closed as an honest negative — [`docs/SERVING_SLO_PROBE.md`](docs/SERVING_SLO_PROBE.md) |
| C (T1) | Impossibility theorem | proof architecture complete (Lemma 1 rigorous; W1/W3a closed-form + verified; W2 confirmed via CJKL'22); one routine step + review remain — [`docs/T1_PROOF_SKELETON.md`](docs/T1_PROOF_SKELETON.md) and follow-ups |
| Writing | Paper drafts (`docs/paper/`) + full thesis (3 builds) + interactive explainer | done (drafts; school-template TODOs listed in `thesis/latex_school/thesis.tex`) |

## Directory layout

```
matching-experiments/
├── optimal.py                  # Hopcroft–Karp OPT + b-matching OPT
├── iid_sampler.py              # type graph → i.i.d. instance
├── graphs/                     # synthetic (ER, left-regular, clvb_zipf, few-types),
│                               #   real-world loaders, serving topologies
├── algorithms/                 # GreedyWithPermutation, Ranking, Feldman, JailletLu,
│                               #   MPD (+augmentations), TestAndMatch (Choo/BEM),
│                               #   combiner, serving/dynamic/prefix-cache
├── predictions/                # degree truth + 4 structured error models, type advice
├── tests/                      # hand-verifiable correctness tests (all runnable solo)
├── scripts/                    # experiment drivers; every figure/table has one script
├── results/                    # JSON + PNG outputs (seeded, reproducible)
├── data/                       # real graphs + traces (large; not in version control)
├── thesis/
│   ├── en/ zh/                 # chapter markdown (source of truth)
│   ├── latex/                  # draft builds (pandoc+xelatex): main.pdf, main_zh.pdf
│   └── latex_school/           # University of Bristol template build: thesis.pdf
└── docs/
    ├── paper/                  # venue-paper §-drafts
    ├── interactive/            # the impossibility-theorem interactive explainer
    ├── references.bib          # single bibliography for all builds
    ├── advisor_talk/           # meeting scripts
    └── *_REPORT.md, T1_*.md    # phase reports + theory notes
```

## Dependencies

```
Python 3.12 · numpy 1.26+ · scipy · networkx · matplotlib
    pip install --user numpy scipy networkx matplotlib
Thesis builds: pandoc 3.x + XeLaTeX (drafts); pdflatex + biber (school template)
```

## Reproducing results

Every figure and table is regenerated from a fixed seed by a single script — the full
figure/table → script map, commands, and runtimes are in **thesis Appendix A**
([`thesis/en/A_reproduction.md`](thesis/en/A_reproduction.md)). Quick start:

```bash
for t in tests/test_*.py; do python3 "$t"; done   # correctness anchors
python3 scripts/run_unified_benchmark.py          # Table 4.1 (~100 s)
python3 scripts/plot_unified_panels.py            # Table 4.1 panel charts
python3 scripts/run_consistency_robustness.py     # Fig 4.1
python3 scripts/run_impossibility_frontier.py     # Fig 9.1 (~6 s)
```

To rebuild the thesis PDFs: `cd thesis/latex && ./build.sh && ./build_zh.sh`, and
`cd thesis/latex_school && ./build_school.sh`.
