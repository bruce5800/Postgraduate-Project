#!/bin/bash
# Build the CHINESE thesis PDF from ../zh/*.md via pandoc + xelatex (ctexrep class).
# Chinese chapter/section headings are written WITHOUT numbers in the md; ctexrep
# auto-numbers them ("第 X 章"). Figure paths and math are identical to the English build.
# Builds whatever zh/ chapters exist, so translation can proceed incrementally.
set -e
cd "$(dirname "$0")"

CHAPTERS="01_introduction 02_background 03_model_methodology 04_unified_benchmark \
05_order_error 06_test_and_fallback 07_external_validity 08_exploratory_negatives \
09_theory 10_serving_case_study 11_conclusion"

tmp="$(mktemp -t thesiszhXXXX).md"
preprocess() {
  # strip single-line <!-- ... --> comments first, then any multi-line comment blocks
  sed -e 's/<!--.*-->//g' -e '/<!--/,/-->/d' "$1" \
    | sed -e 's/≈/$\\approx$/g' -e 's/✓/$\\checkmark$/g'
}

included=""
for c in $CHAPTERS; do
  if [ -f "../zh/$c.md" ]; then
    preprocess "../zh/$c.md" >> "$tmp"; printf '\n\n' >> "$tmp"; included="$included $c"
  fi
done
# References chapter (citeproc fills the #refs div; unnumbered, placed before the appendix):
printf '\n\n# 参考文献 {.unnumbered}\n\n::: {#refs}\n:::\n\n' >> "$tmp"
if [ -f "../zh/A_reproduction.md" ]; then
  printf '\n\n```{=latex}\n\\appendix\n```\n\n' >> "$tmp"
  preprocess "../zh/A_reproduction.md" >> "$tmp"; included="$included A"
fi
echo "chapters included:$included"

pandoc "$tmp" --metadata-file=meta_zh.yaml -H header.tex \
  --top-level-division=chapter --toc --toc-depth=1 \
  --citeproc --csl=numeric.csl --bibliography=../../docs/references.bib \
  --pdf-engine=xelatex -o main_zh.pdf > build_zh.log 2>&1 || {
    echo "FAILED — tail of build_zh.log:"; tail -30 build_zh.log; rm -f "$tmp"; exit 1; }
rm -f "$tmp"
pages=$(pdfinfo main_zh.pdf 2>/dev/null | awk "/Pages/{print $2}")
echo "OK: built main_zh.pdf (${pages:-?} pages)"
