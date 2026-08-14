# Self-verification checklist — the ownership pass before arXiv (drafted 2026-07-29)

Purpose: after this pass, **every claim in the paper is one you have personally verified
and can defend alone** — the single remaining gate before arXiv/TALG. Estimated total:
**~2.5 focused days** (½ day reproduction, ½ day experiment spot-checks, 1 day theory by
hand, ½ day prose ownership + global checks). Work through in order; tick boxes as you go.

Conventions: `results/*.json` are the ground truth the paper quotes; every command runs
from the repo root; expected values are quoted from the current draft — a mismatch means
either the draft or the pipeline drifted, and either way you must resolve it before
signing off.

---

## A. Full reproduction from a clean state (~½ day, mostly waiting)

- [✅] A1. Fresh environment sanity: `python3 -c "import numpy, scipy, networkx, matplotlib"`.
- [✅] A2. All hand-verifiable tests pass (now 8 files):
  ```bash
  for t in tests/test_*.py; do python3 "$t" || echo "FAIL $t"; done
  ```
- [✅] A3. Fast headline scripts — rerun and confirm each finishes and overwrites `results/`:
  ```bash
  python3 scripts/run_unified_benchmark.py        # ~100 s
  python3 scripts/plot_unified_panels.py
  python3 scripts/run_consistency_robustness.py
  python3 scripts/run_order_vs_theory.py          # ~30 s
  python3 scripts/run_real_predictor.py
  python3 scripts/run_realworld_robustness.py     # ~65 s
  python3 scripts/run_rank_vs_mse_mve.py
  python3 scripts/run_rank_real_trace.py
  python3 scripts/run_serving_slo_probe.py
  python3 scripts/run_impossibility_frontier.py   # ~6 s
  python3 scripts/verify_witness_gap.py           # ~1 min
  python3 scripts/verify_budget_stakes_hetero.py  # ~1 min
  python3 scripts/run_directional_test.py         # ~10 min
  ```
- [✅] A4. Long sweeps, once (background, ~1 h total): `run_er_full.py`, `run_left_regular.py`,
      `run_choo_bem.py`, `run_recalibration.py`.
- [✅] A5. Rebuild the paper and eyeball every figure against the regenerated PNGs:
      `cd docs/paper/latex && ./build_paper.sh` → 23 pp, "citations: all resolved".

## B. Experimental claims, section by section (~½ day)

Open the JSON next to the paper section; confirm each quoted number.

**§3 unified benchmark** (`results/unified_benchmark.json`, `unified_benchmark_tables.md`)
- [✅] B1. Panel C: Ranking floor 0.990; FollowPrediction 1.000 / 0.832 / 0.679 / **0.472**;
      TestAndMatch Choo 1.000/0.984/0.989/0.990; BEM 0.998/0.988/0.988/0.968; combiner flat 0.990.
- [✅] B2. Panel A: MPD adversarial **0.908** (below floor 0.948); augmentations ≈0.97 flat.
      Panel B: Feldman/JL base 0.758/0.789 → ≈0.90 with MPD (F4).
- [✅] B3. F3 wording: "under 0.01 to add on the good side" — check floor 0.990 vs oracle 0.999/1.000.

**§4 order error** (`results/order_vs_theory.json`)
- [✅] B4. Loss below n−LIS bound by ~16×–75× across models; four models collapse on the
      Kendall-τ axis; monotone(systematic_bias) → loss 0 row exists.

**§5 test-and-fallback** (`results/choo_bem.json`, `recalibration.json`, `directional_test.json`)
- [✅] B5. Envelope: Follow 1.000→0.453 (ℓ₁≈1.1); BEM 0.998→0.969; Choo 1.000→0.991.
- [✅] B6. Prefix pathology: ratio 0.992→0.981→0.969→0.956 and misjudgement 0.00→0.13→0.33→0.60
      as k=25→100→200→800 at η=0.15.
- [✅] B7. Recalibration: τ̂≈0.028 < noise floor 0.05–0.13; worst-case misjudge →1.00 / ratio 0.920;
      recal 0.00 / ≈0.986; at perfect advice 1.000 (wc) vs 0.987 (recal).
- [✅] B8. §5.4 envelope: choo 0.948/0.937 (mis 1.00/0.63) at η=0.1/0.2; directional 0.989/0.990
      (mis 0.03/0.00); ~40% capture at η=0 (mis 0.60 — and you can explain WHY that is the
      honest ceiling: k*≈1/0.02²≈2500 > n).
- [✅] B9. §5.4 crossover: choo mis 0.07→1.00 (ratio 0.987→0.922); directional mis 0.53→0.00
      (ratio 0.954→0.991), k=25→800.
- [✅] B10. Combiner: robust tuning flat 0.990; eager switching 0.927 < both 1.000 and 0.958
      (`python3 tests/test_combiner_small.py`).

**§6 external validity** (`results/real_predictor.json`, `realworld_robustness.json`,
`rank_*.json`, `serving_slo_probe.json`)
- [✅] B11. Wikipedia predictor: cost ≈2.1% of OPT wording; staleness 1/7/30d rows; never below floor.
- [✅] B12. Six real graphs: naive-adversarial below floor on ALL six; augmentation restores.
- [✅] B13. Rank-learning negative: engineered 0.989 (rank) vs 0.974 (MSE), floor 0.947;
      real traces τ 0.126 = 0.126 identical.
- [✅] B14. SLO probe: non-predictive within ≤3% of clairvoyant in every regime.

## C. Theory by hand — pen, paper, and the verify scripts (~1 focused day)

This is the part you must OWN completely; every proof is short.

- [✅] C1. **Lemma 1 (master trade-off)**: rederive the three displays yourself —
      conditioning under G; the symmetric one under Bd; |P_G(F)−P_Bd(F)| ≤ γ_k via the
      coupling characterization of TV. (~30 min. Know why σ is shared advice matters.)
- [✅] C2. **Cell constants**: derive OPT=1+θ, baseline=1+θ/2, follow=1+θ·max/min(s,1−s),
      ℓ₁=2θ|s−ŝ| from scratch; cross-check Gadget A / `verify_witness_gap.py` check 1. (~30 min)
- [✅] C3. **Affine law**: redo the sum-over-cells proof; check break-even ℓ₁*=2(ρ_perf−ρ_base)
      and the verified crossing 0.223 vs 0.224. (~30 min)
- [✅] C4. **σ² identities** (one-line algebra each): 1−ρ_base = σ²/2 exactly;
      ρ_perf−ρ_base = Σθᵢεᵢ/N ≤ 2ε_max(1−ρ_base). (~15 min)
- [✅] C5. **Payoff identity (Lemma 2)**: masses of favored/disfavored specialists → per-cell
      contribution 2θᵢ(sᵢ−½)d̂ᵢ/N → sum = 2×advantage/OPT; confirm it needs NO magnitude
      matching. Cross-check `verify_budget_stakes_hetero.py` check 1 (incl. mismatched row). (~30 min)
- [✅] C6. **Theorem 1(ii)**: write out Bernstein for the ±1/0 variable with Var ≤ σ²;
      confirm the error bound exp(−Ω(k·min(δ,Δ)²/σ²)) and where δ ≤ σ²/2 is used. (~45 min.
      Have the Bernstein statement you'd quote to a referee.)
- [✅] C7. **Theorem 1(i)**: (a) per-flipped-cell H² = (2θᵢ/N)(1−√(1−4εᵢ²)); prove
      2ε² ≤ 1−√(1−4ε²) ≤ 4ε² for ε∈[0,½] (two-line calculus); (b) tensorization
      H²_k ≤ k·H²_per and TV ≤ √2·H; (c) chain through Lemma 1. Cross-check
      `verify_budget_stakes_hetero.py` check 3's [4,8] bounds. (~1.5 h)
- [✅] C8. **Sharpness remark**: verify the Cauchy–Schwarz step g² ≤ (4/N²)(Σ_Wθ)(Σ_Wθε²)
      and when the two sides of the law meet. (~30 min)
- [✅] C9. **Corollary**: g* = σ/√n = √(2(1−ρ_base)/n); plug benchmark numbers → ≈0.003. (~10 min)
- [✅] C10. **The refutation (§7.7)**: reread `docs/T1_WITNESS_GAP.md` Lemmas G1–G2 and
      re-explain in your own words why the tolerant-testing witness pair cannot exist
      (stakes gap ⟹ statistic-mean gap ⟹ γ_k→1), and why Lemma B.4's tester was
      promise-restricted. Confirm the quoted numbers: η_c+η_r ≈0.007 at k=200 flat to
      n=320,000; plug-in ℓ̂₁ 1.908 vs 1.913. (~45 min)
- [✅] C11. **§5.4 rule internals**: explain the Jensen bias (why naive plug-in rejects
      perfect advice), why the bootstrap anchors at p̂ not q, and what the early exit
      tests. Reread `algorithms/test_and_match.py::directional_test_and_match`. (~45 min)
- [ ] C12. **Appendix B read-through** (added 2026-08-13, after C1–C11 were signed off).
      The proof of Theorem 1(i) was typeset into Appendix B from the §7.5 sketch plus
      `T1_HETERO_GENERAL.md` fact 3; the mathematics is what you already verified in C7,
      so this is a *fidelity* check, not a re-derivation: read the appendix against your
      C7 notes and confirm every step is the one you checked, that the Hellinger
      convention is used consistently (H² = Σ(√p−√q)², so TV ≤ √(k·H²_per)), and that
      the o(1) is the one Lemma 1 needs. Anything you would phrase differently, rephrase
      — it goes out under your name. (~30 min)

## D. Citation & related-work integrity (~2 h)

- [✅] D1. **CJKL formula**: check the tolerant-testing complexity quoted in §7.7/§2.5
      against arXiv:2106.13414's statement (constants, regimes, tolerant vs non-tolerant).
- [✅] D2. **Choo Thm 3.1**: confirm "no algorithm 1-consistent and >½-robust, adversarial
      arrivals" matches arXiv:2405.09784.
- [✅] D3. **The six new positioning citations** (gupta2017pac, balcan2020datadriven,
      wald1947sequential, bhattacharyya2025product, antoniadis2025switching,
      cui2026skirental): open each once; confirm our one-line characterizations are fair.
- [x] D4. ~~Placeholder author lists in references.bib~~ **DONE 2026-07-29**: all seven
      flagged entries fixed against arXiv/publisher pages — choo2024imperfect (was
      "Gupta"→Gouleakis; +Ling, +Bhattacharyya), bem2026testmatch (Burathep, Kunanon;
      Moses Jr.; SOFSEM 2026), mooncake2024 (Qin et al., 7 authors), preble2024
      (Srivatsa et al., 5), sageserve2025 (Jaiswal et al., 12; now POMACS 9(3) 2025),
      yoshinaga2026accuracy (Toru Yoshinaga), jailletlu2014online (MOR 39(3):624–646),
      borodin2018experimental (upgraded to ACM JEA vol 25, 2020 — the target track's
      predecessor journal). Zero TODO/placeholder fields remain; all four PDFs rebuilt,
      citations resolved. Residual for you: spot-check the rendered bibliography (D5).
- [✅] D5. Skim the rendered bibliography in talg_main.pdf for mangled entries.

## E. Prose ownership + policy (~½ day)

- [✅] E1. Read the full PDF start to finish. For every interpretive sentence (the F1–F4
      framings, "robustness insurance", "test the payoff, not the prediction", §7.8 scope,
      §10 conclusions): if you would phrase it differently, **rephrase it** — edit the
      markdown, not the tex. The advisor's concern is answered by this step: after it,
      every interpretation is yours.
- [✅] E2. Abstract vs body: every abstract claim has a section that proves/measures it.
- [✅] E3. Figure references: text "Figure N" matches the rendered Fig. N for all 10.
- [✅] E4. talg_main.tex TODOs: registered name spelling, university e-mail, CCS concepts.
- [✅] E5. **LLM-disclosure policy**: check arXiv's and ACM/TALG's current policy on
      AI-assisted writing and add the appropriate disclosure/acknowledgement. (Honesty
      requirement, and the advisor's e-mail makes it doubly important.)
- [✅] E6. Decide the artifact link (TALG requires a repository; if the repo stays private
      until acceptance, prepare an anonymized or release snapshot).

## Sign-off

- [✅] All boxes above ticked, discrepancies resolved and rebuilt.
- [✅] You can state, without notes: the law, both proofs' one-line ideas, the refutation
      story, and the three positioning answers (test-before-trust / algorithm selection /
      Wald).
→ Then: arXiv (any format), then TALG Empirical Track submission.
