// MSc defence deck — generated. Rebuild: npm install pptxgenjs && node build_deck.js
// Speaker notes live in notes.json (timed to 15 min); this file defines layout only.
const pptxgen = require("pptxgenjs");
const NOTES = require("./notes.json");
const R = "/Users/lizhuolun/Desktop/TB-3/matching-experiments/results/";

const INK = "1F2933";      // dark ground for title / evaluation / closing
const TEXT = "2B3440";     // body on light
const MUTED = "6B7280";
const PAPER = "FFFFFF";
const TINT = "F1F3F5";     // card fill on light
const TINT_D = "2E3A46";   // card fill on dark
const ON_DARK = "DDE4EA";  // body text on dark — never use TEXT on a dark ground
const CRASH = "C1440E";    // the downside / the wall
const SAFE = "2F6F6B";     // the robust side
const AMBER = "C8A24B";
const PALE = "CBD5DC";

const HF = "Cambria";
const BF = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";           // 13.3 x 7.5
pres.author = "Zhuolun Li";
pres.title = "The Limits of Predictions for Online Bipartite Matching";

const W = 13.3, M = 0.7;
const CW = W - 2 * M;                  // content width 11.9
let N = 0;                             // slide counter -> notes index

// ---------- helpers ----------
function darkSlide() {
  const s = pres.addSlide();
  s.background = { color: INK };
  s.addNotes(NOTES[N++]);
  return s;
}
function lightSlide(title, kicker) {
  const s = pres.addSlide();
  s.background = { color: PAPER };
  s.addNotes(NOTES[N++]);
  s.addText(kicker.toUpperCase(), {
    x: M, y: 0.42, w: 10, h: 0.28, fontFace: BF, fontSize: 11, bold: true,
    color: MUTED, charSpacing: 2, margin: 0,
  });
  s.addText(title, {
    x: M, y: 0.72, w: CW, h: 0.8,
    fontFace: HF, fontSize: 32, bold: true, color: TEXT, margin: 0, valign: "top",
  });
  return s;
}
function badge(s, x, y, label, fill, d) {
  const sz = d || 0.42;
  s.addShape(pres.ShapeType.ellipse, { x, y, w: sz, h: sz, fill: { color: fill || SAFE } });
  s.addText(label, {
    x, y, w: sz, h: sz, align: "center", valign: "middle",
    fontFace: BF, fontSize: sz > 0.45 ? 15 : 13, bold: true, color: PAPER, margin: 0,
  });
}
function card(s, x, y, w, h, fill) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, fill: { color: fill || TINT }, rectRadius: 0.08,
    line: { color: fill || TINT, width: 0 },
  });
}
function stat(s, x, y, w, value, label, color, size) {
  s.addText(value, {
    x, y, w, h: 0.78, fontFace: HF, fontSize: size || 42, bold: true,
    color: color || TEXT, margin: 0,
  });
  s.addText(label, {
    x, y: y + 0.76, w, h: 0.62, fontFace: BF, fontSize: 12, color: MUTED, margin: 0,
  });
}
function bullets(s, x, y, w, h, items, size, color) {
  s.addText(
    items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i !== items.length - 1 } })),
    { x, y, w, h, fontFace: BF, fontSize: size || 15, color: color || TEXT,
      margin: 0, paraSpaceAfter: 8, valign: "top" }
  );
}
function fig(s, path, ar, bx, by, bw, bh) {
  let w = bw, h = bw / ar;
  if (h > bh) { h = bh; w = bh * ar; }
  s.addImage({ path, x: bx + (bw - w) / 2, y: by + (bh - h) / 2, w, h });
}
function edge(s, x1, y1, x2, y2, color, dash) {
  s.addShape(pres.ShapeType.line, {
    x: Math.min(x1, x2), y: Math.min(y1, y2),
    w: Math.abs(x2 - x1), h: Math.abs(y2 - y1),
    flipV: y2 < y1,
    line: { color, width: dash ? 1.25 : 2, dashType: dash ? "dash" : "solid" },
  });
}

// =====================================================================
// 1. Title
// =====================================================================
{
  const s = darkSlide();
  s.addText("The Limits of Predictions for", {
    x: M, y: 1.75, w: 8.2, h: 0.72, fontFace: HF, fontSize: 40, color: PAPER, margin: 0,
  });
  s.addText("Online Bipartite Matching", {
    x: M, y: 2.45, w: 8.2, h: 0.8, fontFace: HF, fontSize: 40, bold: true, color: PAPER, margin: 0,
  });
  s.addText("A Unified Experimental Study", {
    x: M, y: 3.35, w: 8.2, h: 0.5, fontFace: BF, fontSize: 20, color: PALE, margin: 0,
  });
  s.addText("Zhuolun Li", {
    x: M, y: 4.35, w: 6, h: 0.4, fontFace: BF, fontSize: 17, bold: true, color: PAPER, margin: 0,
  });
  s.addText("MSc in Computer Science  ·  School of Computer Science  ·  University of Bristol", {
    x: M, y: 4.78, w: 8.2, h: 0.4, fontFace: BF, fontSize: 13, color: ON_DARK, margin: 0,
  });
  s.addText("Predictions are robustness insurance, not a performance lever.", {
    x: M, y: 5.55, w: 8.2, h: 0.5, fontFace: BF, fontSize: 15, italic: true, color: PALE, margin: 0,
  });

  // right-hand teaser: the three numbers the talk turns on
  card(s, 9.35, 1.75, 3.25, 4.3, TINT_D);
  const teaser = [
    ["0.990", "the advice-free baseline", PAPER],
    ["0.009", "left for perfect advice", SAFE],
    ["0.472", "unguarded following", CRASH],
  ];
  teaser.forEach(([v, l, c], i) => {
    const y = 2.05 + i * 1.36;
    s.addText(v, { x: 9.65, y, w: 2.7, h: 0.62, fontFace: HF, fontSize: 34, bold: true, color: c, margin: 0 });
    s.addText(l, { x: 9.65, y: y + 0.62, w: 2.7, h: 0.35, fontFace: BF, fontSize: 12, color: PALE, margin: 0 });
  });
}

// =====================================================================
// 2. The problem
// =====================================================================
{
  const s = lightSlide("Irrevocable decisions under uncertainty", "The problem");
  bullets(s, M, 1.7, 5.5, 2.3, [
    "Resources are known in advance; requests arrive one at a time.",
    "Each request must be matched to a free compatible resource, or dropped, before the rest of the input is seen.",
    "No decision can be undone.",
  ]);
  card(s, M, 4.2, 5.5, 1.15);
  s.addText("Online advertising · ride-hailing dispatch · AI-inference request routing", {
    x: M + 0.32, y: 4.35, w: 4.9, h: 0.85, fontFace: BF, fontSize: 14, italic: true,
    color: SAFE, margin: 0, valign: "middle",
  });
  s.addText("Performance = the matching produced ÷ the offline optimum on the same instance.", {
    x: M, y: 5.6, w: 5.5, h: 0.5, fontFace: BF, fontSize: 13, color: MUTED, margin: 0,
  });

  // bipartite diagram: compatibility dashed, the matching solid, one drop in red
  const rx = 7.3, qx = 10.15, y0 = 1.95, dy = 0.78, d = 0.4;
  s.addText("resources", { x: rx - 0.1, y: y0 - 0.5, w: 1.6, h: 0.3, fontFace: BF, fontSize: 11, bold: true, color: MUTED, margin: 0 });
  s.addText("requests, in arrival order", { x: qx - 0.35, y: y0 - 0.5, w: 2.6, h: 0.3, fontFace: BF, fontSize: 11, bold: true, color: MUTED, margin: 0 });
  const compat = [[0, 0], [1, 0], [1, 1], [2, 1], [1, 2], [2, 2], [1, 3]];
  compat.forEach(([r, q]) => edge(s, rx + d, y0 + r * dy + d / 2, qx, y0 + q * dy + d / 2, PALE, true));
  [[0, 0], [1, 1], [2, 2]].forEach(([r, q]) =>
    edge(s, rx + d, y0 + r * dy + d / 2, qx, y0 + q * dy + d / 2, SAFE, false));
  [0, 1, 2, 3].forEach(i => {
    if (i < 3) s.addShape(pres.ShapeType.ellipse, { x: rx, y: y0 + i * dy, w: d, h: d, fill: { color: SAFE } });
    s.addShape(pres.ShapeType.roundRect, {
      x: qx, y: y0 + i * dy, w: d, h: d, rectRadius: 0.06,
      fill: { color: i === 3 ? CRASH : TINT }, line: { color: i === 3 ? CRASH : PALE, width: 1 },
    });
    s.addText(String(i + 1), { x: qx, y: y0 + i * dy, w: d, h: d, align: "center", valign: "middle",
      fontFace: BF, fontSize: 11, bold: true, color: i === 3 ? PAPER : MUTED, margin: 0 });
  });
  s.addText("request 4's only compatible\nresource was already taken", {
    x: qx + 0.55, y: y0 + 3 * dy - 0.24, w: 2.0, h: 0.9, fontFace: BF, fontSize: 11,
    color: CRASH, margin: 0, valign: "middle",
  });
  s.addText("dashed = compatible   ·   solid = matched", {
    x: rx, y: y0 + 3 * dy + 0.62, w: 5.3, h: 0.3, fontFace: BF, fontSize: 11, italic: true, color: MUTED, margin: 0,
  });
}

// =====================================================================
// 3. Two guarantees, two families
// =====================================================================
{
  const s = lightSlide("Two guarantees, two families of algorithm", "Background");
  card(s, M, 1.7, 5.75, 1.35);
  s.addText("Consistency", { x: M + 0.32, y: 1.85, w: 2.6, h: 0.4, fontFace: HF, fontSize: 18, bold: true, color: SAFE, margin: 0 });
  s.addText("near-optimal when the prediction is good", { x: M + 0.32, y: 2.28, w: 5.1, h: 0.6, fontFace: BF, fontSize: 14, color: TEXT, margin: 0 });
  card(s, W - M - 5.75, 1.7, 5.75, 1.35);
  s.addText("Robustness", { x: W - M - 5.43, y: 1.85, w: 2.6, h: 0.4, fontFace: HF, fontSize: 18, bold: true, color: CRASH, margin: 0 });
  s.addText("no worse than a prediction-free algorithm when it is wrong", { x: W - M - 5.43, y: 2.28, w: 5.1, h: 0.6, fontFace: BF, fontSize: 14, color: TEXT, margin: 0 });

  const fam = [
    ["1", "MinPredictedDegree",
      "consumes a prediction of how contended each resource will be, and serves the scarcest first",
      "prediction: one number per resource"],
    ["2", "Test-and-fallback",
      "tests a prediction of the arrival mix on a short prefix of the requests, then commits to following it or falling back",
      "prediction: a histogram over request types"],
  ];
  fam.forEach(([n, h, d, sub], i) => {
    const x = i === 0 ? M : W - M - 5.75;
    card(s, x, 3.4, 5.75, 2.35);
    badge(s, x + 0.32, 3.63, n, SAFE, 0.5);
    s.addText(h, { x: x + 1.0, y: 3.64, w: 4.5, h: 0.45, fontFace: HF, fontSize: 18, bold: true, color: TEXT, margin: 0 });
    s.addText(d, { x: x + 0.32, y: 4.32, w: 5.1, h: 0.85, fontFace: BF, fontSize: 14, color: TEXT, margin: 0 });
    s.addText(sub, { x: x + 0.32, y: 5.25, w: 5.1, h: 0.35, fontFace: BF, fontSize: 12, italic: true, color: MUTED, margin: 0 });
  });

  s.addText("Both were analysed only in isolation — each on its own inputs, its own notion of prediction error, and almost entirely in worst-case theory.", {
    x: M, y: 6.1, w: CW, h: 0.6, fontFace: BF, fontSize: 15, bold: true, color: TEXT, margin: 0,
  });
}

// =====================================================================
// 4. Research questions
// =====================================================================
{
  const s = lightSlide("Three questions", "Aims and objectives");
  const qs = [
    ["1", "How do the two families actually compare, head to head, under one prediction-error model — and how much does a prediction buy on realistic data?", "answered experimentally", SAFE],
    ["2", "What are the failure modes of the adaptive test-and-fallback mechanism: the cost of its test, and the calibration of its accept/reject decision?", "answered experimentally", SAFE],
    ["3", "Why does the average-case experience differ so sharply from the worst-case promise — is the wall an artefact, or is it necessary?", "answered in outlook form", CRASH],
  ];
  qs.forEach(([tag, text, how, c], i) => {
    const y = 1.75 + i * 1.72;
    card(s, M, y, CW, 1.5);
    badge(s, M + 0.35, y + 0.5, tag, c, 0.5);
    s.addText(text, {
      x: M + 1.15, y: y + 0.2, w: CW - 3.4, h: 1.1, fontFace: BF, fontSize: 15, color: TEXT, margin: 0, valign: "middle",
    });
    s.addText(how, {
      x: W - M - 2.3, y: y + 0.2, w: 1.95, h: 1.1, fontFace: BF, fontSize: 12, italic: true,
      color: c === CRASH ? CRASH : MUTED, align: "right", valign: "middle", margin: 0,
    });
  });
  s.addText("The first two are answered experimentally; the third in outlook form, and I say exactly how far that goes.", {
    x: M, y: 6.75, w: CW, h: 0.4, fontFace: BF, fontSize: 12.5, italic: true, color: MUTED, margin: 0,
  });
}

// =====================================================================
// 5. Method
// =====================================================================
{
  const s = lightSlide("One harness: only the prediction varies", "Method");
  const items = [
    ["Same instances", "identical graphs, arrival sequences, offline optimum (Hopcroft–Karp) and paired random streams for every algorithm"],
    ["Structured error", "four error models injected along the structure of the instance, not as i.i.d. noise"],
    ["Stated uncertainty", "paired trials, 95% confidence intervals on every reported ratio"],
    ["Reproducible", "every figure and table regenerated from a fixed seed by one script"],
  ];
  items.forEach(([h, d], i) => {
    const y = 1.75 + i * 1.18;
    badge(s, M, y, String(i + 1));
    s.addText(h, { x: M + 0.6, y: y - 0.03, w: 3.0, h: 0.36, fontFace: HF, fontSize: 16, bold: true, color: TEXT, margin: 0 });
    s.addText(d, { x: M + 0.6, y: y + 0.34, w: 6.6, h: 0.75, fontFace: BF, fontSize: 13, color: MUTED, margin: 0 });
  });

  card(s, 8.35, 1.75, W - M - 8.35, 4.6, TINT);
  s.addText("Validated before use", {
    x: 8.68, y: 1.98, w: 3.6, h: 0.4, fontFace: HF, fontSize: 18, bold: true, color: TEXT, margin: 0,
  });
  s.addText("I reproduced the published experimental study of Borodin, Karavasilis and Pankratov before adding any prediction-based work.", {
    x: 8.68, y: 2.45, w: 3.6, h: 1.2, fontFace: BF, fontSize: 13.5, color: TEXT, margin: 0,
  });
  s.addText("5 / 5", { x: 8.68, y: 3.75, w: 3.6, h: 0.8, fontFace: HF, fontSize: 42, bold: true, color: SAFE, margin: 0 });
  s.addText("qualitative claims reproduced, all within an absolute difference of 0.02 — despite a different language and a different max-flow routine.", {
    x: 8.68, y: 4.6, w: 3.6, h: 1.5, fontFace: BF, fontSize: 12.5, color: MUTED, margin: 0,
  });

  s.addText("Run on synthetic families, six real-world graphs, and real request traces (Wikipedia, Azure, Mooncake).", {
    x: M, y: 6.6, w: CW, h: 0.5, fontFace: BF, fontSize: 14, italic: true, color: SAFE, margin: 0,
  });
}

// =====================================================================
// 6. Finding 1 — the benchmark
// =====================================================================
{
  const s = lightSlide("Every wide gap is a downside gap", "Finding 1  ·  the unified benchmark");
  s.addText("Consistency–robustness plane: up and to the right is better, and the star marks the advice-free floor.", {
    x: M, y: 1.5, w: CW, h: 0.32, fontFace: BF, fontSize: 12.5, italic: true, color: MUTED, margin: 0,
  });
  fig(s, R + "consistency_robustness.png", 3.39, M, 1.85, CW, 3.51);
  const cells = [
    ["0.990", "advice-free Ranking\nalready reaches", TEXT],
    ["0.009", "total headroom left\nfor perfect advice", SAFE],
    ["0.472", "unguarded prediction-\nfollowing collapses to", CRASH],
    ["0.990", "the guarded algorithm\nholds, whatever the advice", SAFE],
  ];
  cells.forEach(([v, l, c], i) => {
    stat(s, M + i * (CW / 4), 5.55, 2.8, v, l, c, 38);
  });
}

// =====================================================================
// 7. Finding 2 — order error
// =====================================================================
{
  const s = lightSlide("What governs the loss is order, not magnitude", "Finding 2  ·  the residual loss");
  fig(s, R + "order_vs_theory.png", 2.19, M, 1.65, 7.5, 3.45);
  s.addText("(a) realised loss against the known bound   ·   (b) the same loss against Kendall-τ", {
    x: M, y: 5.2, w: 7.5, h: 0.35, fontFace: BF, fontSize: 12, italic: true, color: MUTED, margin: 0,
  });
  card(s, 8.5, 1.65, W - M - 8.5, 3.9);
  bullets(s, 8.8, 1.95, 3.5, 3.4, [
    "All four error models collapse onto one Kendall-τ curve (Spearman ρ = 0.979).",
    "A monotone rescaling of the predictor changes nothing at all.",
    "The known n − LIS bound is loose by 16–75× and saturates — it cannot tell a harmful prediction from a harmless one.",
  ], 13);
  card(s, M, 5.85, CW, 0.95, TINT);
  s.addText([
    { text: "Attribution:  ", options: { bold: true } },
    { text: "order-dependence itself is Aamand–Chen–Indyk's theorem. Mine is the characterisation — which order measure governs the loss, and how loose the known bound is.", options: {} },
  ], { x: M + 0.32, y: 5.95, w: CW - 0.64, h: 0.75, fontFace: BF, fontSize: 14, color: TEXT, margin: 0, valign: "middle" });
}

// =====================================================================
// 8. Finding 3 — test-and-fallback
// =====================================================================
{
  const s = lightSlide("A more accurate test can make a worse decision", "Finding 3  ·  test-and-fallback");
  bullets(s, M, 1.65, 4.5, 2.1, [
    "The worst-case-calibrated threshold is far too lenient on average-case inputs.",
    "So a larger, more accurate prefix test decides worse than a small, noisy one.",
    "Recalibration removes the pathology and exposes what is underneath.",
  ], 13.5);
  card(s, M, 4.0, 4.5, 2.7);
  s.addText("The resolution limit", { x: M + 0.3, y: 4.2, w: 3.9, h: 0.4, fontFace: HF, fontSize: 17, bold: true, color: CRASH, margin: 0 });
  s.addText("No practical acceptance threshold can capture an upside smaller than its own estimator's noise — and this holds across the whole difficulty range, not just at one setting.", {
    x: M + 0.3, y: 4.65, w: 3.9, h: 1.9, fontFace: BF, fontSize: 13.5, color: TEXT, margin: 0,
  });
  fig(s, R + "impossibility_frontier.png", 2.53, 5.55, 1.9, 7.05, 2.79);
  s.addText("Potential upside grows as the baseline weakens; the upside a sublinear test can safely capture stays near zero. The curves separate rather than converge.", {
    x: 5.75, y: 5.05, w: 6.7, h: 0.8, fontFace: BF, fontSize: 12.5, italic: true, color: MUTED, margin: 0,
  });
}

// =====================================================================
// 9. External validity
// =====================================================================
{
  const s = lightSlide("It survives real predictors and real graphs", "External validity");
  fig(s, R + "real_predictor.png", 2.61, M, 1.6, 7.0, 2.7);
  s.addText("A cheap, non-ML predictor: last-window Wikipedia pageview counts, so the error is genuine temporal drift.", {
    x: M, y: 4.4, w: 7.0, h: 0.4, fontFace: BF, fontSize: 12, italic: true, color: MUTED, margin: 0,
  });
  s.addText("Why it works: aggregating the forecast onto the topology halves its order error — and order is all the algorithm consumes.", {
    x: M, y: 4.95, w: 7.0, h: 0.75, fontFace: BF, fontSize: 14, color: TEXT, margin: 0,
  });
  card(s, M, 5.85, 7.0, 0.9, TINT);
  s.addText("The same forecast, consumed without a guard, collapses to 0.36 — far below the 0.92 baseline.", {
    x: M + 0.3, y: 5.95, w: 6.4, h: 0.7, fontFace: BF, fontSize: 14, bold: true, color: CRASH, margin: 0, valign: "middle",
  });
  const rows = [
    ["27–68%", "of the available gap captured by a linear-time count", SAFE],
    ["0.11 ms", "to compute, against 4.4 ms for the optimum itself", TEXT],
    ["6 / 6", "real-world graphs on which the crash finding still holds", CRASH],
  ];
  rows.forEach(([v, l, c], i) => {
    const y = 1.6 + i * 1.75;
    card(s, 8.2, y, W - M - 8.2, 1.5);
    s.addText(v, { x: 8.5, y: y + 0.2, w: 3.5, h: 0.6, fontFace: HF, fontSize: 28, bold: true, color: c, margin: 0 });
    s.addText(l, { x: 8.5, y: y + 0.82, w: 3.5, h: 0.55, fontFace: BF, fontSize: 12.5, color: MUTED, margin: 0 });
  });
}

// =====================================================================
// 10. Negative results
// =====================================================================
{
  const s = lightSlide("Two attempts to get past the wall", "Negative results");
  s.addText("Reported as results, not omitted.", {
    x: M, y: 1.55, w: 6, h: 0.32, fontFace: BF, fontSize: 13, italic: true, color: MUTED, margin: 0,
  });
  const steps = [
    ["M0", "The mechanism is real: with engineered features, training the predictor for order beats training it for accuracy — 0.989 vs 0.974 — while fitting the truth worse.", SAFE],
    ["M1", "But the advantage is doubly gated, and peaks at +1.3% of the ratio.", AMBER],
    ["M3", "And on genuine temporal features from a real trace it vanishes: identical order (τ = 0.126 both), identical matching.", CRASH],
  ];
  steps.forEach(([tag, text, c], i) => {
    const y = 2.05 + i * 1.5;
    card(s, M, y, 6.0, 1.3);
    s.addShape(pres.ShapeType.roundRect, { x: M + 0.28, y: y + 0.42, w: 0.62, h: 0.46, rectRadius: 0.08, fill: { color: c } });
    s.addText(tag, { x: M + 0.28, y: y + 0.42, w: 0.62, h: 0.46, align: "center", valign: "middle", fontFace: BF, fontSize: 13, bold: true, color: PAPER, margin: 0 });
    s.addText(text, { x: M + 1.1, y: y + 0.15, w: 4.6, h: 1.0, fontFace: BF, fontSize: 12.5, color: TEXT, margin: 0, valign: "middle" });
  });
  fig(s, R + "rank_real_trace.png", 2.62, 7.15, 1.95, 5.45, 2.1);
  s.addText("M3: rank- and MSE-trained predictors are indistinguishable on real features.", {
    x: 7.15, y: 4.15, w: 5.45, h: 0.4, fontFace: BF, fontSize: 12, italic: true, color: MUTED, margin: 0,
  });
  card(s, 7.15, 4.7, 5.45, 1.85, TINT);
  s.addText("Second attempt: a tail objective", {
    x: 7.45, y: 4.9, w: 4.9, h: 0.35, fontFace: HF, fontSize: 16, bold: true, color: TEXT, margin: 0,
  });
  s.addText("If throughput is too forgiving, try latency. Under bursty load the best non-predictive policy comes within 3% of a policy that knows the future exactly.", {
    x: 7.45, y: 5.32, w: 4.9, h: 1.1, fontFace: BF, fontSize: 13, color: TEXT, margin: 0,
  });
}

// =====================================================================
// 11. Theory outlook
// =====================================================================
{
  const s = lightSlide("Why the wall should be expected", "Theory  ·  outlook");
  card(s, M, 1.6, CW, 1.75, TINT);
  s.addText("Every test-and-fallback algorithm, deciding by any measurable rule on its prefix, satisfies", {
    x: M + 0.32, y: 1.75, w: CW - 0.64, h: 0.35, fontFace: BF, fontSize: 13, color: MUTED, margin: 0, align: "center",
  });
  s.addText([
    { text: "(1 − η", options: {} }, { text: "c", options: { subscript: true } },
    { text: ")   ≤   η", options: {} }, { text: "r", options: { subscript: true } },
    { text: "  +  γ", options: {} }, { text: "k", options: { subscript: true } },
    { text: "  +  o(1)", options: {} },
  ], { x: M + 0.32, y: 2.15, w: CW - 0.64, h: 0.62, fontFace: HF, fontSize: 28, bold: true, color: TEXT, margin: 0, align: "center" });
  s.addText("forgone upside   ≤   robustness loss   +   how far apart the two prefix distributions are", {
    x: M + 0.32, y: 2.83, w: CW - 0.64, h: 0.35, fontFace: BF, fontSize: 12.5, italic: true, color: MUTED, margin: 0, align: "center",
  });

  bullets(s, M, 3.65, 6.4, 2.3, [
    "“Consistent and robust” becomes a question of sample complexity: how long a prefix is needed to tell good advice from bad?",
    "The stakes are capped by the baseline's slack — so on strong-baseline instances the required prefix exceeds the whole instance.",
  ], 14);

  card(s, 7.6, 3.65, W - M - 7.6, 2.3);
  s.addText("≈ 0.004", { x: 7.9, y: 3.85, w: 4.4, h: 0.8, fontFace: HF, fontSize: 40, bold: true, color: CRASH, margin: 0 });
  s.addText("the upside the reading says no rule can capture at the benchmark's parameters — exactly the order of the upsides I measured.", {
    x: 7.9, y: 4.65, w: 4.4, h: 1.15, fontFace: BF, fontSize: 12.5, color: TEXT, margin: 0,
  });

  card(s, M, 6.2, CW, 0.85, TINT);
  s.addText("Scope: only the inequality above is proved here. The budget law behind the number, and whether it extends past decomposable families, is not established in this thesis.", {
    x: M + 0.32, y: 6.3, w: CW - 0.64, h: 0.65, fontFace: BF, fontSize: 13, italic: true, color: TEXT, margin: 0, valign: "middle",
  });
}

// =====================================================================
// 12. Critical evaluation
// =====================================================================
{
  const s = darkSlide();
  s.addText("EVALUATION", { x: M, y: 0.5, w: 8, h: 0.3, fontFace: BF, fontSize: 11, bold: true, color: PALE, charSpacing: 2, margin: 0 });
  s.addText("What the project achieved, and what it did not", {
    x: M, y: 0.85, w: CW, h: 0.7, fontFace: HF, fontSize: 30, bold: true, color: PAPER, margin: 0,
  });
  const evals = [
    ["1", "Q1 — met in full", "the benchmark answers it numerically, and it survives real predictors and real graphs", SAFE],
    ["2", "Q2 — met, with one qualification", "the test measured is the surrogate the original authors specify, not an implemented tolerant tester", AMBER],
    ["3", "Q3 — bracketed, not closed", "one proved inequality and a quantitative reading, not a theorem that the wall is forced", CRASH],
  ];
  evals.forEach(([tag, verdict, why, c], i) => {
    const y = 1.85 + i * 1.62;
    card(s, M, y, 6.1, 1.4, TINT_D);
    badge(s, M + 0.3, y + 0.45, tag, c, 0.5);
    s.addText(verdict, { x: M + 1.0, y: y + 0.18, w: 4.9, h: 0.35, fontFace: HF, fontSize: 16, bold: true, color: PAPER, margin: 0 });
    s.addText(why, { x: M + 1.0, y: y + 0.58, w: 4.9, h: 0.7, fontFace: BF, fontSize: 12, color: ON_DARK, margin: 0 });
  });

  s.addText("With hindsight", { x: 7.5, y: 1.85, w: 5, h: 0.4, fontFace: HF, fontSize: 20, bold: true, color: PAPER, margin: 0 });
  const hind = [
    ["Right", "structured error models — i.i.d. noise would have hidden the order effect entirely", SAFE],
    ["Debatable", "known-i.i.d. is the model where the baseline is strongest, so the choice partly pre-selected the headline", AMBER],
    ["Debatable", "measuring only matching size — a second objective should have run through the whole benchmark", AMBER],
    ["Process", "I ran the synthetic stages before the real-feature test; the cheaper, decisive experiment should have come first", PALE],
  ];
  hind.forEach(([tag, text, c], i) => {
    const y = 2.45 + i * 1.1;
    s.addText([
      { text: tag + "  ", options: { bold: true, color: c } },
      { text: text, options: { color: ON_DARK } },
    ], { x: 7.5, y, w: 5.1, h: 0.95, fontFace: BF, fontSize: 12.5, margin: 0, valign: "top" });
  });
}

// =====================================================================
// 13. Conclusion
// =====================================================================
{
  const s = darkSlide();
  s.addText("CONCLUSION", { x: M, y: 0.65, w: 8, h: 0.3, fontFace: BF, fontSize: 11, bold: true, color: PALE, charSpacing: 2, margin: 0 });
  s.addText("Where predictions cannot help", {
    x: M, y: 1.05, w: CW, h: 0.8, fontFace: HF, fontSize: 34, bold: true, color: PAPER, margin: 0,
  });
  const three = [
    ["A cheap, order-faithful predictor", "already captures nearly all there is to capture."],
    ["The sophisticated machinery", "earns its keep as insurance, not as performance."],
    ["Finding out whether to trust a prediction", "costs more, on these inputs, than the prediction is worth."],
  ];
  three.forEach(([a, b], i) => {
    const y = 2.35 + i * 1.05;
    badge(s, M, y, String(i + 1), i === 2 ? CRASH : SAFE);
    s.addText([
      { text: a + "  ", options: { bold: true, color: PAPER } },
      { text: b, options: { color: ON_DARK } },
    ], { x: M + 0.62, y: y - 0.02, w: 7.4, h: 0.8, fontFace: BF, fontSize: 15, margin: 0 });
  });

  card(s, 8.6, 2.35, W - M - 8.6, 2.95, TINT_D);
  s.addText("Where to look next", { x: 8.9, y: 2.55, w: 3.5, h: 0.35, fontFace: HF, fontSize: 16, bold: true, color: PAPER, margin: 0 });
  bullets(s, 8.9, 3.0, 3.5, 2.1, [
    "Adversarial or non-stationary arrivals, where the baseline is provably far from optimal",
    "Objectives on which the baseline is not near-optimal",
    "Completing the budget–stakes law",
  ], 12, ON_DARK);

  s.addText("Recognising where predictions cannot help is, I hope, as useful as knowing where they can.", {
    x: M, y: 5.85, w: CW, h: 0.6, fontFace: HF, fontSize: 19, italic: true, color: PAPER, margin: 0,
  });
  s.addText("Thank you — happy to take questions.", {
    x: M, y: 6.55, w: 8, h: 0.4, fontFace: BF, fontSize: 14, color: PALE, margin: 0,
  });
}

// =====================================================================
// Backup slides
// =====================================================================
{
  const s = lightSlide("Backup · the four findings on six real graphs", "For questions");
  fig(s, R + "realworld_robustness.png", 1.78, M, 1.6, 6.6, 4.5);
  const f = [
    ["F1", "naive following falls below the advice-free floor on all six, by 0.06 to 0.10", CRASH],
    ["F2", "structural robustness holds qualitatively on all six; strictly on the four social and biological graphs", SAFE],
    ["F3", "the consistency upside is small everywhere (mean +0.049) and smallest exactly where the baseline is strongest", SAFE],
    ["F4", "the augmentation rescues the worst-case-designed algorithms: 0.73–0.77 lifted to 0.99", SAFE],
  ];
  f.forEach(([tag, text, c], i) => {
    const y = 1.7 + i * 1.25;
    s.addText(tag, { x: 7.6, y, w: 0.75, h: 0.35, fontFace: HF, fontSize: 16, bold: true, color: c, margin: 0 });
    s.addText(text, { x: 8.4, y: y - 0.02, w: 4.2, h: 1.1, fontFace: BF, fontSize: 12.5, color: TEXT, margin: 0 });
  });
}
{
  const s = lightSlide("Backup · limitations, stated plainly", "For questions");
  const lims = [
    ["Input model", "Known-i.i.d. throughout. The wall is an average-case statement; I do not claim it for adversarial arrival order."],
    ["Test model", "An empirical ℓ1 surrogate for the unimplemented tolerant tester, following the original authors."],
    ["Objective", "Matching size only. On tail latency, fairness or recompute cost the picture could differ."],
    ["Data breadth", "Each real modality is exercised by one trace."],
    ["Theory scope", "One proved inequality plus a quantitative reading. No theorem beyond that is claimed."],
  ];
  lims.forEach(([h, d], i) => {
    const y = 1.7 + i * 1.02;
    card(s, M, y, CW, 0.88);
    s.addText(h, { x: M + 0.32, y: y + 0.16, w: 2.4, h: 0.55, fontFace: HF, fontSize: 15, bold: true, color: TEXT, margin: 0, valign: "middle" });
    s.addText(d, { x: M + 3.0, y: y + 0.1, w: CW - 3.4, h: 0.68, fontFace: BF, fontSize: 13, color: MUTED, margin: 0, valign: "middle" });
  });
  s.addText("Scale: 16 figures, all regenerated from a fixed seed by a single script; reproduction guide in Appendix A.", {
    x: M, y: 6.75, w: CW, h: 0.4, fontFace: BF, fontSize: 12, italic: true, color: MUTED, margin: 0,
  });
}

pres.writeFile({ fileName: "/Users/lizhuolun/Desktop/TB-3/matching-experiments/thesis/defence/defence.pptx" })
  .then(f => console.log("wrote", f));
