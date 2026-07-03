# Master's Thesis — Outline & Reuse Map (English; Chinese translation afterwards)

**Decision:** full-English formal thesis first (then a Chinese translation); the venue
paper is the *tight subset* of this, produced later once T1 closes. The thesis is the
**superset** — longer, complete, and it includes the full research journey (the negatives
and explorations that a venue paper cuts), which is exactly what a thesis committee values.

**Relationship to the paper draft.** The paper draft (`docs/paper/00–07`) is the tight
core; most of it becomes thesis chapters with light expansion. The thesis then *adds* a
fuller background chapter, the Phase-2 reproduction, a chapter on the exploratory
directions and negative results, and appendices.

## Chapter structure and reuse map

| Ch | Title | Source (reuse) | New writing needed |
|---|---|---|---|
| — | Front matter (title page, English abstract, [Chinese abstract], ToC, list of figures/tables) | `paper/00` abstract | template + short; Chinese abstract in the translation pass |
| **1** | Introduction | `paper/00_abstract_intro §1` | expand: motivation, **thesis objectives**, contributions, **thesis organization** para |
| **2** | Background & Related Work | `paper/07 §9` + `paper/06 §7.1` + `LITERATURE_REVIEW.md` | **NEW, substantial:** online matching & competitive analysis; the known-i.i.d. model; learning-augmented algorithms (consistency/robustness); the specific algorithms (ACI, Choo, BEM); distribution testing primer — the fuller treatment a paper omits |
| **3** | Model, Algorithms & Methodology | `paper/01 §2` + `PHASE2_REPORT.md` | expand §2; **add the Phase-2 reproduction of Borodin et al.** as foundational validation; more detail on the harness, RNG design, OPT, CIs |
| **4** | The Unified Benchmark | `paper/02 §3` + `UNIFIED_BENCHMARK.md` | light expansion; full CI tables in-text or appendix |
| **5** | What Governs the Loss: Order Error | `paper/03 §4` + `PHASE3_REPORT.md §3.2` | light expansion |
| **6** | Test-and-Fallback in Depth | `paper/04 §5` + `PHASE3C_REPORT.md` | light expansion; more on recalibration |
| **7** | External Validity | `paper/05 §6` + `REAL_PREDICTOR.md`, `REALWORLD_ROBUSTNESS.md` | light expansion |
| **8** | Exploratory Directions & Negative Results | `RANK_LEARNING_M0_M3.md`, `SERVING_SLO_PROBE.md`, `PHASE4_SERVING_REPORT.md`, `LITERATURE_REVIEW.md` | **NEW:** the learning-to-rank exploration (M0–M3), the serving SLO probe, how the deep literature review shaped the direction — the *journey*. Thesis-appropriate; a paper cuts this. |
| **9** | The Impossibility Theorem | `paper/06 §7` + `T1_*` docs | reuse; present honestly with **proof status** (thesis may include in-progress theory) |
| **10** | AI-Inference Serving Case Study | `paper/07 §8` + `PHASE4_SERVING_REPORT.md` | light expansion (thesis can afford more of the serving work) |
| **11** | Conclusion & Future Work | `paper/07 §10` | expand future work |
| — | Appendices | `README.md`, results/, all scripts | **NEW:** reproduction guide (script→figure), full result tables, additional figures |
| — | Acknowledgements, References | `references.bib` | template + finalize bib |

## What the thesis adds over the paper (the delta to write)

1. **Ch 2 (Background)** — a real chapter, not a paper's compressed related-work.
2. **Ch 3 Phase-2 reproduction** — the Borodin reproduction as validation of the harness.
3. **Ch 8 (Exploratory & negatives)** — Direction A (learning-to-rank), the serving SLO
   probe, the literature-review-driven pivots. Demonstrates workload and honest process.
4. **Appendices** — reproduction guide + full tables.
5. **Fuller front/back matter** and the eventual Chinese translation.

## Honesty carried through
- Order-error credits ACI (Ch 5); serving is a case study (Ch 10); the combiner is a
  benchmarked baseline (Ch 6); T1's scope and proof status are stated (Ch 9); the
  negatives (Ch 8) are presented *as* results, not buried.

## Suggested drafting order (highest-value new content first)
1. **Ch 2 Background** (biggest new chapter; also orients the reader).
2. **Ch 8 Exploratory & negatives** (new, and it is thesis-defining — the journey).
3. **Ch 3** add Phase-2 reproduction; **Ch 1** expand.
4. Port Ch 4–7, 9–11 from the paper draft with light expansion.
5. Appendices; then the **Chinese translation pass**.
