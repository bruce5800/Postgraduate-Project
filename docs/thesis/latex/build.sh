#!/bin/bash
# Build the thesis PDF from the markdown chapters. Single standalone pandoc call so
# pandoc's own (complete, correct) LaTeX preamble handles tables/fonts/math. Chapters
# stay modular as ../<chapter>.md; metadata (title/abstract/class) is in meta.yaml.
# To use the school's template later: pandoc ... --template=school_template.tex
set -e
cd "$(dirname "$0")"

CHAPTERS="01_introduction 02_background 03_model_methodology 04_unified_benchmark \
05_order_error 06_test_and_fallback 07_external_validity 08_exploratory_negatives \
09_theory 10_serving_case_study 11_conclusion"

tmp="$(mktemp -t thesisXXXX).md"
preprocess() {
  # drop HTML comment blocks; strip "Chapter N."/"Appendix A." from # headings and
  # "N.M " numeric prefixes from ##/### headings (LaTeX auto-numbers both).
  sed -e '/<!--/,/-->/d' "$1" \
    | sed -E 's/^# (Chapter [0-9]+\.|Appendix [A-Z]\.) /# /' \
    | sed -E 's/^(#{2,3}) [0-9]+(\.[0-9]+)* /\1 /' \
    | sed -e 's/≈/$\\approx$/g' -e 's/✓/$\\checkmark$/g'
}

for c in $CHAPTERS; do preprocess "../$c.md" >> "$tmp"; printf '\n\n' >> "$tmp"; done
printf '\n\n```{=latex}\n\\appendix\n```\n\n' >> "$tmp"
preprocess "../A_reproduction.md" >> "$tmp"

pandoc "$tmp" --metadata-file=meta.yaml -H header.tex \
  --top-level-division=chapter --toc --toc-depth=1 \
  --pdf-engine=xelatex -o main.pdf > build.log 2>&1 || {
    echo "pandoc/pdflatex FAILED — tail of build.log:"; tail -30 build.log; rm -f "$tmp"; exit 1; }
rm -f "$tmp"
pages=$(pdfinfo main.pdf 2>/dev/null | awk '/Pages/{print $2}')
echo "OK: built main.pdf (${pages:-?} pages)"
